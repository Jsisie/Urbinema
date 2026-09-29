package fr.jsisie.urbinema.data.repository

import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents

/**
 * Lookups loaded once so rank/badge mapping does not hit Room once per film.
 * The previous per-movie queries were the 30s stall after marking Vu.
 */
data class CatalogDomainLookups(
    val primaryCountryByMovieId: Map<Long, String>,
    val continentsByCountryId: Map<Long, Set<String>>,
    val characteristicCodesByDirectorId: Map<Long, Set<String>>,
    private val eras: List<EraRange>,
) {
    fun eraCodeFor(year: Int): String? = eras
        .filter { year in it.startYear..it.endYear }
        .minByOrNull { it.endYear - it.startYear }
        ?.code
}

data class EraRange(val code: String, val startYear: Int, val endYear: Int)

/** Loads country, continent, director-characteristic and era maps in a handful of queries. */
suspend fun UrbinemaDatabase.catalogDomainLookups(): CatalogDomainLookups {
    val catalogDao = catalogDao()
    val countries = catalogDao.countries().associateBy { it.countryId }
    val continents = catalogDao.continents().associateBy { it.continentId }
    val characteristics = catalogDao.characteristics().associateBy { it.characteristicId }
    val primaryCountryByMovieId = catalogDao.movieCountries()
        .filter { it.isPrimary }
        .mapNotNull { row -> countries[row.countryId]?.code?.let { row.movieId to it } }
        .toMap()
    val continentsByCountryId = catalogDao.countryContinents()
        .groupBy { it.countryId }
        .mapValues { (_, rows) ->
            rows.mapNotNull { continents[it.continentId]?.code }.toSet()
        }
    val characteristicCodesByDirectorId = catalogDao.directorCharacteristics()
        .groupBy { it.directorId }
        .mapValues { (_, rows) ->
            rows.mapNotNull { characteristics[it.characteristicId]?.code }.toSet()
        }
    val eras = catalogDao.eras().map { EraRange(it.code, it.startYear, it.endYear) }
    return CatalogDomainLookups(
        primaryCountryByMovieId = primaryCountryByMovieId,
        continentsByCountryId = continentsByCountryId,
        characteristicCodesByDirectorId = characteristicCodesByDirectorId,
        eras = eras,
    )
}

/**
 * Maps a complete Room projection to the Android-free rank/badge model.
 * A retired duplicate can still be referenced by an old "vu" row after its
 * country links were cleared; callers skip that row instead of crashing startup.
 */
fun MovieWithRelations.toDomainOrNull(lookups: CatalogDomainLookups): Movie? {
    val hasCountry = lookups.primaryCountryByMovieId[movie.movieId] != null || countries.isNotEmpty()
    if (!hasCountry) return null
    return toDomain(lookups)
}

/** Maps a complete Room projection to the Android-free rank/badge model. */
fun MovieWithRelations.toDomain(lookups: CatalogDomainLookups): Movie {
    val primaryCountry = lookups.primaryCountryByMovieId[movie.movieId]
        ?: countries.firstOrNull()?.code
        ?: error("Movie ${movie.code} has no primary country")
    val continentCodes = countries.flatMap { lookups.continentsByCountryId[it.countryId].orEmpty() }
        .ifEmpty { lookups.continentsByCountryId[countries.firstOrNull()?.countryId].orEmpty() }
    val directorChars = directors.flatMap {
        lookups.characteristicCodesByDirectorId[it.directorId].orEmpty()
    }
    return Movie(
        code = EditorialCode(movie.code),
        originalTitle = movie.originalTitle,
        frenchTitle = movie.frenchTitle,
        synopsis = movie.synopsis,
        releaseYear = movie.releaseYear,
        durationMinutes = movie.durationMinutes,
        format = MovieFormat.valueOf(movie.format.name),
        weight = MovieWeightComponents(
            historicalDistance = movie.historicalDistance,
            artisticDemand = movie.artisticDemand,
            historicalImportance = movie.historicalRichness,
            culturalRichness = movie.culturalRichness,
        ),
        primaryCountry = EditorialCode(primaryCountry),
        countries = countries.mapTo(linkedSetOf()) { EditorialCode(it.code) }
            .ifEmpty { linkedSetOf(EditorialCode(primaryCountry)) },
        continents = continentCodes.mapTo(linkedSetOf(), ::EditorialCode),
        directors = directors.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        genres = genres.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        characteristics = characteristics.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        directorCharacteristics = directorChars.mapTo(linkedSetOf(), ::EditorialCode),
        era = lookups.eraCodeFor(movie.releaseYear)?.let(::EditorialCode),
        isSilent = movie.isSilent,
        isBlackAndWhite = movie.isBlackAndWhite,
        isExperimental = movie.isExperimental,
    )
}

/** Maps a complete Room projection to the Android-free rank/badge model. */
suspend fun MovieWithRelations.toDomain(database: UrbinemaDatabase): Movie =
    toDomain(database.catalogDomainLookups())
