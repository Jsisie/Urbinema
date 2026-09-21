package fr.jsisie.urbinema.domain.quest

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieValidation
import fr.jsisie.urbinema.domain.xp.QuestDifficulty
import java.time.DayOfWeek
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.temporal.TemporalAdjusters

data class QuestWeek(val startsAt: Instant, val expiresAt: Instant, val zoneId: ZoneId) {
    init {
        require(startsAt < expiresAt)
    }

    /** Tests the half-open weekly interval used for activation and expiration. */
    fun contains(instant: Instant): Boolean = !instant.isBefore(startsAt) && instant.isBefore(expiresAt)
}

/** Resolves local weekly boundaries without assuming that every local day is 24 hours. */
class QuestCalendar {
    /** Returns the Monday 02:00 cycle containing [now] in [zoneId]. */
    fun weekContaining(now: Instant, zoneId: ZoneId): QuestWeek {
        val localNow = now.atZone(zoneId)
        var monday = localNow.toLocalDate().with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
        var start = atTwoAm(monday, zoneId)
        if (localNow.isBefore(start)) {
            monday = monday.minusWeeks(1)
            start = atTwoAm(monday, zoneId)
        }
        return QuestWeek(start.toInstant(), atTwoAm(monday.plusWeeks(1), zoneId).toInstant(), zoneId)
    }

    private fun atTwoAm(date: LocalDate, zoneId: ZoneId): ZonedDateTime =
        ZonedDateTime.of(LocalDateTime.of(date, LocalTime.of(2, 0)), zoneId)
}

interface QuestRule {
    /** Counts qualifying progress from eligible validations, capped by the caller's target. */
    fun progress(validations: Collection<MovieValidation>): Int

    /** How many units of the quest can still be completed with films not yet watched. */
    fun remainingCapacity(unwatchedMovies: Collection<Movie>): Int
}

class QuestRuleRegistry(
    rules: Map<EditorialCode, QuestRule> = emptyMap(),
    private val resolve: (EditorialCode) -> QuestRule? = { null },
) {
    private val rules = rules.toMap()

    /** Resolves a stable catalog rule code or fails fast on invalid content. */
    fun require(code: EditorialCode): QuestRule =
        rules[code] ?: resolve(code)
            ?: error("No quest rule registered for ${code.value}")
}

data class QuestDefinition(
    val code: EditorialCode,
    val ruleCode: EditorialCode,
    val difficulty: QuestDifficulty,
    val targetCount: Int,
) {
    init {
        require(targetCount > 0)
    }
}

data class AssignedQuest(
    val assignmentCode: EditorialCode,
    val definition: QuestDefinition,
    val week: QuestWeek,
    val targetCountSnapshot: Int = definition.targetCount,
    val xpRewardSnapshot: Int,
    val completedAt: Instant? = null,
    val rewarded: Boolean = false,
) {
    init {
        require(targetCountSnapshot > 0 && xpRewardSnapshot > 0)
        require(completedAt == null || week.contains(completedAt))
        require(!rewarded || completedAt != null)
    }
}

data class WeeklyQuestSet(val quests: List<AssignedQuest>) {
    init {
        require(quests.size == 3) { "A week contains exactly three quests" }
        require(quests.map { it.definition.difficulty }.toSet() == QuestDifficulty.entries.toSet()) {
            "A week must contain one Bronze, one Silver and one Gold quest"
        }
        require(quests.map { it.week }.distinct().size == 1) { "Weekly quests must share one cycle" }
    }
}

data class QuestProgress(
    val count: Int,
    val target: Int,
    val completed: Boolean,
    val completedAt: Instant?,
)

sealed interface QuestRewardResult {
    data class Granted(val xp: Int, val completedAt: Instant) : QuestRewardResult
    data object AlreadyGranted : QuestRewardResult
    data object NotCompleted : QuestRewardResult
    data object Expired : QuestRewardResult
}

/** Applies weekly eligibility, non-retroactivity and one-time XP semantics. */
class QuestEngine(private val registry: QuestRuleRegistry) {
    /**
     * Computes progress using only validations recorded during the assignment
     * and watched within its Monday-to-Monday local date window.
     */
    fun progress(quest: AssignedQuest, validations: Collection<MovieValidation>): QuestProgress {
        val startDate = quest.week.startsAt.atZone(quest.week.zoneId).toLocalDate()
        val endDateExclusive = quest.week.expiresAt.atZone(quest.week.zoneId).toLocalDate()
        val eligible = validations
            .filter { quest.week.contains(it.validatedAt) }
            .filter { !it.watchedOn.isBefore(startDate) && it.watchedOn.isBefore(endDateExclusive) }
            .distinctBy { it.movie.code }
        val calculatedCount = registry.require(quest.definition.ruleCode).progress(eligible)
            .coerceIn(0, quest.targetCountSnapshot)
        val completed = quest.completedAt != null || calculatedCount >= quest.targetCountSnapshot
        val count = if (quest.completedAt != null) quest.targetCountSnapshot else calculatedCount
        return QuestProgress(
            count = count,
            target = quest.targetCountSnapshot,
            completed = completed,
            completedAt = quest.completedAt,
        )
    }

    /** Decides an idempotent XP award; persistence enforces assignment uniqueness. */
    fun reward(
        quest: AssignedQuest,
        validations: Collection<MovieValidation>,
        now: Instant,
    ): QuestRewardResult {
        if (quest.rewarded) return QuestRewardResult.AlreadyGranted
        if (!quest.week.contains(now)) return QuestRewardResult.Expired
        val progress = progress(quest, validations)
        if (!progress.completed) return QuestRewardResult.NotCompleted
        return QuestRewardResult.Granted(quest.xpRewardSnapshot, now)
    }
}

/** Reusable quest rules that keep catalog-specific selection outside the engine. */
object QuestRules {
    /** Counts distinct validated films matching [predicate]. */
    fun matchingMovies(predicate: (Movie) -> Boolean): QuestRule =
        object : QuestRule {
            override fun progress(validations: Collection<MovieValidation>): Int =
                validations.map { it.movie }.distinctBy { it.code }.count(predicate)

            override fun remainingCapacity(unwatchedMovies: Collection<Movie>): Int =
                unwatchedMovies.distinctBy { it.code }.count(predicate)
        }

    /** Counts distinct values extracted from matching films. */
    fun distinct(extractor: (Movie) -> Iterable<EditorialCode>): QuestRule = object : QuestRule {
        override fun progress(validations: Collection<MovieValidation>): Int =
            validations.map { it.movie }.distinctBy { it.code }.flatMap(extractor).toSet().size

        override fun remainingCapacity(unwatchedMovies: Collection<Movie>): Int =
            unwatchedMovies.distinctBy { it.code }.flatMap(extractor).toSet().size
    }
}
