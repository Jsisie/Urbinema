package fr.jsisie.urbinema.domain.quest

import fr.jsisie.urbinema.domain.model.EditorialCode
import fr.jsisie.urbinema.domain.model.Movie
import fr.jsisie.urbinema.domain.model.MovieFormat
import fr.jsisie.urbinema.domain.model.MovieValidation
import fr.jsisie.urbinema.domain.model.MovieWeightComponents
import fr.jsisie.urbinema.domain.xp.QuestDifficulty
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

class QuestEngineTest {
    private val zone = ZoneId.of("Europe/Paris")
    private val calendar = QuestCalendar()
    private val ruleCode = EditorialCode("COUNT_ALL")
    private val engine = QuestEngine(QuestRuleRegistry(mapOf(
        ruleCode to QuestRules.matchingMovies { true },
    )))

    @Test
    fun `week changes exactly Monday at two local time`() {
        val before = Instant.parse("2026-09-14T23:59:59Z") // Tue 01:59:59 CEST
        val after = Instant.parse("2026-09-15T00:00:00Z") // Tue in UTC, Monday boundary local date is 14th
        val mondayBefore = Instant.parse("2026-09-13T23:59:59Z")
        val mondayAfter = Instant.parse("2026-09-14T00:00:00Z")
        assertEquals(LocalDate.of(2026, 9, 7), calendar.weekContaining(mondayBefore, zone).startsAt.atZone(zone).toLocalDate())
        assertEquals(LocalDate.of(2026, 9, 14), calendar.weekContaining(mondayAfter, zone).startsAt.atZone(zone).toLocalDate())
        assertEquals(calendar.weekContaining(before, zone), calendar.weekContaining(after, zone))
    }

    @Test
    fun `week duration follows daylight saving transitions`() {
        val week = calendar.weekContaining(Instant.parse("2026-10-26T12:00:00Z"), zone)
        val hours = java.time.Duration.between(week.startsAt, week.expiresAt).toHours()
        assertEquals(168L, hours) // DST changed the day before this Monday.
        assertEquals(2, week.startsAt.atZone(zone).hour)
    }

    @Test
    fun `validations before activation and watched dates outside week are non retroactive`() {
        val week = calendar.weekContaining(Instant.parse("2026-09-16T10:00:00Z"), zone)
        val quest = assignment(week, target = 1)
        val beforeActivation = validation(
            "OLD", LocalDate.of(2026, 9, 14), week.startsAt.minusSeconds(1),
        )
        val oldWatchDate = validation(
            "OLD_DATE", LocalDate.of(2026, 9, 13), week.startsAt.plusSeconds(1),
        )
        assertEquals(0, engine.progress(quest, listOf(beforeActivation, oldWatchDate)).count)
    }

    @Test
    fun `progress is capped and duplicate movie cannot progress twice`() {
        val week = calendar.weekContaining(Instant.parse("2026-09-16T10:00:00Z"), zone)
        val event = validation("A", LocalDate.of(2026, 9, 16), week.startsAt.plusSeconds(1))
        val progress = engine.progress(assignment(week, target = 1), listOf(event, event))
        assertEquals(1, progress.count)
        assertTrue(progress.completed)
    }

    @Test
    fun `reward is granted once only while active`() {
        val week = calendar.weekContaining(Instant.parse("2026-09-16T10:00:00Z"), zone)
        val event = validation("A", LocalDate.of(2026, 9, 16), week.startsAt.plusSeconds(1))
        val quest = assignment(week, target = 1)
        val result = engine.reward(quest, listOf(event), week.startsAt.plusSeconds(2))
        assertEquals(250, (result as QuestRewardResult.Granted).xp)
        assertEquals(QuestRewardResult.AlreadyGranted, engine.reward(
            quest.copy(completedAt = week.startsAt.plusSeconds(2), rewarded = true),
            listOf(event),
            week.startsAt.plusSeconds(3),
        ))
        assertEquals(QuestRewardResult.Expired, engine.reward(quest, listOf(event), week.expiresAt))
    }

