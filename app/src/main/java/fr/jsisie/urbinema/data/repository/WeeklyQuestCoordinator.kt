package fr.jsisie.urbinema.data.repository

import android.util.Log
import androidx.room.withTransaction
import fr.jsisie.urbinema.data.db.ContinentEntity
import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.data.db.QuestEntity
import fr.jsisie.urbinema.data.db.UserQuestEntity
import fr.jsisie.urbinema.data.db.UserQuestStatus
import fr.jsisie.urbinema.data.db.UserQuestWithDefinition
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieValidation
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.quest.AssignedQuest
import fr.jsisie.urbinema.domain.quest.QuestCalendar
import fr.jsisie.urbinema.domain.quest.QuestDefinition
import fr.jsisie.urbinema.domain.quest.QuestEngine
import fr.jsisie.urbinema.domain.quest.QuestRewardResult
import fr.jsisie.urbinema.domain.quest.QuestRuleRegistry
import fr.jsisie.urbinema.domain.xp.QuestDifficulty
import fr.jsisie.urbinema.domain.xp.XpEngine
import java.time.Clock
import java.time.Instant
import java.time.ZoneId
import kotlin.coroutines.cancellation.CancellationException
import kotlin.random.Random
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Assigns, progresses, expires and rewards the weekly quests. */
class WeeklyQuestCoordinator(
    private val database: UrbinemaDatabase,
    private val questEngine: QuestEngine,
    private val xpEngine: XpEngine,
    private val progressRepository: ProgressRepository,
    private val rules: QuestRuleRegistry,
    private val questCalendar: QuestCalendar = QuestCalendar(),
    private val clock: Clock = Clock.systemUTC(),
    private val zoneId: ZoneId = ZoneId.systemDefault(),
    private val random: Random = Random.Default,
) {
    /**
     * Ensures the Monday 02:00 week has one Bronze, one Silver and one Gold.
     *
     * Expired rows are closed first. An ACTIVE quest that is no longer
     * completable with remaining unwatched films is replaced. Snapshots of
     * target and XP are frozen on insert so a later pack edit cannot change
     * a quest already handed out.
     */
    suspend fun ensureCurrentWeek(userId: Long, now: Instant = Instant.now(clock)) {
        withContext(Dispatchers.IO) {
            ensureCurrentWeekInternal(userId, now)
        }
    }

    private suspend fun ensureCurrentWeekInternal(userId: Long, now: Instant) {
        val week = questCalendar.weekContaining(now, zoneId)
        val dao = database.progressDao()
        try {
            dao.expireQuests(userId, now)
            val definitions = dao.activeQuestDefinitions()
            if (definitions.isEmpty()) {
                Log.w(TAG, "No active quest definitions in the catalogue")
                return
            }

            val unwatched = loadUnwatchedMovies(userId)
            val eligibilityKnown = unwatched != null
            val remaining = unwatched.orEmpty()
            val assignments = dao.questAssignmentsForWeek(userId, week.startsAt)
            val impossible = assignments.filter { assignment ->
                assignment.assignment.status == UserQuestStatus.ACTIVE &&
                    eligibilityKnown &&
                    !isStillPossible(assignment, remaining)
            }
            val occupied = assignments
                .filter {
                    it.assignment.status == UserQuestStatus.ACTIVE ||
                        it.assignment.status == UserQuestStatus.COMPLETED
                }
                .filter { candidate ->
                    impossible.none { it.assignment.userQuestId == candidate.assignment.userQuestId }
                }
                .map { it.definition.difficulty.name }
                .toSet()
            val usedQuestIds = assignments.map { it.assignment.questId }.toMutableSet()
            val replacements = QuestDifficulty.entries.mapNotNull { difficulty ->
                if (difficulty.name in occupied) return@mapNotNull null
                pickQuest(definitions, difficulty, usedQuestIds, remaining, eligibilityKnown)
                    ?.also { usedQuestIds += it.questId }
            }

            database.withTransaction {
                impossible.forEach { dao.expireUserQuest(it.assignment.userQuestId) }
                replacements.forEach { definition ->
                    dao.insertUserQuest(
                        UserQuestEntity(
                            userId = userId,
                            questId = definition.questId,
                            startsAt = week.startsAt,
                            expiresAt = week.expiresAt,
                            targetCountSnapshot = definition.targetCount,
                            xpRewardSnapshot = xpEngine.rewardFor(
                                QuestDifficulty.valueOf(definition.difficulty.name),
                            ),
                        )
                    )
                }
            }
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            Log.e(TAG, "Weekly quest assignment failed, falling back", error)
            fallbackAssign(userId, week)
        }
    }

    /**
     * Re-reads validations, updates quest progress, and grants XP once when a
     * quest crosses its target during the active week.
     */
    suspend fun onProgressChanged(userId: Long, now: Instant = Instant.now(clock)) {
        withContext(Dispatchers.IO) {
            onProgressChangedInternal(userId, now)
        }
    }

    private suspend fun onProgressChangedInternal(userId: Long, now: Instant) {
        ensureCurrentWeekInternal(userId, now)
        val week = questCalendar.weekContaining(now, zoneId)
        val dao = database.progressDao()
        val assignments = dao.questAssignmentsForWeek(userId, week.startsAt)
        val lookup = continentLookup()
        val primaryCountryIds = primaryCountryIds()
        val moviesById = dao.validatedMovies(userId).mapNotNull { rel ->
            rel.toQuestMovie(lookup, primaryCountryIds[rel.movie.movieId])
                ?.let { rel.movie.movieId to it }
        }.toMap()
        val validations = dao.movieValidations(userId).mapNotNull { row ->
            moviesById[row.movieId]?.let { movie ->
                MovieValidation(movie, row.watchedOn, row.validatedAt)
            }
        }

        assignments.filter { it.assignment.status == UserQuestStatus.ACTIVE }.forEach { value ->
            val assigned = AssignedQuest(
                assignmentCode = EditorialCode("USER_QUEST_${value.assignment.userQuestId}"),
                definition = QuestDefinition(
                    code = EditorialCode(value.definition.code),
                    ruleCode = EditorialCode(value.definition.ruleCode),
                    difficulty = QuestDifficulty.valueOf(value.definition.difficulty.name),
                    targetCount = value.assignment.targetCountSnapshot,
                ),
                week = week,
                targetCountSnapshot = value.assignment.targetCountSnapshot,
                xpRewardSnapshot = value.assignment.xpRewardSnapshot,
                completedAt = value.assignment.completedAt,
                rewarded = false,
            )
            val progress = questEngine.progress(assigned, validations)
            when (val reward = questEngine.reward(assigned, validations, now)) {
                is QuestRewardResult.Granted -> {
                    Log.i(
                        TAG,
                        "Quête ${value.definition.code} (${value.definition.difficulty}) " +
                            "terminée : +${value.assignment.xpRewardSnapshot} XP",
                    )
                    progressRepository.completeQuest(
                        userId = userId,
                        userQuestId = value.assignment.userQuestId,
                        activityPayloadJson =
                            """{"version":1,"questCode":"${value.definition.code}"}""",
                    )
                }
                else -> dao.updateQuestProgress(
                    userQuestId = value.assignment.userQuestId,
                    progress = progress.count,
                    status = UserQuestStatus.ACTIVE,
                    completedAt = null,
                )
            }
        }
        val profile = dao.localUser()
        if (profile != null) {
            val calculated = xpEngine.progress(dao.totalXp(userId), profile.maxLevelReached)
            dao.advanceMaxLevel(userId, calculated.displayedLevel)
        }
    }

    fun currentWeekStartsAt(now: Instant = Instant.now(clock)): Instant =
        questCalendar.weekContaining(now, zoneId).startsAt

    private suspend fun loadUnwatchedMovies(userId: Long): List<Movie>? {
        return runCatching {
            val catalogDao = database.catalogDao()
            val catalog = catalogDao.allMoviesWithRelations()
            if (catalog.isEmpty()) return@runCatching emptyList()
            val lookup = continentLookup()
            val primaryCountryIds = primaryCountryIds()
            val watchedCodes = database.progressDao().validatedMovies(userId)
                .map { it.movie.code }
                .toSet()
            val mapped = catalog.mapNotNull { rel ->
                rel.toQuestMovie(lookup, primaryCountryIds[rel.movie.movieId])
            }.filter { it.code.value !in watchedCodes }
            if (mapped.isEmpty() && catalog.any { it.movie.code !in watchedCodes }) {
                return@runCatching null
            }
            mapped
        }.onFailure { Log.e(TAG, "Could not evaluate quest remaining films", it) }.getOrNull()
    }

    private suspend fun continentLookup(): Map<Long, Set<String>> {
        val continents = database.catalogDao().continents().associateBy(ContinentEntity::continentId)
        return database.catalogDao().countryContinents()
            .groupBy { it.countryId }
            .mapValues { (_, rows) ->
                rows.mapNotNull { continents[it.continentId]?.code }.toSet()
            }
    }

    private suspend fun primaryCountryIds(): Map<Long, Long> =
        database.catalogDao().movieCountries()
            .filter { it.isPrimary }
            .associate { it.movieId to it.countryId }

    private suspend fun fallbackAssign(userId: Long, week: fr.jsisie.urbinema.domain.quest.QuestWeek) {
        val dao = database.progressDao()
        if (dao.questAssignmentsForWeek(userId, week.startsAt).any {
                it.assignment.status == UserQuestStatus.ACTIVE
            }
        ) {
            return
        }
        val definitions = dao.activeQuestDefinitions()
        QuestDifficulty.entries.forEach { difficulty ->
            val definition = definitions.filter { it.difficulty.name == difficulty.name }
                .randomOrNull(random) ?: return@forEach
            runCatching {
                dao.insertUserQuest(
                    UserQuestEntity(
                        userId = userId,
                        questId = definition.questId,
                        startsAt = week.startsAt,
                        expiresAt = week.expiresAt,
                        targetCountSnapshot = definition.targetCount,
                        xpRewardSnapshot = xpEngine.rewardFor(difficulty),
                    )
                )
            }.onFailure { Log.e(TAG, "Fallback quest insert failed for ${difficulty.name}", it) }
        }
    }

    private fun isStillPossible(assignment: UserQuestWithDefinition, unwatched: List<Movie>): Boolean {
        val remaining = runCatching {
            rules.require(EditorialCode(assignment.definition.ruleCode)).remainingCapacity(unwatched)
        }.getOrDefault(Int.MAX_VALUE)
        return remaining + assignment.assignment.progress >= assignment.assignment.targetCountSnapshot
    }

    private fun pickQuest(
        definitions: List<QuestEntity>,
        difficulty: QuestDifficulty,
        usedQuestIds: Set<Long>,
        unwatched: List<Movie>,
        eligibilityKnown: Boolean,
    ): QuestEntity? {
        val sameDifficulty = definitions.filter {
            it.difficulty.name == difficulty.name && it.questId !in usedQuestIds
        }
        val eligible = sameDifficulty.filter { definition ->
            if (!eligibilityKnown) return@filter true
            val remaining = runCatching {
                rules.require(EditorialCode(definition.ruleCode)).remainingCapacity(unwatched)
            }.getOrNull() ?: return@filter true
            remaining >= definition.targetCount
        }
        val pool = when {
            eligible.isNotEmpty() -> eligible
            !eligibilityKnown -> sameDifficulty
            else -> emptyList()
        }
        if (pool.isEmpty()) return null
        return pool[random.nextInt(pool.size)]
    }

    private fun MovieWithRelations.toQuestMovie(
        continentCodesByCountryId: Map<Long, Set<String>>,
        primaryCountryId: Long?,
    ): Movie? = runCatching {
        val primary = countries.firstOrNull { it.countryId == primaryCountryId }
            ?: countries.firstOrNull()
            ?: return null
        Movie(
            code = EditorialCode(movie.code),
            originalTitle = movie.originalTitle,
            frenchTitle = movie.frenchTitle,
            synopsis = movie.synopsis,
            releaseYear = movie.releaseYear,
            durationMinutes = movie.durationMinutes,
            format = MovieFormat.valueOf(movie.format.name),
            weight = MovieWeightComponents(
                historicalDistance = movie.historicalDistance.coerceIn(0.0, 1.0),
                artisticDemand = movie.artisticDemand.coerceIn(0.0, 1.0),
                historicalImportance = movie.historicalRichness.coerceIn(0.0, 1.0),
                culturalRichness = movie.culturalRichness.coerceIn(0.0, 1.0),
            ),
            primaryCountry = EditorialCode(primary.code),
            countries = countries.mapTo(linkedSetOf()) { EditorialCode(it.code) }
                .ifEmpty { linkedSetOf(EditorialCode(primary.code)) },
            continents = countries.flatMap { continentCodesByCountryId[it.countryId].orEmpty() }
                .mapTo(linkedSetOf(), ::EditorialCode),
            directors = directors.mapNotNull { runCatching { EditorialCode(it.code) }.getOrNull() }
                .toCollection(linkedSetOf()),
            genres = genres.mapNotNull { runCatching { EditorialCode(it.code) }.getOrNull() }
                .toCollection(linkedSetOf()),
            characteristics = characteristics.mapNotNull { runCatching { EditorialCode(it.code) }.getOrNull() }
                .toCollection(linkedSetOf()),
            isSilent = movie.isSilent,
            isBlackAndWhite = movie.isBlackAndWhite,
            isExperimental = movie.isExperimental,
        )
    }.getOrNull()

    private companion object {
        const val TAG = "UrbinemaQuests"
    }
}
