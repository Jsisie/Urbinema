package fr.jsisie.urbinema.domain.collection

import fr.jsisie.urbinema.domain.model.CollectionDefinition
import fr.jsisie.urbinema.domain.model.EditorialCode

enum class CollectionMilestone(val minimumFraction: Double) {
    NOT_EXPLORED(0.0),
    DISCOVERED(0.25),
    EXPLORING(0.50),
    ADVANCED(0.75),
    COMPLETED(1.0),
}

data class CollectionProgress(
    val collectionCode: EditorialCode,
    val watchedCount: Int,
    val totalCount: Int,
    val fraction: Double,
    val percentage: Int,
    val milestone: CollectionMilestone,
    val completed: Boolean,
)

/** Recalculates percentage milestones for collections of arbitrary size. */
class CollectionProgressEngine {
    /**
     * Calculates current progress from movie identities; an empty editorial
     * collection is deliberately not considered completed.
     */
    fun calculate(
        collection: CollectionDefinition,
        validatedMovieCodes: Set<EditorialCode>,
    ): CollectionProgress {
        val watched = collection.movieCodes.count { it in validatedMovieCodes }
        val total = collection.movieCodes.size
        val fraction = if (total == 0) 0.0 else watched.toDouble() / total
        val milestone = CollectionMilestone.entries.last { fraction >= it.minimumFraction }
        return CollectionProgress(
            collectionCode = collection.code,
            watchedCount = watched,
            totalCount = total,
            fraction = fraction,
            percentage = (fraction * 100).toInt(),
            milestone = milestone,
            completed = total > 0 && watched == total,
        )
    }
}
