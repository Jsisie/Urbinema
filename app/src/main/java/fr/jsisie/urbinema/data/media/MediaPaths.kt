package fr.jsisie.urbinema.data.media

import android.content.res.AssetManager
import java.io.File

/**
 * Packaged and user-owned media locations.
 *
 * Drop a file named `{EDITORIAL_CODE}.webp`, `.png`, `.jpg` or `.jpeg` in the
 * matching `assets/media/{kind}/` folder. The UI looks it up by Room code
 * without requiring a JSON `mediaAssets` row. JSON wiring remains optional
 * for later kinds (badges, avatars, etc.).
 */
enum class MediaKind(val folder: String) {
    POSTER("posters"),
    COLLECTION("collections"),
    DIRECTOR("directors"),
    COUNTRY("countries"),
    CONTINENT("continents"),
    AVATAR("avatars"),
    BADGE("badges"),
    RANKING("rankings"),
}

object MediaPaths {
    const val ASSET_ROOT = "media"
    const val DEFAULT_EXTENSION = "webp"
    const val USER_AVATAR_RELATIVE = "media/users/avatar.webp"

    val IMAGE_EXTENSIONS = listOf("webp", "png", "jpg", "jpeg")
    val PACKAGED_AVATAR_CODES = (1..10).map { index ->
        "AVATAR_" + index.toString().padStart(2, '0')
    }

    fun packagedAsset(kind: MediaKind, editorialCode: String, extension: String = DEFAULT_EXTENSION): String =
        "$ASSET_ROOT/${kind.folder}/$editorialCode.$extension"

    fun folder(kind: MediaKind): String = "$ASSET_ROOT/${kind.folder}"

    /**
     * First matching image for [editorialCode] in [kind]'s asset folder.
     * Preference order: webp, png, jpg, jpeg. Comparison is case-insensitive.
     */
    fun resolveExisting(
        listFolder: (String) -> Array<String>?,
        kind: MediaKind,
        editorialCode: String,
    ): String? {
        val folder = folder(kind)
        val names = listFolder(folder)?.associateBy { it.lowercase() }.orEmpty()
        for (extension in IMAGE_EXTENSIONS) {
            val actual = names["${editorialCode.lowercase()}.$extension"] ?: continue
            return "$folder/$actual"
        }
        return null
    }

    fun resolveExisting(assets: AssetManager, kind: MediaKind, editorialCode: String): String? =
        resolveExisting(assets::list, kind, editorialCode)

    fun userAvatarFile(filesDir: File): File = File(filesDir, USER_AVATAR_RELATIVE)

    fun userAvatarCode(userId: Long): String = "USER_AVATAR_$userId"
}
