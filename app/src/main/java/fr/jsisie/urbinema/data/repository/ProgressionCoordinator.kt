package fr.jsisie.urbinema.data.repository

import android.util.Log
import androidx.room.withTransaction
import fr.jsisie.urbinema.data.db.ActivityEventEntity
import fr.jsisie.urbinema.data.db.CatalogDimensionStatEntity
import fr.jsisie.urbinema.data.db.UserBadgeCrossRef
import fr.jsisie.urbinema.data.db.UserProgressStateEntity
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.db.XpSources
import fr.jsisie.urbinema.data.db.XpTransactionEntity
import fr.jsisie.urbinema.domain.badge.BadgeRegistry
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.TerritoryDimension
import fr.jsisie.urbinema.domain.model.TerritoryKey
import fr.jsisie.urbinema.domain.rank.CatalogRankStats
import fr.jsisie.urbinema.domain.rank.CatalogRankStatsEngine
import fr.jsisie.urbinema.domain.rank.RankDefaults
import fr.jsisie.urbinema.domain.rank.RankEngine
import fr.jsisie.urbinema.domain.rank.TerritoryReference
import fr.jsisie.urbinema.domain.xp.XpEngine
import java.time.Clock
import java.time.Instant

/**
 * Recalculates every durable consequence of a movie validation.
 *
 * The validated movie set remains the source of truth. Cached score state,
 * rank and newly earned badges are committed in one transaction.
 */