    @Test
    fun `incomplete quest gives no xp`() {
        val week = calendar.weekContaining(Instant.parse("2026-09-16T10:00:00Z"), zone)
        val result = engine.reward(assignment(week, target = 2), emptyList(), week.startsAt.plusSeconds(1))
        assertEquals(QuestRewardResult.NotCompleted, result)
        assertFalse(engine.progress(assignment(week, 2), emptyList()).completed)
    }

    @Test
    fun `a country quest is not completable once every matching film is watched`() {
        val rule = QuestRules.matchingMovies { EditorialCode("ITALY") in it.countries }
        val leftover = listOf(movie("ONLY_FRANCE", country = "FRANCE"))
        assertEquals(0, rule.remainingCapacity(leftover))
        assertTrue(rule.remainingCapacity(listOf(movie("ROMA", country = "ITALY"))) >= 1)
        assertTrue(rule.remainingCapacity(listOf(movie("ROMA", country = "ITALY"))) < 3)
    }

    @Test
    fun `asian films quest counts remaining asian movies`() {
        val rule = DefaultQuestRules.registry().require(EditorialCode("WATCH_CONTINENT_ASIA"))
        val onlyJapan = listOf(
            movie("KWAIDAN", country = "JAPAN", continents = setOf("ASIA")),
            movie("TOKYO", country = "JAPAN", continents = setOf("ASIA")),
        )
        assertEquals(2, rule.remainingCapacity(onlyJapan))
        val threeFilms = listOf(
            movie("KWAIDAN", country = "JAPAN", continents = setOf("ASIA")),
            movie("PATHER", country = "INDIA", continents = setOf("ASIA")),
            movie("CHUNGKING", country = "HONG_KONG", continents = setOf("ASIA")),
        )
        assertEquals(3, rule.remainingCapacity(threeFilms))
        val mixed = threeFilms + movie("ROME", country = "ITALY", continents = setOf("EUROPE"))
        assertEquals(3, rule.remainingCapacity(mixed))
    }

    @Test
    fun `patterned rule codes resolve country genre decade and runtime`() {
        val registry = DefaultQuestRules.registry()
        val comedies = listOf(
            movie("A", genres = setOf("COMEDIE")),
            movie("B", genres = setOf("DRAME")),
        )
        assertEquals(1, registry.require(EditorialCode("WATCH_GENRE_COMEDIE")).remainingCapacity(comedies))
        val fifties = listOf(movie("C", year = 1954), movie("D", year = 1962))
        assertEquals(1, registry.require(EditorialCode("WATCH_DECADE_1950")).remainingCapacity(fifties))
        val longFilms = listOf(movie("E", minutes = 130), movie("F", minutes = 90))
        assertEquals(
            1,
            registry.require(EditorialCode("WATCH_RUNTIME_OVER_120")).remainingCapacity(longFilms),
        )
    }

    private fun assignment(week: QuestWeek, target: Int) = AssignedQuest(
        assignmentCode = EditorialCode("ASSIGNMENT"),
        definition = QuestDefinition(EditorialCode("QUEST"), ruleCode, QuestDifficulty.SILVER, target),
        week = week,
        xpRewardSnapshot = 250,
    )

    private fun validation(code: String, watchedOn: LocalDate, at: Instant) = MovieValidation(
        movie = movie(code),
        watchedOn = watchedOn,
        validatedAt = at,
    )

    private fun movie(
        code: String,
        country: String = "FRANCE",
        continents: Set<String> = setOf("EUROPE"),
        genres: Set<String> = emptySet(),
        year: Int = 2000,
        minutes: Int = 90,
    ) = Movie(
        code = EditorialCode(code),
        originalTitle = code,
        releaseYear = year,
        durationMinutes = minutes,
        format = MovieFormat.FEATURE,
        weight = MovieWeightComponents(0.0, 0.0, 0.0, 0.0),
        primaryCountry = EditorialCode(country),
        continents = continents.map(::EditorialCode).toSet(),
        directors = setOf(EditorialCode("DIRECTOR")),
        genres = genres.map(::EditorialCode).toSet(),
    )
}
