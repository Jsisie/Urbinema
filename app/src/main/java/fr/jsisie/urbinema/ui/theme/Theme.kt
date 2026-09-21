package fr.jsisie.urbinema.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

enum class UrbinemaThemeMode { Dark, Light, System }

/** Public access to semantic tokens selected by [UrbinemaTheme]. */
object UrbinemaThemeTokens {
    val colors: UrbinemaColors
        @Composable get() = LocalUrbinemaColors.current
    val dimens: UrbinemaDimens
        @Composable get() = LocalUrbinemaDimens.current
}

/** Applies one of the two fixed palettes; dynamic color is intentionally unsupported. */
@Composable
fun UrbinemaTheme(
    mode: UrbinemaThemeMode = UrbinemaThemeMode.Dark,
    content: @Composable () -> Unit
) {
    val darkTheme = when (mode) {
        UrbinemaThemeMode.Dark -> true
        UrbinemaThemeMode.Light -> false
        UrbinemaThemeMode.System -> isSystemInDarkTheme()
    }
    val colors = if (darkTheme) SalleObscureColors else SalleEclaireeColors
    CompositionLocalProvider(LocalUrbinemaColors provides colors) {
        MaterialTheme(
            colorScheme = if (darkTheme) SalleObscureScheme else SalleEclaireeScheme,
            typography = UrbinemaTypography,
            shapes = UrbinemaShapes,
            content = content,
        )
    }
}