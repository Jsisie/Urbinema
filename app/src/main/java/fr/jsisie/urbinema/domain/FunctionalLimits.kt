package fr.jsisie.urbinema.domain

/**
 * Named product numbers (Shift+Ctrl+F). Keep UI copy and tests on these,
 * not on raw literals scattered in screens.
 */
object FunctionalLimits {
    /** Followed collections that are not yet 100 %. */
    const val MAX_IN_PROGRESS_COLLECTIONS = 10

    const val MIN_USER_AGE = 8
    const val MAX_USER_AGE = 120

    /** Coalesce Room-driven UI rebuilds (ms). */
    const val UI_REFRESH_DEBOUNCE_MS = 48L
}
