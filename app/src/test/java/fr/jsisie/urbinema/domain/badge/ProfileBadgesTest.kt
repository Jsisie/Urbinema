package fr.jsisie.urbinema.domain.badge

import org.junit.Assert.assertEquals
import org.junit.Test

class ProfileBadgesTest {
    @Test
    fun `first three earned fill the profile when nothing was chosen`() {
        assertEquals(
            listOf("001", "005", "018"),
            ProfileBadges.resolve(listOf("001", "005", "018", "027"), stored = null),
        )
    }

    @Test
    fun `a custom selection keeps order and drops unknown codes`() {
        assertEquals(
            listOf("027", "001"),
            ProfileBadges.resolve(
                earnedInOrder = listOf("001", "005", "027"),
                stored = "027,MISSING,001",
            ),
        )
    }

    @Test
    fun `encode keeps at most three codes`() {
        assertEquals("001,005,018", ProfileBadges.encode(listOf("001", "005", "018", "027")))
        assertEquals(emptyList<String>(), ProfileBadges.parse(" , "))
    }
}
