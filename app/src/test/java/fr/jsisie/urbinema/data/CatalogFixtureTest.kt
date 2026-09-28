package fr.jsisie.urbinema.data

import fr.jsisie.urbinema.data.importer.CatalogPack
import fr.jsisie.urbinema.data.importer.CatalogValidator
import fr.jsisie.urbinema.data.importer.MovieImport
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.quest.DefaultQuestRules
import java.io.File
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CatalogFixtureTest {
    @Test
    fun packagedCatalog_isValidAndContainsTheV1RuleCatalogs() {
        val pack = packagedCatalog()
        val report = CatalogValidator().validate(pack)

        assertTrue(report.errors.joinToString { "${it.path}: ${it.message}" }, report.isValid)
        assertEquals(19, pack.version)
        assertTrue(pack.movies.size >= 1400)
        assertTrue(pack.collections.size >= 18)
        assertEquals("CLUB", pack.collections.first { it.code == "COLLECTION_005" }.track)
        assertEquals("OFFSCREEN", pack.collections.first { it.code == "COLLECTION_010" }.track)
        assertEquals("DARKROOM", pack.collections.first { it.code == "COLLECTION_012" }.track)
        assertEquals("GATEWAY", pack.collections.first { it.code == "COLLECTION_015" }.track)
        assertEquals("CINEMATHEQUE", pack.collections.first { it.code == "COLLECTION_016" }.track)
        assertEquals("DARKROOM", pack.collections.first { it.code == "COLLECTION_017" }.track)
        assertEquals("Âge d'or japonais", pack.collections.first { it.code == "COLLECTION_003" }.name)
        assertEquals(10, pack.rankings.size)
        assertTrue(pack.rankings.all { !it.longDescription.isNullOrBlank() })
        assertEquals(32, pack.badges.size)
        assertEquals(16, pack.quests.count { it.difficulty == "BRONZE" })
        assertEquals(17, pack.quests.count { it.difficulty == "SILVER" })
        assertEquals(17, pack.quests.count { it.difficulty == "GOLD" })
        assertEquals(50, pack.quests.size)
        assertTrue(pack.movies.all { movie -> movie.countries.count { it.isPrimary } == 1 })
        assertTrue(pack.movies.all { it.countries.size in 1..2 })
        val usedCountries = pack.movies.flatMap { movie -> movie.countries.map { it.code } }.toSet()
        assertEquals(usedCountries, pack.countries.map { it.code }.toSet())
        val nouvelleVague = pack.movies.count { "NOUVELLE_VAGUE_FRANCAISE" in it.characteristicCodes }
        assertTrue("Nouvelle Vague trop large: $nouvelleVague", nouvelleVague in 20..50)
        val moviesByCode = pack.movies.associateBy { it.code }
        pack.collections.forEach { collection ->
            val years = collection.movies.map { moviesByCode.getValue(it.code).releaseYear }
            assertTrue(
                "${collection.code} films not year-asc: $years",
                years == years.sorted(),
            )
        }
    }

    @Test
    fun everyPackQuestIsCompletableOnAFreshCatalog() {
        val pack = packagedCatalog()
        val registry = DefaultQuestRules.registry()
        val continentsByCountry = pack.countries.associate { country ->
            country.code to country.continentCodes.toSet()
        }
        val movies = pack.movies.map { it.toDomainMovie(continentsByCountry) }
        pack.quests.forEach { quest ->
            val remaining = registry.require(EditorialCode(quest.ruleCode))
                .remainingCapacity(movies)
            assertTrue(
                "${quest.code} remaining=$remaining target=${quest.targetCount}",
                remaining >= quest.targetCount,
            )
        }
    }

    private fun packagedCatalog(): CatalogPack {
        val file = File("src/main/assets/catalog/catalog.json")
        assertTrue("Missing packaged catalogue at ${file.absolutePath}", file.isFile)
        return Json { ignoreUnknownKeys = true }.decodeFromString<CatalogPack>(file.readText())
    }

    private fun MovieImport.toDomainMovie(
        continentsByCountry: Map<String, Set<String>>,
    ): Movie {
        val primary = countries.first { it.isPrimary }.code
        return Movie(
            code = EditorialCode(code),
            originalTitle = originalTitle,
            frenchTitle = frenchTitle,
            synopsis = synopsis,
            releaseYear = releaseYear,
            durationMinutes = durationMinutes,
            format = MovieFormat.valueOf(format),
            weight = MovieWeightComponents(
                historicalDistance = historicalDistance.coerceIn(0.0, 1.0),
                artisticDemand = artisticDemand.coerceIn(0.0, 1.0),
                historicalImportance = historicalRichness.coerceIn(0.0, 1.0),
                culturalRichness = culturalRichness.coerceIn(0.0, 1.0),
            ),
            primaryCountry = EditorialCode(primary),
            countries = countries.mapTo(linkedSetOf()) { EditorialCode(it.code) },
            continents = countries.flatMap { continentsByCountry[it.code].orEmpty() }
                .mapTo(linkedSetOf(), ::EditorialCode),
            directors = directors.mapTo(linkedSetOf()) { EditorialCode(it.code) },
            genres = genreCodes.mapTo(linkedSetOf(), ::EditorialCode),
            characteristics = characteristicCodes.mapTo(linkedSetOf(), ::EditorialCode),
            isSilent = isSilent,
            isBlackAndWhite = isBlackAndWhite,
            isExperimental = isExperimental,
        )
    }
}
