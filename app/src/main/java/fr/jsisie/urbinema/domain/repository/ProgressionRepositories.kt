package fr.jsisie.urbinema.domain.repository

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieValidation
import fr.jsisie.urbinema.domain.quest.AssignedQuest
import fr.jsisie.urbinema.domain.rank.CatalogRankStats
import java.time.Instant

interface ProgressionReadRepository {
    /** Loads the unique validated movie set used for deterministic recalculation. */
    suspend fun validatedMovies(userId: Long): List<Movie>

    /** Loads dated validations used only by non-retroactive quest rules. */
    suspend fun movieValidations(userId: Long): List<MovieValidation>

    /** Loads permanently earned badge codes. */
    suspend fun earnedBadgeCodes(userId: Long): Set<EditorialCode>

    /** Sums the immutable XP ledger rather than trusting a mutable cache. */
    suspend fun totalXp(userId: Long): Long
}

interface RankStateRepository {
    /** Loads the greatest rank ever displayed for the profile ratchet. */
    suspend fun maximumRank(userId: Long): Int

    /** Advances the rank ratchet atomically and never lowers it. */
    suspend fun advanceMaximumRank(userId: Long, candidate: Int): Int

    /** Loads the latest persisted rarity and dimension-weight ratchets. */
    suspend fun latestCatalogStats(): CatalogRankStats?

    /** Stores one newer catalog-stat version transactionally. */
    suspend fun saveCatalogStats(stats: CatalogRankStats)
}

interface BadgeStateRepository {
    /** Inserts newly earned badges idempotently and preserves prior acquisitions. */
    suspend fun grantBadges(userId: Long, badgeCodes: Set<EditorialCode>, earnedAt: Instant): Set<EditorialCode>
}

interface QuestStateRepository {
    /** Loads the three assignments for the cycle, if they were already created. */
    suspend fun assignmentsFor(userId: Long, startsAt: Instant): List<AssignedQuest>

    /** Persists exactly one weekly Bronze/Silver/Gold set atomically. */
    suspend fun createAssignments(userId: Long, assignments: List<AssignedQuest>)

    /**
     * Inserts one XP transaction keyed uniquely by assignment and marks the
     * quest completed in the same transaction.
     */
    suspend fun completeAndReward(
        userId: Long,
        assignmentCode: EditorialCode,
        xp: Int,
        completedAt: Instant,
    ): Boolean
}
