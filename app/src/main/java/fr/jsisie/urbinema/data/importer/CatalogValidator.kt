package fr.jsisie.urbinema.data.importer

import fr.jsisie.urbinema.data.db.MediaStorageType
import fr.jsisie.urbinema.data.db.MovieFormat
import fr.jsisie.urbinema.data.db.QuestDifficulty
import java.time.Instant
import java.time.Year

data class CatalogValidationError(val path: String, val message: String)

data class CatalogValidationReport(val errors: List<CatalogValidationError>) {
    val isValid: Boolean get() = errors.isEmpty()
}

/** Validates all cross-row invariants before Room starts the import transaction. */
class CatalogValidator {
    /** Returns every actionable error rather than stopping at the first malformed row. */
    fun validate(pack: CatalogPack): CatalogValidationReport {
        val errors = mutableListOf<CatalogValidationError>()
        fun error(path: String, message: String) { errors += CatalogValidationError(path, message) }
        fun unique(path: String, values: List<String>) {
            values.groupingBy { it }.eachCount().filterValues { it > 1 }.keys.forEach {
                error(path, "duplicate code '$it'")
            }
        }
        fun references(path: String, values: List<String>, available: Set<String>) {
            values.filterNot(available::contains).distinct().forEach {
                error(path, "unknown reference '$it'")
            }
        }

        if (pack.version <= 0) error("version", "must be positive")
        runCatching { Instant.parse(pack.generatedAt) }
            .onFailure { error("generatedAt", "must be an ISO-8601 UTC instant") }

        unique("mediaAssets", pack.mediaAssets.map { it.code })
        unique("characteristicTypes", pack.characteristicTypes.map { it.typeCode })
        unique("countries", pack.countries.map { it.code })
        unique("continents", pack.continents.map { it.code })
        unique("directors", pack.directors.map { it.code })
        unique("characteristics", pack.characteristics.map { it.code })
        unique("genres", pack.genres.map { it.code })
        unique("eras", pack.eras.map { it.code })
        unique("movies", pack.movies.map { it.code })
        unique("collections", pack.collections.map { it.code })
        unique("rankings", pack.rankings.map { it.code })
        unique("badges", pack.badges.map { it.code })
        unique("quests", pack.quests.map { it.code })
        listOf(
            "mediaAssets" to pack.mediaAssets.map { it.code },
            "characteristicTypes" to pack.characteristicTypes.map { it.typeCode },
            "countries" to pack.countries.map { it.code },
            "continents" to pack.continents.map { it.code },
            "directors" to pack.directors.map { it.code },
            "characteristics" to pack.characteristics.map { it.code },
            "genres" to pack.genres.map { it.code },
            "eras" to pack.eras.map { it.code },
            "movies" to pack.movies.map { it.code },
            "collections" to pack.collections.map { it.code },
            "rankings" to pack.rankings.map { it.code },
            "badges" to pack.badges.map { it.code },
            "quests" to pack.quests.map { it.code },
        ).forEach { (path, codes) ->
            if (codes.any(String::isBlank)) error("$path.code", "must not be blank")
        }

        val media = pack.mediaAssets.mapTo(mutableSetOf()) { it.code }
        val typeCodes = pack.characteristicTypes.mapTo(mutableSetOf()) { it.typeCode }
        val countries = pack.countries.mapTo(mutableSetOf()) { it.code }
        val continents = pack.continents.mapTo(mutableSetOf()) { it.code }
        val directors = pack.directors.mapTo(mutableSetOf()) { it.code }
        val characteristics = pack.characteristics.mapTo(mutableSetOf()) { it.code }
        val genres = pack.genres.mapTo(mutableSetOf()) { it.code }
        val eras = pack.eras.mapTo(mutableSetOf()) { it.code }
        val movies = pack.movies.mapTo(mutableSetOf()) { it.code }

        pack.mediaAssets.forEachIndexed { index, value ->
            if (value.code.isBlank()) error("mediaAssets[$index].code", "must not be blank")
            if (runCatching { MediaStorageType.valueOf(value.storageType) }.isFailure) {
                error("mediaAssets[$index].storageType", "must be ASSET or FILE")
            }
            if (value.path.isBlank() || value.path.startsWith("/") || value.path.startsWith("\\") ||
                Regex("^[A-Za-z]:").containsMatchIn(value.path) || ".." in value.path.split('/', '\\')
            ) error("mediaAssets[$index].path", "must be a safe application-relative path")
        }

        references("countries.imageMediaCode", pack.countries.mapNotNull { it.imageMediaCode }, media)
        references("countries.continentCodes", pack.countries.flatMap { it.continentCodes }, continents)
        pack.countries.forEachIndexed { index, country ->
            duplicateRefs("countries[$index].continentCodes", country.continentCodes, ::error)
        }
        references("continents.imageMediaCode", pack.continents.mapNotNull { it.imageMediaCode }, media)
        references("directors.portraitMediaCode", pack.directors.mapNotNull { it.portraitMediaCode }, media)
        references(
            "directors.characteristicCodes",
            pack.directors.flatMap { it.characteristicCodes },
            characteristics,
        )
        pack.directors.forEachIndexed { index, director ->
            duplicateRefs(
                "directors[$index].characteristicCodes",
                director.characteristicCodes,
                ::error,
            )
        }
        references("characteristics.typeCode", pack.characteristics.map { it.typeCode }, typeCodes)
        references(
            "characteristics.imageMediaCode",
            pack.characteristics.mapNotNull { it.imageMediaCode },
            media,
        )
        references("genres.imageMediaCode", pack.genres.mapNotNull { it.imageMediaCode }, media)
        references("eras.imageMediaCode", pack.eras.mapNotNull { it.imageMediaCode }, media)

        val maximumYear = Year.now().value + 2
        pack.eras.forEachIndexed { index, era ->
            if (era.startYear > era.endYear) error("eras[$index]", "startYear must be <= endYear")
        }
        pack.movies.forEachIndexed { index, movie ->
            val path = "movies[$index]"
            if (movie.originalTitle.isBlank()) error("$path.originalTitle", "must not be blank")
            if (movie.durationMinutes <= 0) error("$path.durationMinutes", "must be positive")
            if (movie.releaseYear !in 1880..maximumYear) {
                error("$path.releaseYear", "must be between 1880 and $maximumYear")
            }
            if (runCatching { MovieFormat.valueOf(movie.format) }.isFailure) {
                error("$path.format", "must be SHORT, MEDIUM, FEATURE or EXTENDED")
            }
            listOf(
                "historicalDistance" to movie.historicalDistance,
                "artisticDemand" to movie.artisticDemand,
                "historicalRichness" to movie.historicalRichness,
                "culturalRichness" to movie.culturalRichness,
            ).forEach { (name, score) ->
                if (!score.isFinite() || score !in 0.0..1.0) error("$path.$name", "must be in [0,1]")
            }
            references("$path.posterMediaCode", listOfNotNull(movie.posterMediaCode), media)
            references("$path.countries", movie.countries.map { it.code }, countries)
            references("$path.directors", movie.directors.map { it.code }, directors)
            references("$path.genreCodes", movie.genreCodes, genres)
            references("$path.characteristicCodes", movie.characteristicCodes, characteristics)
            if (movie.countries.count { it.isPrimary } != 1) {
                error("$path.countries", "must contain exactly one primary country")
            }
            if (movie.directors.isEmpty()) error("$path.directors", "must contain at least one director")
            duplicateRefs("$path.countries", movie.countries.map { it.code }, ::error)
            duplicateRefs("$path.directors", movie.directors.map { it.code }, ::error)
            duplicateRefs("$path.genreCodes", movie.genreCodes, ::error)
            duplicateRefs("$path.characteristicCodes", movie.characteristicCodes, ::error)
            val orders = movie.directors.map { it.billingOrder }
            if (orders.any { it < 0 } || orders.distinct().size != orders.size) {
                error("$path.directors.billingOrder", "must contain unique non-negative values")
            }
        }

        pack.collections.forEachIndexed { index, collection ->
            val path = "collections[$index]"
            references("$path.coverMediaCode", listOfNotNull(collection.coverMediaCode), media)
            references("$path.movies", collection.movies.map { it.code }, movies)
            references("$path.characteristicCodes", collection.characteristicCodes, characteristics)
            references("$path.countryCodes", collection.countryCodes, countries)
            references("$path.continentCodes", collection.continentCodes, continents)
            references("$path.eraCodes", collection.eraCodes, eras)
            duplicateRefs("$path.movies", collection.movies.map { it.code }, ::error)
            duplicateRefs("$path.characteristicCodes", collection.characteristicCodes, ::error)
            duplicateRefs("$path.countryCodes", collection.countryCodes, ::error)
            duplicateRefs("$path.continentCodes", collection.continentCodes, ::error)
            duplicateRefs("$path.eraCodes", collection.eraCodes, ::error)
            val orders = collection.movies.map { it.displayOrder }
            if (orders.any { it < 0 } || orders.distinct().size != orders.size) {
                error("$path.movies.displayOrder", "must contain unique non-negative values")
            }
            if (collection.track !in COLLECTION_TRACKS) {
                error("$path.track", "must be GATEWAY, JOURNEY or DEMANDING")
            }
        }
        duplicateInts("collections.displayOrder", pack.collections.map { it.displayOrder }, ::error)
        duplicateInts("rankings.displayOrder", pack.rankings.map { it.displayOrder }, ::error)

        references("rankings.imageMediaCode", pack.rankings.mapNotNull { it.imageMediaCode }, media)
        references("badges.iconMediaCode", pack.badges.mapNotNull { it.iconMediaCode }, media)
        pack.badges.forEachIndexed { index, badge ->
            if (badge.difficulty !in 1..5) error("badges[$index].difficulty", "must be in [1,5]")
        }
        pack.quests.forEachIndexed { index, quest ->
            if (runCatching { QuestDifficulty.valueOf(quest.difficulty) }.isFailure) {
                error("quests[$index].difficulty", "must be BRONZE, SILVER or GOLD")
            }
            if (quest.targetCount <= 0) error("quests[$index].targetCount", "must be positive")
            if (quest.ruleCode.isBlank()) error("quests[$index].ruleCode", "must not be blank")
        }
        return CatalogValidationReport(errors)
    }

    private fun duplicateRefs(
        path: String,
        values: List<String>,
        error: (String, String) -> Unit,
    ) {
        values.groupingBy { it }.eachCount().filterValues { it > 1 }.keys.forEach {
            error(path, "duplicate reference '$it'")
        }
    }

    private fun duplicateInts(
        path: String,
        values: List<Int>,
        error: (String, String) -> Unit,
    ) {
        values.groupingBy { it }.eachCount().filterValues { it > 1 }.keys.forEach {
            error(path, "duplicate value '$it'")
        }
    }

    private companion object {
        val COLLECTION_TRACKS = setOf("GATEWAY", "CLUB", "DARKROOM", "CINEMATHEQUE", "OFFSCREEN")
    }
}
