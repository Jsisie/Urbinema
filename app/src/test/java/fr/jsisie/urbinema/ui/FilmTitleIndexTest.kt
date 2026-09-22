package fr.jsisie.urbinema.ui

import fr.jsisie.urbinema.ui.model.filmIndexLetter
import fr.jsisie.urbinema.ui.model.filmSortKey
import org.junit.Assert.assertEquals
import org.junit.Test

class FilmTitleIndexTest {

    @Test
    fun stripsFrenchArticlesForSortAndLetter() {
        assertEquals("Amants", filmSortKey("Les Amants"))
        assertEquals('A', filmIndexLetter("Les Amants"))

        assertEquals("amant", filmSortKey("L'amant"))
        assertEquals('A', filmIndexLetter("L'amant"))

        assertEquals("amant", filmSortKey("L’amant"))
        assertEquals('A', filmIndexLetter("L’amant"))

        assertEquals("Haine", filmSortKey("La Haine"))
        assertEquals('H', filmIndexLetter("La Haine"))

        assertEquals("Samouraï", filmSortKey("Le Samouraï"))
        assertEquals('S', filmIndexLetter("Le Samouraï"))
    }

    @Test
    fun stripsEnglishArticles() {
        assertEquals("Godfather", filmSortKey("The Godfather"))
        assertEquals('G', filmIndexLetter("The Godfather"))

        assertEquals("Clockwork Orange", filmSortKey("A Clockwork Orange"))
        assertEquals('C', filmIndexLetter("A Clockwork Orange"))
    }

    @Test
    fun letterBarNeverUsesRawLesOrL() {
        // Pressing L must not land on these — they belong under A / Q / etc.
        assertEquals('A', filmIndexLetter("Les Amants"))
        assertEquals('A', filmIndexLetter("L'avventura"))
        assertEquals('Q', filmIndexLetter("Les Quatre Cents Coups"))
    }
}
