package fr.jsisie.urbinema.data.importer

import kotlinx.serialization.Serializable

/** Versioned JSON root consumed when building a preloaded Room artefact. */
@Serializable
data class CatalogPack(
    val version: Int,
    val generatedAt: String,
    val mediaAssets: List<MediaAssetImport> = emptyList(),
    val characteristicTypes: List<CharacteristicTypeImport> = emptyList(),
    val countries: List<CountryImport> = emptyList(),
    val continents: List<ContinentImport> = emptyList(),
    val directors: List<DirectorImport> = emptyList(),
    val characteristics: List<CharacteristicImport> = emptyList(),
    val genres: List<GenreImport> = emptyList(),
    val eras: List<EraImport> = emptyList(),
    val movies: List<MovieImport> = emptyList(),
    val collections: List<CollectionImport> = emptyList(),
    val rankings: List<RankingImport> = emptyList(),
    val badges: List<BadgeImport> = emptyList(),
    val quests: List<QuestImport> = emptyList(),
    /** Codes removed as duplicates. `from` no longer has a movie row; `to` is the film that remains. */
    val movieAliases: List<MovieAliasImport> = emptyList(),
)

@Serializable
data class MovieAliasImport(
    val from: String,
    val to: String,
)

@Serializable
data class MediaAssetImport(
    val code: String,
    val storageType: String,
    val path: String,
    val contentDescriptionKey: String? = null,
    val mimeType: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class CharacteristicTypeImport(val typeCode: String, val name: String)

@Serializable
data class CountryImport(
    val code: String,
    val name: String,
    val isoCode: String? = null,
    val imageMediaCode: String? = null,
    val continentCodes: List<String> = emptyList(),
    val isActive: Boolean = true,
)

@Serializable
data class ContinentImport(
    val code: String,
    val name: String,
    val imageMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class DirectorImport(
    val code: String,
    val firstName: String? = null,
    val lastName: String,
    val displayName: String,
    val biography: String? = null,
    val portraitMediaCode: String? = null,
    val characteristicCodes: List<String> = emptyList(),
    val isActive: Boolean = true,
)

@Serializable
data class CharacteristicImport(
    val code: String,
    val name: String,
    val typeCode: String,
    val description: String? = null,
    val imageMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class GenreImport(
    val code: String,
    val name: String,
    val description: String? = null,
    val imageMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class EraImport(
    val code: String,
    val name: String,
    val startYear: Int,
    val endYear: Int,
    val description: String? = null,
    val imageMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class MovieImport(
    val code: String,
    val originalTitle: String,
    val frenchTitle: String? = null,
    val releaseYear: Int,
    val durationMinutes: Int,
    val format: String,
    val synopsis: String? = null,
    val posterMediaCode: String? = null,
    val historicalDistance: Double,
    val artisticDemand: Double,
    val historicalRichness: Double,
    val culturalRichness: Double,
    val isSilent: Boolean = false,
    val isBlackAndWhite: Boolean = false,
    val isExperimental: Boolean = false,
    val countries: List<MovieCountryImport>,
    val directors: List<MovieDirectorImport>,
    val genreCodes: List<String> = emptyList(),
    val characteristicCodes: List<String> = emptyList(),
    val isActive: Boolean = true,
)

@Serializable
data class MovieCountryImport(val code: String, val isPrimary: Boolean)

@Serializable
data class MovieDirectorImport(val code: String, val billingOrder: Int)

@Serializable
data class CollectionImport(
    val code: String,
    val displayOrder: Int,
    val name: String,
    val description: String? = null,
    val longDescription: String? = null,
    val track: String = "CLUB",
    val coverMediaCode: String? = null,
    val isPublished: Boolean = false,
    val movies: List<CollectionMovieImport> = emptyList(),
    val characteristicCodes: List<String> = emptyList(),
    val countryCodes: List<String> = emptyList(),
    val continentCodes: List<String> = emptyList(),
    val eraCodes: List<String> = emptyList(),
    val isActive: Boolean = true,
)

@Serializable
data class CollectionMovieImport(val code: String, val displayOrder: Int)

@Serializable
data class RankingImport(
    val code: String,
    val displayOrder: Int,
    val name: String,
    val description: String,
    val longDescription: String? = null,
    val imageMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class BadgeImport(
    val code: String,
    val name: String,
    val description: String,
    val difficulty: Int,
    val category: String,
    val iconMediaCode: String? = null,
    val isActive: Boolean = true,
)

@Serializable
data class QuestImport(
    val code: String,
    val name: String,
    val description: String,
    val difficulty: String,
    val ruleCode: String,
    val targetCount: Int,
    val isActive: Boolean = true,
)
