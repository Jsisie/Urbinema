package fr.jsisie.urbinema.domain.badge

/** At most three earned badges are shown on the profile. */
object ProfileBadges {
    const val MAX_SHOWCASE = 3

    fun parse(stored: String?): List<String> =
        stored?.split(',')
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }
            .orEmpty()

    fun encode(codes: List<String>): String =
        codes.filter { it.isNotBlank() }.take(MAX_SHOWCASE).joinToString(",")

    /**
     * [earnedInOrder] is chronological (first earned first). Custom [stored]
     * codes win when they are still earned; otherwise the first three earned.
     */
    fun resolve(earnedInOrder: List<String>, stored: String?): List<String> {
        val earned = earnedInOrder.toSet()
        val chosen = parse(stored).filter { it in earned }.take(MAX_SHOWCASE)
        if (chosen.isNotEmpty()) return chosen
        return earnedInOrder.take(MAX_SHOWCASE)
    }
}
