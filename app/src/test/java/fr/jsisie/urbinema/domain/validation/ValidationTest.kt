package fr.jsisie.urbinema.domain.validation

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Clock
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset

class ValidationTest {
    private val now = Instant.parse("2026-09-16T10:00:00Z")
    private val clock = Clock.fixed(now, ZoneOffset.UTC)

    @Test
    fun `validator reports all independent structural errors`() {
        val invalid = validMovie().copy(
            originalTitle = " ",
            releaseYear = 2200,
            durationMinutes = 0,
            directors = emptySet(),
        )
        val errors = MovieValidator().validate(invalid, 2026)
        assertEquals(4, errors.size)
        assertTrue(MovieValidationError.BlankOriginalTitle in errors)
        assertTrue(MovieValidationError.ImplausibleReleaseYear in errors)
        assertTrue(MovieValidationError.InvalidDuration in errors)
        assertTrue(MovieValidationError.MissingDirector in errors)
    }

    @Test
    fun `use case rejects future missing and duplicate validations`() = runTest {
        val movie = validMovie()
        val movies = FakeMovieRepository(movie)
        val validations = FakeValidationRepository()
        val useCase = ValidateMovieUseCase(movies, validations, MovieValidator(), clock)
        assertEquals(
            ValidateMovieResult.FutureWatchDate,
            useCase.execute(1, movie.code, LocalDate.of(2026, 9, 17)),
        )
        assertEquals(
            ValidateMovieResult.MovieNotFound,
            useCase.execute(1, EditorialCode("UNKNOWN"), LocalDate.of(2026, 9, 16)),
        )
        assertTrue(useCase.execute(1, movie.code, LocalDate.of(2026, 9, 16)) is ValidateMovieResult.Validated)
        assertEquals(
            ValidateMovieResult.AlreadyValidated,
            useCase.execute(1, movie.code, LocalDate.of(2026, 9, 16)),
        )
    }

    private fun validMovie() = Movie(
        code = EditorialCode("FILM"),
        originalTitle = "Film",
        releaseYear = 2020,
        durationMinutes = 90,
        format = MovieFormat.FEATURE,
        weight = MovieWeightComponents(0.0, 0.0, 0.0, 0.0),
        primaryCountry = EditorialCode("FRANCE"),
        continents = setOf(EditorialCode("EUROPE")),
        directors = setOf(EditorialCode("DIRECTOR")),
    )

    private class FakeMovieRepository(private val movie: Movie) : MovieRepository {
        override suspend fun findActiveByCode(code: EditorialCode): Movie? =
            movie.takeIf { it.code == code }
    }

    private class FakeValidationRepository : ValidationRepository {
        private val keys = mutableSetOf<Pair<Long, EditorialCode>>()
        override suspend fun isValidated(userId: Long, movieCode: EditorialCode) =
            userId to movieCode in keys

        override suspend fun addValidation(userId: Long, movie: Movie, watchedOn: LocalDate) =
            keys.add(userId to movie.code)

        override suspend fun removeValidation(userId: Long, movieCode: EditorialCode) =
            keys.remove(userId to movieCode)
    }
}
