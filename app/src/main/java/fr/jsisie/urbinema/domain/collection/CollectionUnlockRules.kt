package fr.jsisie.urbinema.domain.collection

/**
 * Unlock chain between collection difficulty tracks.
 *
 * A harder track opens when the previous one has enough **started**
 * collections (followed, with 2+ films watched). Unfollowing must not
 * re-lock the next group (ordinal latch).
 * Once a track ordinal has been opened it is latched forever (except reset).
 */
object CollectionUnlockRules {
    const val MIN_STARTED_COLLECTIONS = 2
    const val MIN_FILMS_PER_COLLECTION = 2
    const val INITIATION_MIN_FILMS = 1
    const val LOCKED_ORDINAL = -1

    /** How many started collections the previous track must have before the next opens. */
    fun requiredStartedCount(previousTrackSize: Int): Int {
        if (previousTrackSize <= 0) return MIN_STARTED_COLLECTIONS
        return minOf(MIN_STARTED_COLLECTIONS, previousTrackSize)
    }

    /**
     * A collection counts as started for the next-track gate only if it is
     * **followed** and has at least [MIN_FILMS_PER_COLLECTION] watched films.
     * Shared titles (Initiation ∩ Nouvel Hollywood) must not open Ciné-club
     * just because the user marked two overlapping films Vu.
     */
    fun isQualified(watchedCount: Int, followed: Boolean): Boolean =
        followed && watchedCount >= MIN_FILMS_PER_COLLECTION

    /** Initiation itself opens the rest of GATEWAY after a single watched film. */
    fun isInitiationOpen(watchedCount: Int): Boolean =
        watchedCount >= INITIATION_MIN_FILMS

    /**
     * An empty previous track never unlocks the next one (size 0 would otherwise
     * satisfy `requiredStartedCount(0) == 0`).
     */
    fun previousTrackOpen(previousTrackSize: Int, qualifiedCount: Int): Boolean {
        if (previousTrackSize <= 0) return false
        return qualifiedCount >= requiredStartedCount(previousTrackSize)
    }

    /**
     * Highest open track ordinal (0 = GATEWAY, including Hollywood).
     * [LOCKED_ORDINAL] means only Initiation itself is available.
     *
     * The latch keeps a harder group open after unfollow, but **never**
     * bypasses Initiation: without one watched Initiation film, every other
     * collection stays locked (reset included).
     *
     * [tracks] is ordered like the UI tracks: each pair is
     * (qualifiedCount, size) for that group.
     */
    fun latchedOpenOrdinal(
        initiationOpen: Boolean,
        tracks: List<Pair<Int, Int>>,
        latchedOrdinal: Int,
    ): Int {
        if (!initiationOpen) return LOCKED_ORDINAL
        return maxOf(computedOpenOrdinal(true, tracks), latchedOrdinal)
    }

    fun computedOpenOrdinal(
        initiationOpen: Boolean,
        tracks: List<Pair<Int, Int>>,
    ): Int {
        if (!initiationOpen) return LOCKED_ORDINAL
        var open = 0
        for (index in 1 until tracks.size) {
            val (qualified, size) = tracks[index - 1]
            if (!previousTrackOpen(size, qualified)) break
            open = index
        }
        return open
    }

    fun isTrackLocked(trackOrdinal: Int, openOrdinal: Int): Boolean {
        if (openOrdinal < 0) return true
        return trackOrdinal > openOrdinal
    }
}
