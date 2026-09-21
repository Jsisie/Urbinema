package fr.jsisie.urbinema.data

import android.content.Context
import android.database.sqlite.SQLiteConstraintException
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.importer.CatalogImportResult
import fr.jsisie.urbinema.data.importer.CatalogImporter
import fr.jsisie.urbinema.data.importer.CatalogPack
import fr.jsisie.urbinema.data.importer.ContinentImport
import fr.jsisie.urbinema.data.importer.CountryImport
import fr.jsisie.urbinema.data.importer.DirectorImport
import fr.jsisie.urbinema.data.importer.MovieCountryImport
import fr.jsisie.urbinema.data.importer.MovieDirectorImport
import fr.jsisie.urbinema.data.importer.MovieImport
import java.io.IOException
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class UrbinemaDatabaseTest {
    private lateinit var database: UrbinemaDatabase

    @Before
    fun createDatabase() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(context, UrbinemaDatabase::class.java)
            .addCallback(UrbinemaDatabase.SchemaCallback)
            .allowMainThreadQueries()
            .build()
        database.openHelper.writableDatabase
    }

    @After
    @Throws(IOException::class)
    fun closeDatabase() {
        database.close()
    }

    @Test
    fun foreignKeysRejectUnknownMovieCountryReferences() {
        val error = runCatching {
            database.openHelper.writableDatabase.execSQL(
                "INSERT INTO movies_countries(movieId, countryId, isPrimary) VALUES (999, 999, 1)"
            )
        }.exceptionOrNull()

        assertTrue(error is SQLiteConstraintException)
    }

    @Test
    fun partialIndexAllowsOnlyOnePrimaryCountryPerMovie() = runBlocking {
        val result = CatalogImporter(database).import(validPack())
        assertTrue(result is CatalogImportResult.Success)

        val error = runCatching {
            database.openHelper.writableDatabase.execSQL(
                """UPDATE movies_countries SET isPrimary = 1
                   WHERE countryId = (SELECT countryId FROM countries WHERE code = 'JP')"""
            )
        }.exceptionOrNull()

        assertTrue(error is SQLiteConstraintException)
    }

    @Test
    fun importerRejectsMissingPrimaryWithoutWritingAnything() = runBlocking {
        val invalidMovie = validPack().movies.single().copy(
            countries = listOf(MovieCountryImport("FR", false))
        )
        val result = CatalogImporter(database).import(validPack().copy(movies = listOf(invalidMovie)))

        assertTrue(result is CatalogImportResult.Invalid)
        assertEquals(0, database.catalogImportDao().catalogRowCount())
    }

    @Test
    fun importerMergesANewerPackWithoutChangingExistingMovieIds() = runBlocking {
        val importer = CatalogImporter(database)
        assertTrue(importer.import(validPack()) is CatalogImportResult.Success)
        val originalId = database.catalogDao().movieByCode("MOVIE_1")?.movieId

        val secondResult = importer.import(validPack().copy(version = 2))

        assertTrue(secondResult is CatalogImportResult.Success)
        assertEquals(originalId, database.catalogDao().movieByCode("MOVIE_1")?.movieId)
    }

    @Test
    fun packagedCatalog_importsIntoAnEmptyDatabase() = runBlocking {
        val json = ApplicationProvider.getApplicationContext<Context>()
            .assets.open("catalog/catalog.json")
            .bufferedReader()
            .use { it.readText() }
        val result = CatalogImporter(database).importJson(json)
        assertTrue(
            "Import failed: ${(result as? CatalogImportResult.Failure)?.message} " +
                "${(result as? CatalogImportResult.Failure)?.cause}",
            result is CatalogImportResult.Success,
        )
        assertTrue(database.catalogDao().allMoviesWithRelations().size >= 50)
    }

    private fun validPack() = CatalogPack(
        version = 1,
        generatedAt = "2026-09-16T08:00:00Z",
        countries = listOf(
            CountryImport(code = "FR", name = "France", continentCodes = listOf("EU")),
            CountryImport(code = "JP", name = "Japon", continentCodes = listOf("AS")),
        ),
        continents = listOf(
            ContinentImport(code = "EU", name = "Europe"),
            ContinentImport(code = "AS", name = "Asie"),
        ),
        directors = listOf(
            DirectorImport(code = "DIRECTOR_1", lastName = "Varda", displayName = "Agnès Varda")
        ),
        movies = listOf(
            MovieImport(
                code = "MOVIE_1",
                originalTitle = "Cléo de 5 à 7",
                releaseYear = 1962,
                durationMinutes = 90,
                format = "FEATURE",
                historicalDistance = 0.7,
                artisticDemand = 0.8,
                historicalRichness = 0.9,
                culturalRichness = 0.8,
                countries = listOf(
                    MovieCountryImport("FR", true),
                    MovieCountryImport("JP", false),
                ),
                directors = listOf(MovieDirectorImport("DIRECTOR_1", 0)),
            )
        ),
    )
}
