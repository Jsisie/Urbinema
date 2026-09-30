package fr.jsisie.urbinema.ui.components

import android.graphics.BitmapFactory
import android.util.LruCache
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.runtime.Composable
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import fr.jsisie.urbinema.data.media.MediaKind
import fr.jsisie.urbinema.data.media.MediaPaths
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Loads a packaged editorial image by Room code.
 * Looks for `{CODE}.webp`, `.png`, `.jpg` or `.jpeg` in `assets/media/{kind}/`.
 * Decode stays off the main thread so opening a fiche does not wait on the JPEG.
 */
@Composable
fun EditorialImage(
    kind: MediaKind,
    code: String,
    contentDescription: String?,
    modifier: Modifier = Modifier,
    contentScale: ContentScale = ContentScale.Crop,
    grayscale: Boolean = false,
    placeholder: @Composable BoxScope.() -> Unit,
) {
    val context = LocalContext.current
    val bitmap = produceState<ImageBitmap?>(null, kind, code) {
        val cached = EditorialBitmapCache.get(kind, code)
        if (cached != null) {
            value = cached
            return@produceState
        }
        value = withContext(Dispatchers.IO) {
            val path = MediaPaths.resolveExisting(context.assets, kind, code) ?: return@withContext null
            runCatching {
                context.assets.open(path).use { BitmapFactory.decodeStream(it) }?.asImageBitmap()
            }.getOrNull()?.also { EditorialBitmapCache.put(kind, code, it) }
        }
    }
    val grayFilter = remember(grayscale) {
        if (grayscale) ColorFilter.colorMatrix(ColorMatrix().apply { setToSaturation(0f) }) else null
    }
    Box(modifier, contentAlignment = Alignment.Center) {
        val image = bitmap.value
        if (image != null) {
            Image(
                bitmap = image,
                contentDescription = contentDescription,
                modifier = Modifier.matchParentSize(),
                contentScale = contentScale,
                colorFilter = grayFilter,
            )
        } else {
            placeholder()
        }
    }
}

private object EditorialBitmapCache {
    private val bitmaps = LruCache<String, ImageBitmap>(48)

    fun get(kind: MediaKind, code: String): ImageBitmap? = bitmaps.get(key(kind, code))

    fun put(kind: MediaKind, code: String, bitmap: ImageBitmap) {
        bitmaps.put(key(kind, code), bitmap)
    }

    private fun key(kind: MediaKind, code: String) = "${kind.name}:$code"
}
