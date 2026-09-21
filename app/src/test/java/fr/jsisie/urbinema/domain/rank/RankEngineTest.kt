package fr.jsisie.urbinema.domain.rank

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.model.TerritoryDimension
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.sqrt

class RankEngineTest {
    private val parameters = RankParameters.v03((1..9).map(Int::toDouble))
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
        assertEquals(1, result.rawRank)
        assertEquals(7, result.displayedRank)
        assertEquals(2, parameters.thresholds.count { 1.0 >= it } + 1)
    }

    @Test
    fun `age adds a modest bonus that grows slowly`() {
        val catalog = listOf(movie("A"))
        val stats = statsEngine.build(1, catalog, parameters.dimensionShares)
        val young = engine.calculate(catalog, stats, ageYears = 20)
        val older = engine.calculate(catalog, stats, ageYears = 60)
        assertEquals(0.0, engine.ageBonus(null), 1e-12)
        assertTrue(young.ageBonus > 0.0)
        assertTrue(older.ageBonus > young.ageBonus)
        assertTrue(older.score - young.score < 0.5)
        assertEquals(older.diversity, young.diversity, 1e-12)
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
    ) = Movie(
        code = EditorialCode(code),
        originalTitle = code,
        releaseYear = 2000,
        durationMinutes = 90,
        format = MovieFormat.FEATURE,
        weight = weight,
        primaryCountry = EditorialCode(country),
        continents = setOf(EditorialCode("EUROPE")),
        directors = setOf(EditorialCode("DIRECTOR")),
    )
}
