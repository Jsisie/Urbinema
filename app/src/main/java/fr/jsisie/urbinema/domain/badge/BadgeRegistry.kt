package fr.jsisie.urbinema.domain.badge

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie

fun interface BadgeRule {
    /**
     * Tests a badge against the validated films.
     *
     * [catalogPrimaryCountries] is the set of primary countries present in the
     * packaged catalog — used by the all-countries badge, ignored by the rest.
     */
    fun isSatisfied(
        validatedMovies: Collection<Movie>,
        catalogPrimaryCountries: Set<EditorialCode>,
    ): Boolean
}

data class BadgeUnlock(val badgeCode: EditorialCode)

/** Extensible registry keyed exclusively by stable editorial badge codes. */
class BadgeRegistry(rules: Map<EditorialCode, BadgeRule>) {
    private val rules = rules.toMap()

    init {
        require(rules.isNotEmpty())
    }

    /** Returns newly satisfied badges, leaving already earned badges untouched. */
    fun newlyUnlocked(
        validatedMovies: Collection<Movie>,
        alreadyEarned: Set<EditorialCode>,
        catalogPrimaryCountries: Set<EditorialCode> = emptySet(),
    ): Set<BadgeUnlock> = rules
        .filterKeys { it !in alreadyEarned }
        .filterValues { it.isSatisfied(validatedMovies, catalogPrimaryCountries) }
        .keys
        .mapTo(linkedSetOf(), ::BadgeUnlock)

    /** Resolves one registered rule for catalog validation and focused tests. */
    fun require(code: EditorialCode): BadgeRule =
        requireNotNull(rules[code]) { "No badge rule registered for ${code.value}" }

    companion object {
        /**
         * Builds the current 32 rules. Geographic codes are stable import-contract
         * codes: ITALY, USA, JAPAN, FRANCE, EUROPE and ASIA.
         */
        fun initial(): BadgeRegistry = BadgeRegistry(linkedMapOf(
            code("001") to countAtLeast(1),
            code("002") to countAtLeast(20),
            code("003") to countAtLeast(100),
            code("004") to countAtLeast(300),
            code("005") to distinctCountries(15),
            code("006") to distinctCountries(30),
            code("007") to distinctCountries(50),
            code("008") to BadgeRule { movies, _ ->
                movies.filter { code("EUROPE") in it.continents }.map { it.primaryCountry }.toSet().size >= 10
            },
            code("009") to BadgeRule { movies, _ ->
                movies.flatMap { movie -> movie.continents.map { it to movie.code } }
                    .groupBy({ it.first }, { it.second })
                    .count { (_, filmCodes) -> filmCodes.toSet().size >= 5 } >= 5
            },
            code("010") to countryCount("ITALY", 20),
            code("011") to countryCount("USA", 50),
            code("012") to countryCount("JAPAN", 20),
            code("013") to countryCount("FRANCE", 20),
            code("014") to continentCount("ASIA", 50),
            code("015") to yearBefore(1950, 40),
            code("016") to yearBefore(1960, 100),
            code("017") to yearBefore(1980, 300),
            code("018") to BadgeRule { movies, _ -> movies.count(Movie::isSilent) >= 20 },
            code("019") to distinctDecades(5),
            code("020") to everyDecadeFrom1890To2020(),
            code("021") to BadgeRule { movies, _ ->
                movies.count { code("NOUVELLE_VAGUE_FRANCAISE") in it.directorCharacteristics } >= 15
            },
            code("022") to characteristicCount("COMMEDIA_ALL_ITALIANA", 15),
            code("023") to characteristicCount("CINEMA_SOVIETIQUE", 10),
            code("024") to genreCount("FILM_NOIR", 20),
            code("025") to characteristicCount("SPAGHETTI_WESTERN", 15),
            code("026") to BadgeRule { movies, _ -> movies.count(Movie::isExperimental) >= 10 },
            code("027") to BadgeRule { movies, _ -> movies.count { it.durationMinutes > 180 } >= 20 },
            code("028") to BadgeRule { movies, _ -> movies.count { it.durationMinutes > 300 } >= 5 },
            code("029") to BadgeRule { movies, _ ->
                movies.flatMap { movie -> movie.directors.map { it to movie.code } }
                    .groupBy({ it.first }, { it.second })
                    .count { (_, filmCodes) -> filmCodes.toSet().size >= 10 } >= 20
            },
            code("030") to BadgeRule { movies, _ ->
                movies.flatMap { movie -> movie.characteristics.map { it to movie.code } }
                    .groupBy({ it.first }, { it.second })
                    .count { (_, filmCodes) -> filmCodes.toSet().size >= 10 } >= 30
            },
            code("031") to allCatalogCountries(),
            code("032") to genreCount("HORREUR", 30),
        ))

        private fun code(value: String) = EditorialCode(value)
        private fun countAtLeast(target: Int) =
            BadgeRule { movies, _ -> movies.map(Movie::code).toSet().size >= target }
        private fun distinctCountries(target: Int) =
            BadgeRule { movies, _ -> movies.map(Movie::primaryCountry).toSet().size >= target }
        private fun countryCount(country: String, target: Int) =
            BadgeRule { movies, _ -> movies.count { it.primaryCountry == code(country) } >= target }
        private fun continentCount(continent: String, target: Int) =
            BadgeRule { movies, _ -> movies.count { code(continent) in it.continents } >= target }
        private fun distinctDecades(target: Int) =
            BadgeRule { movies, _ -> movies.map { it.releaseYear / 10 }.toSet().size >= target }
        private fun characteristicCount(characteristic: String, target: Int) =
            BadgeRule { movies, _ -> movies.count { code(characteristic) in it.characteristics } >= target }
        private fun genreCount(genre: String, target: Int) =
            BadgeRule { movies, _ -> movies.count { code(genre) in it.genres } >= target }
        private fun yearBefore(year: Int, target: Int) =
            BadgeRule { movies, _ -> movies.count { it.releaseYear < year } >= target }

        /** One validated film in every decade from the 1890s through the 2020s. */
        private fun everyDecadeFrom1890To2020() = BadgeRule { movies, _ ->
            val seen = movies.map { it.releaseYear / 10 }.toSet()
            (189..202).all { it in seen }
        }
        private fun allCatalogCountries() = BadgeRule { movies, catalogCountries ->
            catalogCountries.isNotEmpty() &&
                catalogCountries.all { country -> movies.any { it.primaryCountry == country } }
        }
    }
}
