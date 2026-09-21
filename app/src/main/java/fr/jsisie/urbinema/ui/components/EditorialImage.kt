package fr.jsisie.urbinema.ui.components

import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import fr.jsisie.urbinema.data.media.MediaKind
import fr.jsisie.urbinema.data.media.MediaPaths

/**
 * Loads a packaged editorial image by Room code.
 * Looks for `{CODE}.webp`, `.png`, `.jpg` or `.jpeg` in `assets/media/{kind}/`.
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
    val path = remember(kind, code) { MediaPaths.resolveExisting(context.assets, kind, code) }
    val bitmap = remember(path) {
        path?.let { asset ->
            runCatching {
                context.assets.open(asset).use { BitmapFactory.decodeStream(it) }
            }.getOrNull()
        }
    }
    val grayFilter = remember(grayscale) {
        if (grayscale) ColorFilter.colorMatrix(ColorMatrix().apply { setToSaturation(0f) }) else null
    }
    Box(modifier, contentAlignment = Alignment.Center) {
        if (bitmap != null) {
            Image(
                bitmap = bitmap.asImageBitmap(),
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
