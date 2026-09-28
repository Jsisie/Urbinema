package fr.jsisie.urbinema.domain.collection

import fr.jsisie.urbinema.domain.FunctionalLimits

/** Caps how many unfinished collections a profile may follow at once. */
object CollectionFollowRules {
    const val MAX_IN_PROGRESS_COLLECTIONS = FunctionalLimits.MAX_IN_PROGRESS_COLLECTIONS

    fun atFollowLimit(inProgressCount: Int): Boolean =
        inProgressCount >= MAX_IN_PROGRESS_COLLECTIONS
}
