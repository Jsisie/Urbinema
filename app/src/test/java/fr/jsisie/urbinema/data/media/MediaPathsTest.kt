package fr.jsisie.urbinema.data.media

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class MediaPathsTest {
    @Test
    fun `prefers webp then png then jpeg aliases`() {
        val files = arrayOf("_keep.txt", "TITANIC_1997.PNG", "TITANIC_1997.jpg")
        assertEquals(
            "media/posters/TITANIC_1997.PNG",
            MediaPaths.resolveExisting({ files }, MediaKind.POSTER, "TITANIC_1997"),
        )
    }

    @Test
    fun `returns webp when several formats exist`() {
        val files = arrayOf("TITANIC_1997.webp", "TITANIC_1997.png")
        assertEquals(
            "media/posters/TITANIC_1997.webp",
            MediaPaths.resolveExisting({ files }, MediaKind.POSTER, "TITANIC_1997"),
        )
    }

    @Test
    fun `missing file stays null so the UI can keep the placeholder`() {
        assertNull(
            MediaPaths.resolveExisting({ emptyArray() }, MediaKind.POSTER, "TITANIC_1997"),
        )
    }

    @Test
    fun `packaged path stays relative to assets root`() {
        assertEquals(
            "media/posters/TITANIC_1997.webp",
            MediaPaths.packagedAsset(MediaKind.POSTER, "TITANIC_1997"),
        )
    }

    @Test
    fun `badge codes resolve jpeg in the badges folder`() {
        val files = arrayOf("_keep.txt", "001.jpeg")
        assertEquals(
            "media/badges/001.jpeg",
            MediaPaths.resolveExisting({ files }, MediaKind.BADGE, "001"),
        )
    }

    @Test
    fun `packaged avatars resolve like posters`() {
        val files = arrayOf("AVATAR_01.jpeg", "AVATAR_02.png")
        assertEquals(
            "media/avatars/AVATAR_01.jpeg",
            MediaPaths.resolveExisting({ files }, MediaKind.AVATAR, "AVATAR_01"),
        )
        assertEquals(
            (1..10).map { "AVATAR_" + it.toString().padStart(2, '0') },
            MediaPaths.PACKAGED_AVATAR_CODES,
        )
    }

    @Test
    fun `all ten packaged avatars exist in assets`() {
        val folder = java.io.File("src/main/assets/media/avatars")
        assertTrue("Missing avatars folder at ${folder.absolutePath}", folder.isDirectory)
        val names = folder.list().orEmpty().map { it.lowercase() }.toSet()
        MediaPaths.PACKAGED_AVATAR_CODES.forEach { code ->
            val present = MediaPaths.IMAGE_EXTENSIONS.any { ext ->
                "${code.lowercase()}.$ext" in names
            }
            assertTrue("$code missing from ${folder.absolutePath}", present)
        }
    }
}
