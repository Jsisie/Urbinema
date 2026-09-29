package fr.jsisie.urbinema.domain.xp

import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.domain.FunctionalLimits

data class XpCurveSegment(
    val startLevel: Int,
    val endLevel: Int,
    val baseCost: Int,
    val incrementPerLevel: Int,
) {
    init {
        val maxLevel = 50
        require(startLevel in 1..maxLevel-1 && endLevel in startLevel..maxLevel-1)
        require(baseCost > 0 && incrementPerLevel >= 0)
    }

    /** Returns the transition cost represented by this segment. */
    fun costAt(level: Int): Int {
        require(level in startLevel..endLevel)
        return baseCost + incrementPerLevel * (level - startLevel)
    }
}

data class XpConfiguration(
    val maxLevel: Int = 50,
    val filmReward: Int = FunctionalLimits.FILM_XP_IN_FOLLOWED_COLLECTION,
    val rewards: Map<QuestDifficulty, Int> = mapOf(
        QuestDifficulty.BRONZE to 100,
        QuestDifficulty.SILVER to 250,
        QuestDifficulty.GOLD to 500,
    ),
    val segments: List<XpCurveSegment> = exactV1Segments,
) {
    init {
        require(maxLevel >= 2)
        require(filmReward >= 0)
        require(rewards.keys == QuestDifficulty.entries.toSet())
        require(rewards.values.all { it > 0 } && QuestDifficulty.entries
            .zipWithNext().all { (a, b) -> rewards.getValue(a) < rewards.getValue(b) })
        val covered = segments.flatMap { it.startLevel..it.endLevel }
        require(covered == (1 until maxLevel).toList()) { "XP segments must cover every transition exactly once" }
    }

    companion object {
        /** Exact segments from FORMULE_NIVEAUX_XP v1.0. */
        val exactV1Segments: List<XpCurveSegment> = listOf(
            XpCurveSegment(1, 1, 115, 0),
            XpCurveSegment(2, 2, 140, 0),
            XpCurveSegment(3, 3, 200, 0),
            XpCurveSegment(4, 4, 270, 0),
            XpCurveSegment(5, 9, 275, 20),
            XpCurveSegment(10, 14, 520, 40),
            XpCurveSegment(15, 19, 700, 40),
            XpCurveSegment(20, 24, 1_100, 525),
            XpCurveSegment(25, 49, 3_202, 0),
        )
    }
}

enum class QuestDifficulty { BRONZE, SILVER, GOLD }

data class LevelProgress(
    val totalXp: Long,
    val calculatedLevel: Int,
    val displayedLevel: Int,
    val currentLevelThreshold: Long,
    val nextLevelThreshold: Long?,
    val xpIntoLevel: Long,
    val xpNeededForNextLevel: Long?,
)

/** Exact, configurable XP curve with a historical level ratchet. */
class XpEngine(private val configuration: XpConfiguration = XpConfiguration()) {
    val thresholds: List<Long> = buildThresholds()

    init {
        require(thresholds.first() == 0L)
        require(thresholds.zipWithNext().all { (a, b) -> a < b })
    }

    /** Returns the cumulative XP required to reach [level]. */
    fun thresholdFor(level: Int): Long {
        require(level in 1..configuration.maxLevel)
        return thresholds[level - 1]
    }

    /** Returns the configured cost of the transition after [level]. */
    fun costToNextLevel(level: Int): Int {
        require(level in 1 until configuration.maxLevel)
        return configuration.segments.single { level in it.startLevel..it.endLevel }.costAt(level)
    }

    /** Resolves level progress without ever dropping below [historicalMaxLevel]. */
    fun progress(totalXp: Long, historicalMaxLevel: Int = 1): LevelProgress {
        require(totalXp >= 0)
        require(historicalMaxLevel in 1..configuration.maxLevel)
        val calculated = thresholds.indexOfLast { it <= totalXp } + 1
        val displayed = maxOf(calculated, historicalMaxLevel)
        val currentThreshold = thresholdFor(calculated)
        val next = thresholds.getOrNull(calculated)
        return LevelProgress(
            totalXp = totalXp,
            calculatedLevel = calculated,
            displayedLevel = displayed,
            currentLevelThreshold = currentThreshold,
            nextLevelThreshold = next,
            xpIntoLevel = totalXp - currentThreshold,
            xpNeededForNextLevel = next?.minus(totalXp),
        )
    }

    /** Returns the immutable reward associated with a quest difficulty. */
    fun rewardFor(difficulty: QuestDifficulty): Int = configuration.rewards.getValue(difficulty)

    /** XP once, and only when the film sits in a followed collection. Otherwise 0. */
    fun rewardForFilm(): Int = configuration.filmReward

    private fun buildThresholds(): List<Long> {
        val result = MutableList(configuration.maxLevel) { 0L }
        for (level in 1 until configuration.maxLevel) {
            result[level] = result[level - 1] + costToNextLevel(level)
        }
        return result
    }
}
