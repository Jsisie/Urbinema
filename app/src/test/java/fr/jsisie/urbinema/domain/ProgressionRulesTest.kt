package fr.jsisie.urbinema.domain

import fr.jsisie.urbinema.domain.badge.BadgeRegistry
import fr.jsisie.urbinema.domain.badge.BadgeRule
import fr.jsisie.urbinema.domain.collection.CollectionMilestone
import fr.jsisie.urbinema.domain.collection.CollectionProgressEngine
import fr.jsisie.urbinema.domain.model.CollectionDefinition
import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ProgressionRulesTest {
    @Test
    fun `collection milestones use percentages for arbitrary sizes`() {
        val definition = CollectionDefinition(
            code("COLLECTION"),
            (1..12).mapTo(linkedSetOf()) { code("MOVIE_$it") },
        )
        val engine = CollectionProgressEngine()
        assertEquals(CollectionMilestone.NOT_EXPLORED, engine.calculate(definition, emptySet()).milestone)
        assertEquals(CollectionMilestone.DISCOVERED, engine.calculate(definition, (1..3).mapToSet()).milestone)
        assertEquals(CollectionMilestone.EXPLORING, engine.calculate(definition, (1..6).mapToSet()).milestone)
        assertEquals(CollectionMilestone.ADVANCED, engine.calculate(definition, (1..9).mapToSet()).milestone)
        val complete = engine.calculate(definition, (1..12).mapToSet())
        assertEquals(CollectionMilestone.COMPLETED, complete.milestone)
        assertTrue(complete.completed)
        assertEquals(100, complete.percentage)
    }

    @Test
    fun `empty collection is not completed`() {
        val progress = CollectionProgressEngine().calculate(
            CollectionDefinition(code("EMPTY"), emptySet()),
            emptySet(),
        )
        assertFalse(progress.completed)
        assertEquals(0, progress.percentage)
    }

    @Test
    fun `all thirty-eight initial badge codes are registered`() {
        val registry = BadgeRegistry.initial()
        (1..38).forEach { registry.require(code(it.toString().padStart(3, '0'))) }
    }

    @Test
    fun `geographic badges count primary country only and earned badges stay excluded`() {
        val registry = BadgeRegistry.initial()
        val italyFilms = (1..20).map { movie("ITALY_$it", country = "ITALY") }
        assertTrue(registry.require(code("010")).holds(italyFilms))
        assertTrue(registry.newlyUnlocked(italyFilms, setOf(code("010")))
            .none { it.badgeCode == code("010") })
    }

    @Test
    fun `duration rules are strictly over three and five hours`() {
        val registry = BadgeRegistry.initial()
        assertFalse(registry.require(code("027")).holds(
            (1..20).map { movie("THREE_$it", duration = 180) },
        ))
        assertTrue(registry.require(code("027")).holds(
            (1..20).map { movie("LONG_$it", duration = 181) },
        ))
        assertFalse(registry.require(code("028")).holds(
            (1..5).map { movie("FIVE_$it", duration = 300) },
        ))
    }

    @Test
    fun `era badges use the doubled cinephile thresholds`() {
        val registry = BadgeRegistry.initial()
        assertFalse(registry.require(code("015")).holds((1..39).map { movie("PRE50_$it", year = 1949) }))
        assertTrue(registry.require(code("015")).holds((1..40).map { movie("PRE50_$it", year = 1949) }))
        assertFalse(registry.require(code("016")).holds((1..99).map { movie("PRE60_$it", year = 1959) }))
        assertTrue(registry.require(code("016")).holds((1..100).map { movie("PRE60_$it", year = 1959) }))
        assertFalse(registry.require(code("017")).holds((1..299).map { movie("PRE80_$it", year = 1979) }))
        assertTrue(registry.require(code("017")).holds((1..300).map { movie("PRE80_$it", year = 1979) }))
        val decades = (1890..2020 step 10).map { movie("DECADE_$it", year = it) }
        assertFalse(registry.require(code("020")).holds(decades.dropLast(1)))
        assertTrue(registry.require(code("020")).holds(decades))
    }

    @Test
    fun `all-countries badge needs one film from every catalog primary country`() {
        val registry = BadgeRegistry.initial()
        val catalog = setOf(code("FRANCE"), code("JAPAN"))
        val franceOnly = listOf(movie("FR", country = "FRANCE"))
        assertFalse(registry.require(code("031")).holds(franceOnly, catalog))
        assertTrue(
            registry.require(code("031")).holds(
                franceOnly + movie("JP", country = "JAPAN"),
                catalog,
            ),
        )
        assertFalse(registry.require(code("031")).holds(franceOnly, emptySet()))
    }

    @Test
    fun `horror badge needs fifty films tagged HORREUR`() {
        val registry = BadgeRegistry.initial()
        val fortyNine = (1..49).map { movie("HORROR_$it", genres = setOf("HORREUR")) }
        assertFalse(registry.require(code("032")).holds(fortyNine))
        assertTrue(registry.require(code("032")).holds(fortyNine + movie("HORROR_50", genres = setOf("HORREUR"))))
    }

    @Test
    fun `new form genre and continent badges use their catalog thresholds`() {
        val registry = BadgeRegistry.initial()
        val silver = (1..39).map { movie("BW_$it", blackAndWhite = true) }
        assertFalse(registry.require(code("033")).holds(silver))
        assertTrue(registry.require(code("033")).holds(silver + movie("BW_40", blackAndWhite = true)))
        assertFalse(registry.require(code("033")).holds((1..50).map { movie("SILENT_$it", blackAndWhite = true, silent = true) }))

        val shorts = (1..29).map { movie("SHORT_$it", format = MovieFormat.SHORT) }
        assertFalse(registry.require(code("034")).holds(shorts))
        assertTrue(registry.require(code("034")).holds(shorts + movie("SHORT_30", format = MovieFormat.SHORT)))

        val docs = (1..19).map { movie("DOC_$it", genres = setOf("DOCUMENTAIRE")) }
        assertFalse(registry.require(code("035")).holds(docs))
        assertTrue(registry.require(code("035")).holds(docs + movie("DOC_20", genres = setOf("DOCUMENTAIRE"))))

        val africa = (1..19).map { movie("AF_$it", continents = setOf("AFRICA")) }
        assertFalse(registry.require(code("036")).holds(africa))
        assertTrue(registry.require(code("036")).holds(africa + movie("AF_20", continents = setOf("AFRICA"))))

        val recent = (1..49).map { movie("NOW_$it", year = 2000) }
        assertFalse(registry.require(code("037")).holds(recent))
        assertTrue(registry.require(code("037")).holds(recent + movie("NOW_50", year = 2000)))
        assertFalse(registry.require(code("037")).holds((1..50).map { movie("OLD_$it", year = 1999) }))

        val animated = (1..19).map { movie("ANIM_$it", genres = setOf("ANIMATION")) }
        assertFalse(registry.require(code("038")).holds(animated))
        assertTrue(registry.require(code("038")).holds(animated + movie("ANIM_20", genres = setOf("ANIMATION"))))
    }

    private fun Iterable<Int>.mapToSet() = mapTo(linkedSetOf()) { code("MOVIE_$it") }
    private fun code(value: String) = EditorialCode(value)
    private fun BadgeRule.holds(
        movies: Collection<Movie>,
        catalogCountries: Set<EditorialCode> = emptySet(),
    ) = isSatisfied(movies, catalogCountries)
    private fun movie(
        movieCode: String,
        country: String = "FRANCE",
        duration: Int = 90,
        year: Int = 2000,
        genres: Set<String> = emptySet(),
        blackAndWhite: Boolean = false,
        silent: Boolean = false,
        format: MovieFormat = MovieFormat.FEATURE,
        continents: Set<String> = setOf("EUROPE"),
    ) = Movie(
        code = code(movieCode),
        originalTitle = movieCode,
        releaseYear = year,
        durationMinutes = duration,
        format = format,
        weight = MovieWeightComponents(0.0, 0.0, 0.0, 0.0),
        primaryCountry = code(country),
        continents = continents.mapTo(linkedSetOf(), ::code),
        directors = setOf(code("DIRECTOR")),
        genres = genres.mapTo(linkedSetOf(), ::code),
        isSilent = silent,
        isBlackAndWhite = blackAndWhite,
    )
}
