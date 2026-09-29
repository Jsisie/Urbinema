package fr.jsisie.urbinema.domain.collection

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CollectionUnlockRulesTest {
    @Test
    fun `a track with many collections still asks for two started ones`() {
        assertEquals(2, CollectionUnlockRules.requiredStartedCount(8))
        assertFalse(CollectionUnlockRules.previousTrackOpen(8, 1))
        assertTrue(CollectionUnlockRules.previousTrackOpen(8, 2))
    }

    @Test
    fun `a track with a single collection only requires that one`() {
        assertEquals(1, CollectionUnlockRules.requiredStartedCount(1))
        assertTrue(CollectionUnlockRules.previousTrackOpen(1, 1))
        assertFalse(CollectionUnlockRules.previousTrackOpen(1, 0))
    }

    @Test
    fun `an empty previous track does not open the next one`() {
        assertEquals(2, CollectionUnlockRules.requiredStartedCount(0))
        assertFalse(CollectionUnlockRules.previousTrackOpen(0, 0))
    }

    @Test
    fun `qualification needs two films and a follow`() {
        assertFalse(CollectionUnlockRules.isQualified(watchedCount = 2, followed = false))
        assertFalse(CollectionUnlockRules.isQualified(watchedCount = 1, followed = true))
        assertTrue(CollectionUnlockRules.isQualified(watchedCount = 2, followed = true))
    }

    @Test
    fun `an opened track stays open after the starts disappear`() {
        val tracks = listOf(2 to 8, 0 to 6, 0 to 4)
        val open = CollectionUnlockRules.latchedOpenOrdinal(
            initiationOpen = true,
            tracks = tracks,
            latchedOrdinal = 1,
        )
        assertEquals(1, open)
        assertFalse(CollectionUnlockRules.isTrackLocked(1, open))
        assertTrue(CollectionUnlockRules.isTrackLocked(2, open))
    }

    @Test
    fun `without initiation every other collection stays locked even with a latch`() {
        assertEquals(
            CollectionUnlockRules.LOCKED_ORDINAL,
            CollectionUnlockRules.computedOpenOrdinal(false, listOf(2 to 3)),
        )
        assertEquals(
            CollectionUnlockRules.LOCKED_ORDINAL,
            CollectionUnlockRules.latchedOpenOrdinal(false, listOf(0 to 3), latchedOrdinal = 2),
        )
    }

    @Test
    fun `initiation opens premieres seances only when followed and one film is watched`() {
        assertFalse(CollectionUnlockRules.isInitiationOpen(watchedCount = 1, followed = false))
        assertFalse(CollectionUnlockRules.isInitiationOpen(watchedCount = 0, followed = true))
        assertTrue(CollectionUnlockRules.isInitiationOpen(watchedCount = 1, followed = true))
    }

    @Test
    fun `gateway stays closed until initiation has a watched film`() {
        val tracks = listOf(0 to 2, 0 to 5, 0 to 3)
        assertEquals(
            CollectionUnlockRules.LOCKED_ORDINAL,
            CollectionUnlockRules.latchedOpenOrdinal(false, tracks, latchedOrdinal = -1),
        )
        assertTrue(CollectionUnlockRules.isTrackLocked(0, CollectionUnlockRules.LOCKED_ORDINAL))
    }
}