class ProgressionCoordinator(
    private val database: UrbinemaDatabase,
    private val rankEngine: RankEngine,
    private val statsEngine: CatalogRankStatsEngine,
    private val badgeRegistry: BadgeRegistry,
    private val xpEngine: XpEngine,
    private val clock: Clock = Clock.systemUTC(),
) {
    /**
     * Rebuilds rank, XP level and badge unlocks from the validated movie set.
     *
     * Catalog rarity stats are loaded if already stored for this pack version,
     * otherwise they are computed once and persisted. Rank display is ratcheted
     * (never decreases). New badges are inserted only; already earned ones stay.
     */
    suspend fun recalculate(userId: Long) {
        val catalogDao = database.catalogDao()
        val progressDao = database.progressDao()
        val rankDao = database.rankConfigDao()
        val catalog = catalogDao.allMoviesWithRelations().map { it.toDomain(database) }
        if (catalog.isEmpty()) return

        val version = checkNotNull(rankDao.latestCatalogVersion())
        val existingRows = rankDao.latestDimensionStats()
        val stats = if (existingRows.isNotEmpty()) {
            CatalogRankStats(
                version = version.version.toLong(),
                references = existingRows.associate {
                    TerritoryKey(
                        TerritoryDimension.valueOf(it.dimensionCode),
                        EditorialCode(it.territoryCode),
                    ) to TerritoryReference(it.rarityReference, it.weightReference)
                },
            )
        } else {
            statsEngine.build(
                version = version.version.toLong(),
                catalog = catalog,
                dimensionShares = RankDefaults.parameters.dimensionShares,
            ).also { calculated ->
                rankDao.insertDimensionStats(
                    calculated.references.map { (key, reference) ->
                        CatalogDimensionStatEntity(
                            catalogVersionId = version.catalogVersionId,
                            dimensionCode = key.dimension.name,
                            territoryCode = key.code.value,
                            rarityReference = reference.rarity,
                            weightReference = reference.weight,
                        )
                    }
                )
            }
        }

        val user = checkNotNull(progressDao.localUser())
        val currentRank = checkNotNull(catalogDao.rankingById(user.rankingId))
        val currentRankOrder = currentRank.displayOrder

        val watchedRels = progressDao.validatedMovies(userId)
        val validated = watchedRels.map { it.toDomain(database) }
        val ageYears = user.birthDate?.let { java.time.Year.now().value - it.year }
        val result = rankEngine.calculate(validated, stats, currentRankOrder, ageYears)
        val candidateRanking = checkNotNull(progressDao.rankingByOrder(result.displayedRank))
        val now = Instant.now(clock)
        Log.i(
            TAG,
            "Rang recalculé: films=${result.rawMovieCount} " +
                "Vw=${"%.4f".format(result.weightedVolume)} " +
                "D=${"%.4f".format(result.diversity)} " +
                "P=${"%.4f".format(result.depth)} " +
                "âge=${ageYears ?: "-"} A=${"%.4f".format(result.ageBonus)} " +
                "S=${"%.4f".format(result.score)} " +
                "(S = 0.6*ln(1+Vw) + 6*D + 1.2*ln(1+P) + A) " +
                "rangBrut=${result.rawRank} rangAffiché=${result.displayedRank} " +
                "code=${candidateRanking.code}",
        )

        database.withTransaction {
            if (candidateRanking.rankingId != user.rankingId) {
                progressDao.updateRanking(userId, candidateRanking.rankingId)
                progressDao.insertActivityEvent(
                    ActivityEventEntity(
                        userId = userId,
                        type = "RANK_UP",
                        occurredAt = now,
                        payloadJson = """{"version":1,"rankCode":"${candidateRanking.code}"}""",
                    )
                )
            }
            progressDao.upsertProgressState(
                UserProgressStateEntity(
                    userId = userId,
                    weightedVolume = result.weightedVolume,
                    diversity = result.diversity,
                    depth = result.depth,
                    score = result.score,
                    rawRankOrder = result.rawRank,
                    recalculatedAt = now,
                )
            )

            val earned = progressDao.earnedBadgeCodes(userId).mapTo(hashSetOf(), ::EditorialCode)
            val catalogCountries = catalog.mapTo(linkedSetOf()) { it.primaryCountry }
            badgeRegistry.newlyUnlocked(validated, earned, catalogCountries).forEach { unlock ->
                val badge = progressDao.badgeByCode(unlock.badgeCode.value) ?: return@forEach
                if (progressDao.insertUserBadge(UserBadgeCrossRef(userId, badge.badgeId, now)) != -1L) {
                    progressDao.insertActivityEvent(
                        ActivityEventEntity(
                            userId = userId,
                            type = "BADGE_EARNED",
                            occurredAt = now,
                            payloadJson = """{"version":1,"badgeCode":"${badge.code}"}""",
                        )
                    )
                }
            }

            val filmXp = xpEngine.rewardForFilm()
            if (filmXp <= 0) {
                val stripped = progressDao.deleteXpBySource(userId, XpSources.FILM)
                if (stripped > 0) {
                    val remaining = progressDao.totalXp(userId)
                    val calculated = xpEngine.progress(remaining, 1).calculatedLevel
                    progressDao.setMaxLevelReached(userId, calculated)
                    Log.i(TAG, "XP films retirée ($stripped lignes). Niveau recalé : $calculated")
                }
            } else {
                val retargeted = progressDao.updateXpAmountBySource(userId, XpSources.FILM, filmXp)
                val alreadyPaid = progressDao.filmXpMovieIds(userId).toHashSet()
                watchedRels.forEach { rel ->
                    if (rel.movie.movieId in alreadyPaid) return@forEach
                    progressDao.insertXpTransactionIgnore(
                        XpTransactionEntity(
                            userId = userId,
                            movieId = rel.movie.movieId,
                            source = XpSources.FILM,
                            amount = filmXp,
                            earnedAt = now,
                        )
                    )
                }
                if (retargeted > 0) {
                    val remaining = progressDao.totalXp(userId)
                    val calculated = xpEngine.progress(remaining, 1).calculatedLevel
                    progressDao.setMaxLevelReached(userId, calculated)
                    Log.i(TAG, "XP film recalée à $filmXp ($retargeted lignes). Niveau recalé : $calculated")
                }
            }
        }
    }

    private companion object {
        const val TAG = "UrbinemaProgress"
    }
}
