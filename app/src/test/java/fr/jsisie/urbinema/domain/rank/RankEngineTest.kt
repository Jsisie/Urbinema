package fr.jsisie.urbinema.domain.rank

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.model.TerritoryDimension
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.ln
import kotlin.math.sqrt

class RankEngineTest {
    private val parameters = RankParameters.v031((1..9).map(Int::toDouble))
    private val engine = RankEngine(parameters)
    private val statsEngine = CatalogRankStatsEngine()

    @Test
    fun `film weight has exact v03 endpoints`() {
        assertEquals(1.0, engine.attenuatedWeight(movie("MIN")), 1e-12)
        assertEquals(
            sqrt(10.0),
            engine.attenuatedWeight(movie("MAX", MovieWeightComponents(1.0, 1.0, 1.0, 1.0))),
            1e-12,
        )
    }

    @Test
    fun `first territory occurrence adds diversity but no depth`() {
        val catalog = listOf(movie("A"))
        val result = engine.calculate(catalog, statsEngine.build(1, catalog, parameters.dimensionShares))
        assertTrue(result.diversity > 0.0)
        assertEquals(0.0, result.depth, 1e-12)
    }

    @Test
    fun `second occurrence adds depth without changing diversity`() {
        val one = movie("A")
        val two = movie("B")
        val catalog = listOf(one, two)
        val stats = statsEngine.build(1, catalog, parameters.dimensionShares)
        val first = engine.calculate(listOf(one), stats)
        val second = engine.calculate(catalog, stats)
        assertEquals(first.diversity, second.diversity, 1e-12)
        assertTrue(second.depth > first.depth)
    }

    @Test
    fun `shifted volume logarithm smooths the first films`() {
        val firstGain = engine.volumeScore(1.0)
        val secondGain = engine.volumeScore(2.0) - firstGain
        val tenthGain = engine.volumeScore(10.0) - engine.volumeScore(9.0)

        assertTrue(firstGain > secondGain)
        assertTrue(secondGain > tenthGain)
        assertTrue(firstGain / tenthGain < 1.4)
    }

    @Test
    fun `shifted volume catches up with legacy volume near eleven hundred films`() {
        val referenceWeightedVolume = 2_500.0
        val legacy = 0.6 * ln(1.0 + referenceWeightedVolume)
        val smoothed = engine.volumeScore(referenceWeightedVolume)

        assertEquals(legacy, smoothed, 0.03)
    }

    @Test
    fun `progressive diversity softens the start and preserves full coverage`() {
        val capacity = 1.0
        val initial = engine.smoothedDiversity(0.1, capacity)

        assertTrue(initial in 0.0..0.1)
        assertEquals(capacity, engine.smoothedDiversity(capacity, capacity), 1e-12)
    }

    @Test
    fun `duration factor follows the agreed anchors`() {
        assertEquals(0.10, engine.durationFactor(1), 1e-12)
        assertEquals(0.10, engine.durationFactor(10), 1e-12)
        assertEquals(0.15, engine.durationFactor(15), 1e-12)
        assertEquals(0.20, engine.durationFactor(20), 1e-12)
        assertEquals(0.60, engine.durationFactor(25), 1e-12)
        assertEquals(1.00, engine.durationFactor(30), 1e-12)
        assertEquals(1.00, engine.durationFactor(180), 1e-12)
    }

    @Test
    fun `ten one minute films equal one full territory exposure`() {
        val catalog = (1..11).map { movie("SHORT_$it", durationMinutes = 1) }
        val stats = statsEngine.build(1, catalog, parameters.dimensionShares)
        val one = engine.calculate(catalog.take(1), stats)
        val ten = engine.calculate(catalog.take(10), stats)
        val eleven = engine.calculate(catalog, stats)

        assertEquals(engine.attenuatedWeight(catalog.first()) * 0.10, one.weightedVolume, 1e-12)
        assertEquals(one.diversityCapacity * 0.10, one.rawDiversity, 1e-12)
        assertEquals(ten.diversityCapacity, ten.rawDiversity, 1e-12)
        assertEquals(0.0, ten.depth, 1e-12)
        assertTrue(eleven.depth > 0.0)
    }

    @Test
    fun `rarity is normalized inside its dimension`() {
        val rare = movie("RARE", country = "JAPAN")
        val common1 = movie("COMMON_1", country = "FRANCE")
        val common2 = movie("COMMON_2", country = "FRANCE")
        val stats = statsEngine.build(1, listOf(rare, common1, common2), parameters.dimensionShares)
        val japan = stats.references.entries.single {
            it.key.dimension == TerritoryDimension.COUNTRY && it.key.code == EditorialCode("JAPAN")
        }.value
        val france = stats.references.entries.single {
            it.key.dimension == TerritoryDimension.COUNTRY && it.key.code == EditorialCode("FRANCE")
        }.value
        assertTrue(japan.rarity > france.rarity)
    }

    @Test
    fun `catalog rarity and weight ratchets never decrease`() {
        val firstCatalog = listOf(movie("A", country = "JAPAN"), movie("B", country = "FRANCE"))
        val first = statsEngine.build(1, firstCatalog, parameters.dimensionShares)
        val secondCatalog = firstCatalog + movie("C", country = "JAPAN")
        val second = statsEngine.build(2, secondCatalog, parameters.dimensionShares, first)
        first.references.forEach { (key, old) ->
            second.references[key]?.let { new ->
                assertTrue(new.rarity >= old.rarity)
                assertTrue(new.weight >= old.weight)
            }
        }
    }

    @Test
    fun `displayed rank and threshold boundaries ratchet`() {
        val catalog = listOf(movie("A"))
        val stats = statsEngine.build(1, catalog, parameters.dimensionShares)
        val result = engine.calculate(emptyList(), stats, previousDisplayedRank = 7)
        assertEquals(0.0, result.score, 1e-12)
        assertEquals(1, result.rawRank)
        assertEquals(7, result.displayedRank)
        assertEquals(2, parameters.thresholds.count { 1.0 >= it } + 1)
    }

    @Test
    fun `playtest thresholds slow early ranks without moving rank ten`() {
        assertEquals(
            listOf(1.8, 3.0, 4.2, 5.4, 6.6, 7.8, 9.2, 10.8, 12.5),
            RankDefaults.thresholds,
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun `duplicate validation is rejected`() {
        val film = movie("A")
        val stats = statsEngine.build(1, listOf(film), parameters.dimensionShares)
        engine.calculate(listOf(film, film), stats)
    }

    private fun movie(
        code: String,
        weight: MovieWeightComponents = MovieWeightComponents(0.0, 0.0, 0.0, 0.0),
        country: String = "FRANCE",
        durationMinutes: Int = 90,
    ) = Movie(
        code = EditorialCode(code),
        originalTitle = code,
        releaseYear = 2000,
        durationMinutes = durationMinutes,
        format = MovieFormat.FEATURE,
        weight = weight,
        primaryCountry = EditorialCode(country),
        continents = setOf(EditorialCode("EUROPE")),
        directors = setOf(EditorialCode("DIRECTOR")),
    )
}
