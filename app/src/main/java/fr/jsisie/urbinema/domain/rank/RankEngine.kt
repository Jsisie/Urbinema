package fr.jsisie.urbinema.domain.rank

import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.TerritoryDimension
import fr.jsisie.urbinema.domain.model.TerritoryKey
import kotlin.math.ln
import kotlin.math.pow
import kotlin.math.sqrt

data class MovieWeightParameters(
    val base: Double = 1.0,
    val historicalDistance: Double = 2.0,
    val artisticDemand: Double = 2.0,
    val historicalImportance: Double = 2.0,
    val culturalRichness: Double = 3.0,
    val attenuationExponent: Double = 0.5,
) {
    init {
        require(listOf(base, historicalDistance, artisticDemand, historicalImportance, culturalRichness)
            .all { it.isFinite() && it >= 0.0 })
        require(attenuationExponent.isFinite() && attenuationExponent > 0.0)
    }
}

data class DurationWeightParameters(
    val minimumMinutes: Int,
    val minimumFactor: Double,
    val intermediateMinutes: Int,
    val intermediateFactor: Double,
    val fullWeightMinutes: Int,
) {
    init {
        require(minimumMinutes > 0)
        require(intermediateMinutes > minimumMinutes)
        require(fullWeightMinutes > intermediateMinutes)
        require(minimumFactor in 0.0..1.0)
        require(intermediateFactor in minimumFactor..1.0)
    }
}

/**
 * Product anchors for short-film rank contribution.
 *
 * Kept together so duration calibration never requires editing the formula.
 */
object RankDurationDefaults {
    const val MINIMUM_MINUTES = 10
    const val MINIMUM_FACTOR = 0.10
    const val INTERMEDIATE_MINUTES = 20
    const val INTERMEDIATE_FACTOR = 0.20
    const val FULL_WEIGHT_MINUTES = 30

    val parameters = DurationWeightParameters(
        minimumMinutes = MINIMUM_MINUTES,
        minimumFactor = MINIMUM_FACTOR,
        intermediateMinutes = INTERMEDIATE_MINUTES,
        intermediateFactor = INTERMEDIATE_FACTOR,
        fullWeightMinutes = FULL_WEIGHT_MINUTES,
    )
}

data class RankParameters(
    val movieWeights: MovieWeightParameters = MovieWeightParameters(),
    val durationWeights: DurationWeightParameters = RankDurationDefaults.parameters,
    val dimensionShares: Map<TerritoryDimension, Double>,
    val volumeLambda: Double = 1.02,
    val volumeScale: Double = 25.0,
    val diversityLambda: Double = 6.0,
    val diversityExponent: Double = 1.2,
    val depthLambda: Double = 1.2,
    val thresholds: List<Double>,
) {
    init {
        require(dimensionShares.keys == TerritoryDimension.entries.toSet()) {
            "Every rank dimension must have a target share"
        }
        require(dimensionShares.values.all { it.isFinite() && it > 0.0 })
        require(kotlin.math.abs(dimensionShares.values.sum() - 1.0) < 1e-9) {
            "Dimension shares must sum to 1"
        }
        require(listOf(volumeLambda, volumeScale, diversityLambda, diversityExponent, depthLambda)
            .all { it.isFinite() && it > 0.0 })
        require(volumeLambda < diversityLambda && volumeLambda < depthLambda) {
            "Volume must weigh less than diversity and depth"
        }
        require(thresholds.size == 9 && thresholds.all { it.isFinite() } &&
            thresholds.zipWithNext().all { (a, b) -> a < b }) {
            "Exactly nine strictly increasing rank thresholds are required"
        }
    }

    companion object {
        /**
         * Creates the smoothed v0.3.1 configuration while requiring the
         * product thresholds that remain independently adjustable.
         */
        fun v031(thresholds: List<Double>): RankParameters = RankParameters(
            dimensionShares = mapOf(
                TerritoryDimension.CINEMA_CHARACTERISTIC to 0.25,
                TerritoryDimension.DIRECTOR to 0.20,
                TerritoryDimension.COUNTRY to 0.18,
                TerritoryDimension.DECADE to 0.15,
                TerritoryDimension.CONTINENT to 0.07,
                TerritoryDimension.ERA to 0.05,
                TerritoryDimension.GENRE to 0.05,
                TerritoryDimension.FORM to 0.05,
            ),
            thresholds = thresholds,
        )
    }
}

