package fr.jsisie.urbinema.domain.xp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class XpEngineTest {
    private val engine = XpEngine()

    @Test
    fun `all fifty exact thresholds match the specification`() {
        val expected = listOf(
            0L, 115L, 255L, 455L, 725L, 1_000L, 1_295L, 1_610L, 1_945L, 2_300L,
            2_820L, 3_380L, 3_980L, 4_620L, 5_300L, 6_000L, 6_740L, 7_520L,
            8_340L, 9_200L, 10_300L, 11_925L, 14_075L, 16_750L, 19_950L,
            23_152L, 26_354L, 29_556L, 32_758L, 35_960L, 39_162L, 42_364L,
            45_566L, 48_768L, 51_970L, 55_172L, 58_374L, 61_576L, 64_778L,
            67_980L, 71_182L, 74_384L, 77_586L, 80_788L, 83_990L, 87_192L,
            90_394L, 93_596L, 96_798L, 100_000L,
        )
        assertEquals(expected, engine.thresholds)
    }

    @Test
    fun `every threshold and preceding xp resolve to the expected level`() {
        (1..50).forEach { level ->
            val threshold = engine.thresholdFor(level)
            assertEquals(level, engine.progress(threshold).calculatedLevel)
            if (level < 50) {
                assertEquals(level, engine.progress(engine.thresholdFor(level + 1) - 1).calculatedLevel)
            }
        }
    }

    @Test
    fun `level is capped at fifty and historical level ratchets`() {
        assertEquals(50, engine.progress(1_000_000).calculatedLevel)
        val progress = engine.progress(totalXp = 0, historicalMaxLevel = 42)
        assertEquals(1, progress.calculatedLevel)
        assertEquals(42, progress.displayedLevel)
    }

    @Test
    fun `all transition costs are positive and plateau is exact`() {
        assertTrue((1..49).all { engine.costToNextLevel(it) > 0 })
        assertTrue((25..49).all { engine.costToNextLevel(it) == 3_202 })
    }

    @Test
    fun `quest rewards are exact and increasing`() {
        assertEquals(100, engine.rewardFor(QuestDifficulty.BRONZE))
        assertEquals(250, engine.rewardFor(QuestDifficulty.SILVER))
        assertEquals(500, engine.rewardFor(QuestDifficulty.GOLD))
        assertEquals(10, engine.rewardForFilm())
    }
}
