package fr.jsisie.urbinema.data.repository

import androidx.paging.PagingSource
import androidx.room.withTransaction
import fr.jsisie.urbinema.data.db.ActivityEventEntity
import fr.jsisie.urbinema.data.db.CollectionEntity
import fr.jsisie.urbinema.data.db.MovieEntity
import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.db.UserFollowedCollectionCrossRef
import fr.jsisie.urbinema.data.db.UserMovieCrossRef
import fr.jsisie.urbinema.data.db.UserQuestStatus
import fr.jsisie.urbinema.data.db.XpSources
import fr.jsisie.urbinema.data.db.XpTransactionEntity
import fr.jsisie.urbinema.domain.xp.XpEngine
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import kotlinx.coroutines.flow.Flow

/** Read-only catalogue gateway kept in data until domain contracts are introduced. */
class CatalogRepository(private val database: UrbinemaDatabase) {
    /** Streams active films. */
    fun observeMovies(): Flow<List<MovieEntity>> = database.catalogDao().observeMovies()

    /** Returns a Paging 3 source for the complete active catalogue. */
    fun pageMovies(): PagingSource<Int, MovieEntity> = database.catalogDao().pageMovies()

    /** Loads a film aggregate by technical identifier. */
    suspend fun movieDetails(movieId: Long): MovieWithRelations? =
        database.catalogDao().movieWithRelations(movieId)

    /** Streams published editorial collections. */
    fun observeCollections(): Flow<List<CollectionEntity>> =
        database.catalogDao().observeCollections()
}

/**
 * Transaction boundary for progression writes. Domain recalculation remains outside data,
 * while persistence-level bounds and ledger uniqueness are enforced here and by SQLite.
 */
class ProgressRepository(
    private val database: UrbinemaDatabase,
    private val xpEngine: XpEngine,
    private val clock: Clock = Clock.systemDefaultZone(),
) {
    /** Validates a film and records its history event atomically. */
    suspend fun markWatched(
        userId: Long,
        movieId: Long,
        watchedOn: LocalDate,
        activityPayloadJson: String,
        awardFilmXp: Boolean,
    ) {
        require(!watchedOn.isAfter(LocalDate.now(clock))) { "watchedOn cannot be in the future" }
        val now = Instant.now(clock)
        database.withTransaction {
            database.progressDao().insertUserMovie(
                UserMovieCrossRef(userId, movieId, watchedOn, now)
            )
            database.progressDao().insertActivityEvent(
                ActivityEventEntity(
                    userId = userId,
                    type = "MOVIE_VALIDATED",
                    occurredAt = now,
                    payloadJson = activityPayloadJson,
                )
            )
            val filmXp = if (awardFilmXp) xpEngine.rewardForFilm() else 0
            if (filmXp > 0) {
                database.progressDao().insertXpTransactionIgnore(
                    XpTransactionEntity(
                        userId = userId,
                        movieId = movieId,
                        source = XpSources.FILM,
                        amount = filmXp,
                        earnedAt = now,
                    )
                )
            }
        }
    }

    /** Adds a collection to the user's current collections. No-op if already followed. */
    suspend fun followCollection(userId: Long, collectionId: Long) {
        database.progressDao().insertFollowedCollection(
            UserFollowedCollectionCrossRef(
                userId = userId,
                collectionId = collectionId,
                followedAt = Instant.now(clock),
            )
        )
    }

    /** Removes a collection from the user's current collections. */
    suspend fun unfollowCollection(userId: Long, collectionId: Long) {
        database.progressDao().deleteFollowedCollection(userId, collectionId)
    }

    /** Completes a quest and writes its strictly positive, one-time XP reward atomically. */
    suspend fun completeQuest(
        userId: Long,
        userQuestId: Long,
        activityPayloadJson: String,
    ) {
        val now = Instant.now(clock)
        database.withTransaction {
            val quest = checkNotNull(database.progressDao().userQuestById(userQuestId)) {
                "Unknown user quest $userQuestId"
            }
            require(quest.userId == userId) { "Quest does not belong to user $userId" }
            require(quest.status == UserQuestStatus.ACTIVE) { "Quest is not active" }
            require(quest.targetCountSnapshot > 0) { "targetCount snapshot must be positive" }
            require(quest.xpRewardSnapshot > 0) { "XP reward snapshot must be positive" }
            database.progressDao().updateQuestProgress(
                userQuestId = userQuestId,
                progress = quest.targetCountSnapshot,
                status = UserQuestStatus.COMPLETED,
                completedAt = now,
            )
            database.progressDao().insertXpTransaction(
                XpTransactionEntity(
                    userId = userId,
                    userQuestId = userQuestId,
                    source = XpSources.QUEST,
                    amount = quest.xpRewardSnapshot,
                    earnedAt = now,
                )
            )
            database.progressDao().insertActivityEvent(
                ActivityEventEntity(
                    userId = userId,
                    type = "QUEST_COMPLETED",
                    occurredAt = now,
                    payloadJson = activityPayloadJson,
                )
            )
        }
    }

    /** Streams XP from the immutable transaction ledger. */
    fun observeTotalXp(userId: Long): Flow<Long> =
        database.progressDao().observeTotalXp(userId)

    /** Clears only progression; catalogue, preferences and profile identity survive. */
    suspend fun resetProgress(userId: Long) {
        database.withTransaction {
            val dao = database.progressDao()
            val firstRank = checkNotNull(dao.rankingByOrder(1))
            dao.clearXpTransactions(userId)
            dao.clearUserQuests(userId)
            dao.clearUserBadges(userId)
            dao.clearUserMovies(userId)
            dao.clearFollowedCollections(userId)
            dao.clearActivityEvents(userId)
            dao.clearProgressState(userId)
            dao.resetUserRatchets(userId, firstRank.rankingId)
        }
    }
}