data class TerritoryReference(val rarity: Double, val weight: Double) {
    init {
        require(rarity.isFinite() && rarity > 0.0)
        require(weight.isFinite() && weight > 0.0)
    }
}

data class CatalogRankStats(
    val version: Long,
    val references: Map<TerritoryKey, TerritoryReference>,
)

/** Builds catalog-relative rarity values while preserving both historical ratchets. */
class CatalogRankStatsEngine {
    /**
     * Computes Q and dimension weights for [catalog], retaining the greatest
     * historical value for every territory from [previous].
     */
    fun build(
        version: Long,
        catalog: Collection<Movie>,
        dimensionShares: Map<TerritoryDimension, Double>,
        previous: CatalogRankStats? = null,
    ): CatalogRankStats {
        require(version >= 0)
        require(previous == null || version > previous.version) { "Catalog versions must increase" }
        require(catalog.map { it.code }.distinct().size == catalog.size) { "Movie codes must be unique" }
        require(catalog.isNotEmpty()) { "Rarity is undefined for an empty catalog" }

        val counts = catalog.flatMap { it.rankTerritories() }.groupingBy { it }.eachCount()
        val references = mutableMapOf<TerritoryKey, TerritoryReference>()
        TerritoryDimension.entries.forEach { dimension ->
            val dimensionCounts = counts.filterKeys { it.dimension == dimension }
            if (dimensionCounts.isEmpty()) return@forEach
            val inverseFrequencies = dimensionCounts.mapValues { (_, count) -> catalog.size.toDouble() / count }
            val mean = inverseFrequencies.values.average()
            val rarities = inverseFrequencies.mapValues { (key, inverse) ->
                maxOf(sqrt(inverse / mean), previous?.references?.get(key)?.rarity ?: 0.0)
            }
            val currentWeight = requireNotNull(dimensionShares[dimension]) / rarities.values.sum()
            rarities.forEach { (key, rarity) ->
                references[key] = TerritoryReference(
                    rarity = rarity,
                    weight = maxOf(currentWeight, previous?.references?.get(key)?.weight ?: 0.0),
                )
            }
        }
        return CatalogRankStats(version, references)
    }
}

data class RankResult(
    val rawMovieCount: Int,
    val weightedVolume: Double,
    val rawDiversity: Double,
    val diversity: Double,
    val diversityCapacity: Double,
    val depth: Double,
    val score: Double,
    val rawRank: Int,
    val displayedRank: Int,
)

/** Deterministic implementation of Urbinema rank formula v0.3.1. */
class RankEngine(private val parameters: RankParameters) {
    fun intrinsicWeight(movie: Movie): Double {
        val p = parameters.movieWeights
        val c = movie.weight
        return p.base +
            p.historicalDistance * c.historicalDistance +
            p.artisticDemand * c.artisticDemand +
            p.historicalImportance * c.historicalImportance +
            p.culturalRichness * c.culturalRichness
    }

    /** Calculates intrinsic and attenuated film weight from H/A/R/C. */
    fun attenuatedWeight(movie: Movie): Double {
        return intrinsicWeight(movie).pow(parameters.movieWeights.attenuationExponent)
    }

