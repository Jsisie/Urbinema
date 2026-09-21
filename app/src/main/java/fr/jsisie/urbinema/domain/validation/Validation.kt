package fr.jsisie.urbinema.domain.validation

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import java.time.Clock
import java.time.LocalDate
import java.time.Year

sealed interface MovieValidationError {
    data object BlankOriginalTitle : MovieValidationError
    data object ImplausibleReleaseYear : MovieValidationError
    data object InvalidDuration : MovieValidationError
    data object MissingDirector : MovieValidationError
    data object MissingPrimaryCountry : MovieValidationError
}

/** Strict domain-side validation shared by imports and writes. */
class MovieValidator {
    /** Returns every structural error so a catalog import can report them together. */
    fun validate(movie: Movie, currentYear: Int = Year.now().value): Set<MovieValidationError> = buildSet {
        if (movie.originalTitle.isBlank()) add(MovieValidationError.BlankOriginalTitle)
        if (movie.releaseYear !in 1880..(currentYear + 2)) add(MovieValidationError.ImplausibleReleaseYear)
        if (movie.durationMinutes <= 0) add(MovieValidationError.InvalidDuration)
        if (movie.directors.isEmpty()) add(MovieValidationError.MissingDirector)
        if (movie.primaryCountry.value.isBlank()) add(MovieValidationError.MissingPrimaryCountry)
    }
}

sealed interface ValidateMovieResult {
    data class Validated(val movieCode: EditorialCode, val watchedOn: LocalDate) : ValidateMovieResult
    data object MovieNotFound : ValidateMovieResult
    data object AlreadyValidated : ValidateMovieResult
    data object FutureWatchDate : ValidateMovieResult
    data class InvalidCatalogMovie(val errors: Set<MovieValidationError>) : ValidateMovieResult
}

interface MovieRepository {
    /** Loads an active catalog movie by its stable code. */
    suspend fun findActiveByCode(code: EditorialCode): Movie?
}

interface ValidationRepository {
    /** Tests uniqueness of the user/movie validation relation. */
    suspend fun isValidated(userId: Long, movieCode: EditorialCode): Boolean

    /** Persists the validation and its activity event in one data-layer transaction. */
    suspend fun addValidation(userId: Long, movie: Movie, watchedOn: LocalDate): Boolean

    /** Removes one validation; derived progression is then recalculated by consumers. */
    suspend fun removeValidation(userId: Long, movieCode: EditorialCode): Boolean
}

/** Validates a catalog film while enforcing date and idempotency constraints. */
class ValidateMovieUseCase(
    private val movies: MovieRepository,
    private val validations: ValidationRepository,
    private val validator: MovieValidator,
    private val clock: Clock,
) {
    /** Marks one active catalog film as seen; arbitrary external films are rejected. */
    suspend fun execute(
        userId: Long,
        movieCode: EditorialCode,
        watchedOn: LocalDate,
    ): ValidateMovieResult {
        require(userId > 0)
        if (watchedOn.isAfter(LocalDate.now(clock))) return ValidateMovieResult.FutureWatchDate
        val movie = movies.findActiveByCode(movieCode) ?: return ValidateMovieResult.MovieNotFound
        val errors = validator.validate(movie, Year.now(clock).value)
        if (errors.isNotEmpty()) return ValidateMovieResult.InvalidCatalogMovie(errors)
        if (validations.isValidated(userId, movieCode)) return ValidateMovieResult.AlreadyValidated
        return if (validations.addValidation(userId, movie, watchedOn)) {
            ValidateMovieResult.Validated(movieCode, watchedOn)
        } else {
            ValidateMovieResult.AlreadyValidated
        }
    }
}
