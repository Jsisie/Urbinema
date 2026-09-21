package fr.jsisie.urbinema.domain.model

import java.time.Instant
import java.time.LocalDate

/** Stable editorial identifier used by rules instead of database identifiers. */
@JvmInline
value class EditorialCode(val value: String) {
    init {
        require(value.matches(Regex("[A-Z0-9][A-Z0-9_\\-]*"))) {
            "An editorial code must be uppercase, stable and non-blank"
        }
    }
}

enum class MovieFormat { SHORT, MEDIUM, FEATURE, EXTENDED }

enum class TerritoryDimension {
    COUNTRY, CONTINENT, DECADE, ERA, CINEMA_CHARACTERISTIC, DIRECTOR, GENRE, FORM
}

data class TerritoryKey(
    val dimension: TerritoryDimension,
    val code: EditorialCode,
)

/** The four normalized editorial assessments entering the rank formula. */
data class MovieWeightComponents(
    val historicalDistance: Double,
    val artisticDemand: Double,
    val historicalImportance: Double,
    val culturalRichness: Double,
) {
    init {
        listOf(historicalDistance, artisticDemand, historicalImportance, culturalRichness)
            .forEach { require(it.isFinite() && it in 0.0..1.0) { "Movie weights must be in [0, 1]" } }
    }
}

/**
 * Pure domain projection of a catalog movie.
 *
 * [territories] must already follow catalog cardinality rules: only the primary
 * country, its continents, derived time territories, and every linked
 * director/genre/characteristic are represented.
 */
data class Movie(
    val code: EditorialCode,
    val originalTitle: String,
    val frenchTitle: String? = null,
    val synopsis: String? = null,
    val releaseYear: Int,
    val durationMinutes: Int,
    val format: MovieFormat,
    val weight: MovieWeightComponents,
    val primaryCountry: EditorialCode,
    val countries: Set<EditorialCode> = setOf(primaryCountry),
    val continents: Set<EditorialCode>,
    val directors: Set<EditorialCode>,
    val genres: Set<EditorialCode> = emptySet(),
    val characteristics: Set<EditorialCode> = emptySet(),
    val directorCharacteristics: Set<EditorialCode> = emptySet(),
    val era: EditorialCode? = null,
    val isSilent: Boolean = false,
    val isBlackAndWhite: Boolean = false,
    val isExperimental: Boolean = false,
) {
    init {
        require(primaryCountry in countries) { "The primary country must belong to the film countries" }
    }

    /** Returns the de-duplicated territories used by the rank engine. */
    fun rankTerritories(): Set<TerritoryKey> = buildSet {
        add(TerritoryKey(TerritoryDimension.COUNTRY, primaryCountry))
        continents.forEach { add(TerritoryKey(TerritoryDimension.CONTINENT, it)) }
        add(TerritoryKey(TerritoryDimension.DECADE, EditorialCode("DECADE_${releaseYear / 10 * 10}")))
        era?.let { add(TerritoryKey(TerritoryDimension.ERA, it)) }
        characteristics.forEach { add(TerritoryKey(TerritoryDimension.CINEMA_CHARACTERISTIC, it)) }
        directors.forEach { add(TerritoryKey(TerritoryDimension.DIRECTOR, it)) }
        genres.forEach { add(TerritoryKey(TerritoryDimension.GENRE, it)) }
        add(TerritoryKey(TerritoryDimension.FORM, EditorialCode("FORMAT_${format.name}")))
        if (isSilent) add(TerritoryKey(TerritoryDimension.FORM, EditorialCode("SILENT")))
        if (isBlackAndWhite) add(TerritoryKey(TerritoryDimension.FORM, EditorialCode("BLACK_AND_WHITE")))
        if (isExperimental) add(TerritoryKey(TerritoryDimension.FORM, EditorialCode("EXPERIMENTAL")))
    }
}

data class MovieValidation(
    val movie: Movie,
    val watchedOn: LocalDate,
    val validatedAt: Instant,
)

data class CollectionDefinition(
    val code: EditorialCode,
    val movieCodes: Set<EditorialCode>,
)
