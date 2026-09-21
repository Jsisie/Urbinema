package fr.jsisie.urbinema.domain.quest

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.MovieFormat

/**
 * Catalog rule codes wired to the weekly quest pool.
 *
 * Named aliases stay explicit. Patterned codes are resolved on demand:
 * `WATCH_COUNTRY_*`, `WATCH_CONTINENT_*`, `WATCH_GENRE_*`,
 * `WATCH_CHARACTERISTIC_*`, `WATCH_DECADE_*`, `WATCH_BEFORE_*`,
 * `WATCH_FROM_*`, `WATCH_RUNTIME_OVER_*`.
 */
object DefaultQuestRules {
    /** Builds the registry used at runtime and by catalog fixture tests. */
    fun registry(): QuestRuleRegistry = QuestRuleRegistry(
        rules = mapOf(
            EditorialCode("WATCH_SILENT") to QuestRules.matchingMovies { it.isSilent },
            EditorialCode("WATCH_BLACK_AND_WHITE") to QuestRules.matchingMovies { it.isBlackAndWhite },
            EditorialCode("WATCH_EXPERIMENTAL") to QuestRules.matchingMovies { it.isExperimental },
            EditorialCode("WATCH_SHORT") to QuestRules.matchingMovies { it.format == MovieFormat.SHORT },
            EditorialCode("WATCH_FEATURE") to QuestRules.matchingMovies {
                it.format == MovieFormat.FEATURE || it.format == MovieFormat.EXTENDED
            },
            EditorialCode("WATCH_GENRE_DRAMA") to genre("DRAME"),
            EditorialCode("DISTINCT_ASIAN_COUNTRIES") to continent("ASIA"),
            EditorialCode("DISTINCT_DIRECTORS") to QuestRules.distinct { it.directors },
            EditorialCode("DISTINCT_COUNTRIES") to QuestRules.distinct { it.countries },
            EditorialCode("DISTINCT_GENRES") to QuestRules.distinct { it.genres },
            EditorialCode("DISTINCT_CONTINENTS") to QuestRules.distinct { it.continents },
            EditorialCode("DISTINCT_DECADES") to QuestRules.distinct { movie ->
                listOf(EditorialCode((movie.releaseYear / 10 * 10).toString()))
            },
        ),
        resolve = ::fromCode,
    )

    /**
     * Parses a patterned catalog code such as `WATCH_COUNTRY_JAPAN` or
     * `WATCH_DECADE_1960`. Returns null when the prefix is unknown so
     * [QuestRuleRegistry.require] can fail fast on bad editorial data.
     */
    internal fun fromCode(code: EditorialCode): QuestRule? {
        val value = code.value
        return when {
            value.startsWith("WATCH_COUNTRY_") -> country(value.removePrefix("WATCH_COUNTRY_"))
            value.startsWith("WATCH_CONTINENT_") -> continent(value.removePrefix("WATCH_CONTINENT_"))
            value.startsWith("WATCH_GENRE_") -> genre(value.removePrefix("WATCH_GENRE_"))
            value.startsWith("WATCH_CHARACTERISTIC_") ->
                characteristic(value.removePrefix("WATCH_CHARACTERISTIC_"))
            value.startsWith("WATCH_DECADE_") ->
                value.removePrefix("WATCH_DECADE_").toIntOrNull()?.let(::decade)
            value.startsWith("WATCH_BEFORE_") ->
                value.removePrefix("WATCH_BEFORE_").toIntOrNull()?.let { year ->
                    QuestRules.matchingMovies { it.releaseYear < year }
                }
            value.startsWith("WATCH_FROM_") ->
                value.removePrefix("WATCH_FROM_").toIntOrNull()?.let { year ->
                    QuestRules.matchingMovies { it.releaseYear >= year }
                }
            value.startsWith("WATCH_RUNTIME_OVER_") ->
                value.removePrefix("WATCH_RUNTIME_OVER_").toIntOrNull()?.let { minutes ->
                    QuestRules.matchingMovies { it.durationMinutes > minutes }
                }
            else -> null
        }
    }

    private fun country(code: String) =
        QuestRules.matchingMovies { EditorialCode(code) in it.countries }

    private fun continent(code: String) =
        QuestRules.matchingMovies { EditorialCode(code) in it.continents }

    private fun genre(code: String) =
        QuestRules.matchingMovies { EditorialCode(code) in it.genres }

    private fun characteristic(code: String) =
        QuestRules.matchingMovies { EditorialCode(code) in it.characteristics }

    private fun decade(startYear: Int) =
        QuestRules.matchingMovies { it.releaseYear in startYear until (startYear + 10) }
}