    /**
     * Applies the smoothed formula v0.3.1:
     * `S = 1.02·ln(1+Vw/25) + 6·D_l + 1.2·ln(1+P)`.
     *
     * - Vw is the sum of attenuated film weights (H/A/R/C).
     * - Every film is multiplied by its duration factor on all three axes.
     * - D sums rarity×weight over distinct territories visited.
     * - D_l = D_max·(D/D_max)^1.2 delays the initial diversity windfall
     *   while preserving the value of complete catalogue coverage.
     * - P rewards watching the same territory more than once (sqrt of extras).
     */
    fun calculate(
        validatedMovies: Collection<Movie>,
        catalogStats: CatalogRankStats,
        previousDisplayedRank: Int = 1,
    ): RankResult {
        require(previousDisplayedRank in 1..10)
        require(validatedMovies.map { it.code }.distinct().size == validatedMovies.size) {
            "A movie can only be validated once"
        }
        val exposures = mutableMapOf<TerritoryKey, Double>()
        validatedMovies.forEach { movie ->
            val contribution = durationFactor(movie.durationMinutes)
            movie.rankTerritories().forEach { key ->
                exposures[key] = exposures.getOrDefault(key, 0.0) + contribution
            }
        }
        exposures.keys.forEach { require(it in catalogStats.references) { "Unknown catalog territory: $it" } }
        val weightedVolume = validatedMovies.sumOf { movie ->
            attenuatedWeight(movie) * durationFactor(movie.durationMinutes)
        }
        val rawDiversity = exposures.entries.sumOf { (key, exposure) ->
            catalogStats.references.getValue(key).let { it.weight * it.rarity } *
                exposure.coerceAtMost(1.0)
        }
        val diversityCapacity = catalogStats.references.values.sumOf { it.weight * it.rarity }
        val diversity = smoothedDiversity(rawDiversity, diversityCapacity)
        val depth = exposures.entries.sumOf { (key, exposure) ->
            catalogStats.references.getValue(key).let { it.weight * it.rarity } *
                sqrt(maxOf(0.0, exposure - 1.0))
        }
        val score = volumeScore(weightedVolume) +
            parameters.diversityLambda * diversity +
            parameters.depthLambda * ln(1.0 + depth)
        val rawRank = parameters.thresholds.count { score >= it } + 1
        return RankResult(
            rawMovieCount = validatedMovies.size,
            weightedVolume = weightedVolume,
            rawDiversity = rawDiversity,
            diversity = diversity,
            diversityCapacity = diversityCapacity,
            depth = depth,
            score = score,
            rawRank = rawRank,
            displayedRank = maxOf(rawRank, previousDisplayedRank),
        )
    }

    /** Shifted logarithm: its initial slope is finite instead of maximal. */
    fun volumeScore(weightedVolume: Double): Double {
        require(weightedVolume.isFinite() && weightedVolume >= 0.0)
        return parameters.volumeLambda * ln(1.0 + weightedVolume / parameters.volumeScale)
    }

    /**
     * Duration contribution shared by volume, diversity and depth.
     *
     * Anchors: <=10 min = 0.10, 15 = 0.15, 20 = 0.20, >=30 = 1.00.
     * Values between anchors are linearly interpolated.
     */
    fun durationFactor(durationMinutes: Int): Double {
        require(durationMinutes >= 0)
        val p = parameters.durationWeights
        return when {
            durationMinutes <= p.minimumMinutes -> p.minimumFactor
            durationMinutes <= p.intermediateMinutes -> interpolate(
                durationMinutes,
                p.minimumMinutes,
                p.intermediateMinutes,
                p.minimumFactor,
                p.intermediateFactor,
            )
            durationMinutes < p.fullWeightMinutes -> interpolate(
                durationMinutes,
                p.intermediateMinutes,
                p.fullWeightMinutes,
                p.intermediateFactor,
                1.0,
            )
            else -> 1.0
        }
    }

    /**
     * Progressive diversity, normalized so complete coverage keeps exactly
     * the same value as before smoothing.
     */
    fun smoothedDiversity(rawDiversity: Double, capacity: Double): Double {
        require(rawDiversity.isFinite() && rawDiversity >= 0.0)
        require(capacity.isFinite() && capacity >= 0.0)
        if (capacity == 0.0) return 0.0
        val fraction = (rawDiversity / capacity).coerceIn(0.0, 1.0)
        return capacity * fraction.pow(parameters.diversityExponent)
    }

    private fun interpolate(
        value: Int,
        start: Int,
        end: Int,
        startFactor: Double,
        endFactor: Double,
    ): Double {
        val fraction = (value - start).toDouble() / (end - start).toDouble()
        return startFactor + fraction * (endFactor - startFactor)
    }

}

/** Calibration selected from the 1,613-film catalogue playtest. */
object RankDefaults {
    const val CONFIG_CODE = "RANK_V031_DURATION_WEIGHTED"

    val thresholds: List<Double> = listOf(
        1.80,
        3.00,
        4.20,
        5.40,
        6.60,
        7.80,
        9.20,
        10.80,
        12.50,
    )

    val parameters: RankParameters = RankParameters.v031(thresholds)
}
