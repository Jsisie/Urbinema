package fr.jsisie.urbinema.data.repository

import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents

/** Maps a complete Room projection to the Android-free rank/badge model. */
suspend fun MovieWithRelations.toDomain(database: UrbinemaDatabase): Movie {
    val catalogDao = database.catalogDao()
    val id = movie.movieId
    val primaryCountry = checkNotNull(catalogDao.primaryCountryCode(id)) {
        "Movie ${movie.code} has no primary country"
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
        countries = countries.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        continents = catalogDao.primaryContinentCodes(id)
            .mapTo(linkedSetOf(), ::EditorialCode),
        directors = directors.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        genres = genres.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        characteristics = characteristics.mapTo(linkedSetOf()) { EditorialCode(it.code) },
        directorCharacteristics = catalogDao.directorCharacteristicCodes(id)
            .mapTo(linkedSetOf(), ::EditorialCode),
        era = catalogDao.eraCodeForYear(movie.releaseYear)?.let(::EditorialCode),
        isSilent = movie.isSilent,
        isBlackAndWhite = movie.isBlackAndWhite,
        isExperimental = movie.isExperimental,
    )
}
