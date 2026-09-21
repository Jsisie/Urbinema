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

data class RankParameters(
    val movieWeights: MovieWeightParameters = MovieWeightParameters(),
    val dimensionShares: Map<TerritoryDimension, Double>,
    val volumeLambda: Double = 0.6,
    val diversityLambda: Double = 6.0,
    val depthLambda: Double = 1.2,
    val ageLambda: Double = 0.35,
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
        require(listOf(volumeLambda, diversityLambda, depthLambda).all { it.isFinite() && it > 0.0 })
        require(ageLambda.isFinite() && ageLambda >= 0.0)
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
         * Creates the v0.3 starting configuration while requiring the product
         * thresholds that the specification deliberately leaves uncalibrated.
         */
        fun v03(thresholds: List<Double>): RankParameters = RankParameters(
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
    val diversity: Double,
    val depth: Double,
    val ageBonus: Double,
    val score: Double,
    val rawRank: Int,
    val displayedRank: Int,
)

/** Deterministic implementation of Urbinema rank formula v0.3. */
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
     * Applies formula v0.3:
     * `S = 0.6·ln(1+Vw) + 6·D + 1.2·ln(1+P) + S_A`.
     *
     * - Vw is the sum of attenuated film weights (H/A/R/C).
     * - D sums rarity×weight over distinct territories visited.
     * - P rewards watching the same territory more than once (sqrt of extras).
     * - S_A is the modest age bonus; the displayed rank never goes down.
     */
    fun calculate(
        validatedMovies: Collection<Movie>,
        catalogStats: CatalogRankStats,
        previousDisplayedRank: Int = 1,
        ageYears: Int? = null,
    ): RankResult {
        require(previousDisplayedRank in 1..10)
        require(validatedMovies.map { it.code }.distinct().size == validatedMovies.size) {
            "A movie can only be validated once"
        }
        val occurrences = validatedMovies.flatMap { it.rankTerritories() }.groupingBy { it }.eachCount()
        occurrences.keys.forEach { require(it in catalogStats.references) { "Unknown catalog territory: $it" } }
        val weightedVolume = validatedMovies.sumOf(::attenuatedWeight)
        val diversity = occurrences.keys.sumOf { key ->
            catalogStats.references.getValue(key).let { it.weight * it.rarity }
        }
        val depth = occurrences.entries.sumOf { (key, count) ->
            catalogStats.references.getValue(key).let { it.weight * it.rarity } *
                sqrt(maxOf(0, count - 1).toDouble())
        }
        val lifetimeBonus = ageBonus(ageYears)
        val score = parameters.volumeLambda * ln(1.0 + weightedVolume) +
            parameters.diversityLambda * diversity +
            parameters.depthLambda * ln(1.0 + depth) +
            lifetimeBonus
        val rawRank = parameters.thresholds.count { score >= it } + 1
        return RankResult(
            rawMovieCount = validatedMovies.size,
            weightedVolume = weightedVolume,
            diversity = diversity,
            depth = depth,
            ageBonus = lifetimeBonus,
            score = score,
            rawRank = rawRank,
            displayedRank = maxOf(rawRank, previousDisplayedRank),
        )
    }

    /**
     * Modest lifetime bonus: an older viewer has simply had more years of cinema.
     * It must never dominate diversity or depth.
     *
     * S_A = λ_A * ln(1 + max(0, age - 16) / 20)
     * λ_A = 0.35 → ~0.06 at 20, ~0.28 at 40, ~0.41 at 60.
     */
    fun ageBonus(ageYears: Int?): Double {
        if (ageYears == null) return 0.0
        val clamped = ageYears.coerceIn(8, 120)
        val yearsPastYouth = maxOf(0.0, (clamped - 16.0) / 20.0)
        return parameters.ageLambda * ln(1.0 + yearsPastYouth)
    }
}

/**
 * Initial calibration used until real catalogue simulations are available.
 *
 * Keeping it in one object makes product tuning a data change instead of a
 * rewrite of the calculation.
 */
object RankDefaults {
    val thresholds: List<Double> = listOf(
        1.20,
        2.20,
        3.20,
        4.50,
        5.80,
        7.20,
        8.80,
        10.50,
        12.50,
    )

    val parameters: RankParameters = RankParameters.v03(thresholds)
}
