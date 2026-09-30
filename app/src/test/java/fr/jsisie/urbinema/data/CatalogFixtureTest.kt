package fr.jsisie.urbinema.data

import fr.jsisie.urbinema.data.importer.CatalogPack
import fr.jsisie.urbinema.data.importer.CatalogValidator
import fr.jsisie.urbinema.data.importer.MovieImport
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.quest.DefaultQuestRules
import fr.jsisie.urbinema.domain.rank.CatalogRankStatsEngine
import fr.jsisie.urbinema.domain.rank.RankDefaults
import fr.jsisie.urbinema.domain.rank.RankEngine
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
        assertEquals(42, pack.version)
        assertEquals(1613, pack.movies.size)
        assertEquals("Voir 50 films d'horreur.", pack.badges.first { it.code == "032" }.description)
        assertEquals(
            "Les Conséquences du féminisme",
            pack.movies.first { it.code == "LES_CONSEQUENCES_DU_FEMINISME_1906" }.originalTitle,
        )
        assertTrue(
            listOf(
                "LES_CONSEQUENCES_DU_FEMINISME_1906",
                "BOUDU_SAVED_FROM_DROWNING_1932",
                "SENSO_1954",
                "ELEVATOR_TO_THE_GALLOWS_1958",
                "LE_TROU_1960",
                "JE_SUIS_CUBA_1964",
                "MASCULIN_FEMININ_1966",
                "THE_WILD_CHILD_1970",
                "THE_RED_CIRCLE_1970",
            ).all { code -> pack.movies.first { it.code == code }.frenchTitle == null },
        )
        assertEquals("Z", pack.movies.first { it.code == "Z_1969" }.frenchTitle)
        assertEquals("Le Jupon rouge", pack.movies.first { it.code == "ROUGE_1987" }.originalTitle)
        assertEquals(null, pack.movies.first { it.code == "ROUGE_1987" }.frenchTitle)
        assertEquals(
            "Vérités et mensonges",
            pack.movies.first { it.code == "VERITES_ET_MENSONGES_1973" }.originalTitle,
        )
        assertTrue(
            listOf(
                "PHANTOM_OF_THE_PARADISE_1974",
                "SUSPIRIA_1977",
                "ROBOCOP_1987",
                "RESERVOIR_DOGS_1992",
                "JURASSIC_PARK_1993",
                "TOY_STORY_1995",
                "THE_BIG_LEBOWSKI_1998",
                "CODE_UNKNOWN_2000",
                "THE_DARK_KNIGHT_2008",
                "VERITES_ET_MENSONGES_1973",
                "JE_TU_IL_ELLE_1974",
            ).all { code -> pack.movies.first { it.code == code }.frenchTitle == null },
        )
        assertTrue(
            listOf("BEAU_TRAVAIL_1999", "35_SHOTS_OF_RUM_2008", "TROUBLE_EVERY_DAY_2001", "CHOCOLAT_1988", "WHITE_MATERIAL_2009")
                .all { code ->
                    pack.movies.first { it.code == code }.directors.single().code == "CLAIRE_DENIS"
                },
        )
        assertEquals(6, pack.movies.first { it.code == "VINGT_ANS_APRES_1984" }.directors.size)
        val parcours = pack.paths.first { it.code == "PARCOURS_001" }
        assertEquals(11, parcours.steps.size)
        assertEquals("CINEMA_MUET_MOUVEMENT", parcours.steps.first().characteristicCode)
        assertEquals("CINEMA_CONTEMPORAIN_MOUVEMENT", parcours.steps.last().characteristicCode)
        assertTrue(parcours.steps.all { it.movies.size == 4 })
        assertEquals("LA_SOURIANTE_MADAME_BEUDET_1923", parcours.steps[1].movies.first())
        assertTrue(pack.movies.any { it.code == "LA_COQUILLE_ET_LE_CLERGYMAN_1928" })
        assertTrue(pack.directors.any { it.code == "SHOHEI_IMAMURA" })
        assertTrue(pack.directors.none { it.code == "DIRECTOR" })
        assertEquals(
            "MIKIO_NARUSE",
            pack.movies.first { it.code == "NUAGES_FLOTTANTS_1955" }.directors.first().code,
        )
        assertTrue(
            pack.movies.first { it.code == "THE_LEGEND_OF_SURAM_FORTRESS_1985" }
                .directors.none { it.code == "DIRECTOR" },
        )
        val premiersTemps = pack.collections.first { it.code == "COLLECTION_027" }
        assertEquals("Cinéma des premiers temps", premiersTemps.name)
        assertEquals("GATEWAY", premiersTemps.track)
        assertEquals(17, premiersTemps.movies.size)
        assertEquals(
            "GEORGE_ALBERT_SMITH",
            pack.movies.first { it.code == "LA_LOUPE_DE_GRAND_MAMAN_1900" }.directors.first().code,
        )
        assertTrue(pack.movies.none { it.code == "LA_FEE_AUX_CHOUX_1900" })
        assertEquals(
            "ALICE_GUY",
            pack.movies.first { it.code == "LA_FEE_AUX_CHOUX_1896" }.directors.first().code,
        )
        assertTrue(premiersTemps.movies.any { it.code == "LA_FEE_AUX_CHOUX_1896" })
        assertEquals("LA_FEE_AUX_CHOUX_1896", pack.movieAliases.first { it.from == "LA_FEE_AUX_CHOUX_1900" }.to)
        assertTrue(pack.movies.none { it.code == "OLDBOY_2003" })
        assertTrue(pack.movies.any { it.code == "OLD_BOY_2003" && it.countries.any { country -> country.isPrimary } })
        assertTrue(pack.movies.any { it.code == "LA_CONDITION_DE_L_HOMME_2_1959" })
        assertEquals("OLD_BOY_2003", pack.movieAliases.first { it.from == "OLDBOY_2003" }.to)
        assertTrue(pack.movies.all { movie -> movie.countries.any { it.isPrimary } })
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
        assertEquals(38, pack.badges.size)
        assertEquals(19, pack.quests.count { it.difficulty == "BRONZE" })
        assertEquals(20, pack.quests.count { it.difficulty == "SILVER" })
        assertEquals(20, pack.quests.count { it.difficulty == "GOLD" })
        assertEquals(59, pack.quests.size)
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

    @Test
    fun smoothedRankFormulaKeepsInitiationOpeningProgressive() {
        val pack = packagedCatalog()
        val continentsByCountry = pack.countries.associate { country ->
            country.code to country.continentCodes.toSet()
        }
        val movies = pack.movies.map { imported ->
            imported.toDomainMovie(continentsByCountry).copy(
                era = pack.eras
                    .filter { imported.releaseYear in it.startYear..it.endYear }
                    .minByOrNull { it.endYear - it.startYear }
                    ?.code
                    ?.let(::EditorialCode),
            )
        }
        val byCode = movies.associateBy { it.code.value }
        val initiation = listOf(
            "LE_PARRAIN_1972",
            "LES_DENTS_DE_LA_MER_1975",
            "LA_GUERRE_DES_ETOILES_1977",
            "FORREST_GUMP_1994",
            "PULP_FICTION_1994",
            "LE_ROI_LION_1994",
            "SEVEN_1995",
            "TITANIC_1997",
            "LE_VOYAGE_DE_CHIHIRO_2001",
            "AVATAR_2009",
        ).map(byCode::getValue)
        val engine = RankEngine(RankDefaults.parameters)
        val stats = CatalogRankStatsEngine().build(
            version = pack.version.toLong(),
            catalog = movies,
            dimensionShares = RankDefaults.parameters.dimensionShares,
        )
        var previous = 0.0
        val gains = initiation.indices.map { index ->
            val score = engine.calculate(initiation.take(index + 1), stats).score
            ((score - previous) * 1_000.0).also { previous = score }
        }

        assertTrue("Unexpected Initiation gains: $gains", gains[0] in 130.0..210.0)
        assertTrue("Unexpected Initiation gains: $gains", gains[1] in 90.0..165.0)
        assertTrue("Unexpected Initiation gains: $gains", gains[2] in 70.0..140.0)
        assertTrue("Unexpected Initiation gains: $gains", gains[9] in 40.0..90.0)
        assertTrue("Opening cliff remains too steep: $gains", gains[0] / gains[9] < 3.5)
    }

    @Test
    fun oneMinuteEarlyCinemaFilmDoesNotProduceFeatureLengthRankGain() {
        val pack = packagedCatalog()
        val continentsByCountry = pack.countries.associate { country ->
            country.code to country.continentCodes.toSet()
        }
        val movies = pack.movies.map { imported ->
            imported.toDomainMovie(continentsByCountry).copy(
                era = pack.eras
                    .filter { imported.releaseYear in it.startYear..it.endYear }
                    .minByOrNull { it.endYear - it.startYear }
                    ?.code
                    ?.let(::EditorialCode),
            )
        }
        val byCode = movies.associateBy { it.code.value }
        val sequenceCodes = buildList {
            addAll(pack.collections.first { it.code == "COLLECTION_INITIATION" }.movies.map { it.code })
            addAll(pack.collections.first { it.code == "COLLECTION_015" }.movies.map { it.code })
            addAll(pack.collections.first { it.code == "COLLECTION_027" }.movies.take(12).map { it.code })
        }.distinct()
        assertEquals("LA_LOUPE_DE_GRAND_MAMAN_1900", sequenceCodes.last())
        val sequence = sequenceCodes.map(byCode::getValue)
        val engine = RankEngine(RankDefaults.parameters)
        val stats = CatalogRankStatsEngine().build(
            version = pack.version.toLong(),
            catalog = movies,
            dimensionShares = RankDefaults.parameters.dimensionShares,
        )
        val before = engine.calculate(sequence.dropLast(1), stats).score
        val after = engine.calculate(sequence, stats).score
        val gain = (after - before) * 1_000.0

        assertTrue("One-minute film still grants $gain points", gain in 0.0..50.0)
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
