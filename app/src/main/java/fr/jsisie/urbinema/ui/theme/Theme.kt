package fr.jsisie.urbinema.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import fr.jsisie.urbinema.R

enum class UrbinemaThemeMode { Dark, Light, System, Cyanotype, Tirage, Rayonnage, Affiche, Velours, NuitAmericaine }

internal fun paletteFor(
    mode: UrbinemaThemeMode,
    systemDark: Boolean,
): UrbinemaColors = when (mode) {
    UrbinemaThemeMode.Dark -> SalleObscureColors
    UrbinemaThemeMode.Light -> SalleEclaireeColors
    UrbinemaThemeMode.System -> if (systemDark) SalleObscureColors else SalleEclaireeColors
    UrbinemaThemeMode.Cyanotype -> CyanotypeColors
    UrbinemaThemeMode.Tirage -> TirageColors
    UrbinemaThemeMode.Rayonnage -> RayonnageColors
    UrbinemaThemeMode.Affiche -> AfficheColors
    UrbinemaThemeMode.Velours -> VeloursColors
    UrbinemaThemeMode.NuitAmericaine -> NuitAmericaineColors
}

fun UrbinemaColors.previewSwatches(): List<Color> =
    listOf(background, accent, line, cool).distinct().take(3)

val UrbinemaThemeMode.labelRes: Int
    get() = when (this) {
        UrbinemaThemeMode.Dark -> R.string.dark_theme
        UrbinemaThemeMode.Light -> R.string.light_theme
        UrbinemaThemeMode.System -> R.string.system_theme
        UrbinemaThemeMode.Cyanotype -> R.string.theme_cyanotype
        UrbinemaThemeMode.Tirage -> R.string.theme_tirage
        UrbinemaThemeMode.Rayonnage -> R.string.theme_rayonnage
        UrbinemaThemeMode.Affiche -> R.string.theme_affiche
        UrbinemaThemeMode.Velours -> R.string.theme_velours
        UrbinemaThemeMode.NuitAmericaine -> R.string.theme_nuit_americaine
    }

/** Public access to semantic tokens selected by [UrbinemaTheme]. */
object UrbinemaThemeTokens {
    val colors: UrbinemaColors
        @Composable get() = LocalUrbinemaColors.current
    val dimens: UrbinemaDimens
        @Composable get() = LocalUrbinemaDimens.current
}

private data class ResolvedTheme(
    val colors: UrbinemaColors,
    val scheme: ColorScheme,
    val typography: Typography,
)

/** Applies one of the fixed palettes; dynamic color is intentionally unsupported. */
@Composable
fun UrbinemaTheme(
    mode: UrbinemaThemeMode = UrbinemaThemeMode.Dark,
    content: @Composable () -> Unit
) {
    val resolved = when (mode) {
        UrbinemaThemeMode.Dark -> ResolvedTheme(SalleObscureColors, SalleObscureScheme, UrbinemaTypography)
        UrbinemaThemeMode.Light -> ResolvedTheme(SalleEclaireeColors, SalleEclaireeScheme, UrbinemaTypography)
        UrbinemaThemeMode.System -> if (isSystemInDarkTheme()) {
            ResolvedTheme(SalleObscureColors, SalleObscureScheme, UrbinemaTypography)
        } else {
            ResolvedTheme(SalleEclaireeColors, SalleEclaireeScheme, UrbinemaTypography)
        }
        UrbinemaThemeMode.Cyanotype -> ResolvedTheme(CyanotypeColors, CyanotypeScheme, SourceTypography)
        UrbinemaThemeMode.Tirage -> ResolvedTheme(TirageColors, TirageScheme, SourceTypography)
        UrbinemaThemeMode.Rayonnage -> ResolvedTheme(RayonnageColors, RayonnageScheme, SourceTypography)
        UrbinemaThemeMode.Affiche -> ResolvedTheme(AfficheColors, AfficheScheme, SourceTypography)
        UrbinemaThemeMode.Velours -> ResolvedTheme(VeloursColors, VeloursScheme, SourceTypography)
        UrbinemaThemeMode.NuitAmericaine -> ResolvedTheme(NuitAmericaineColors, NuitAmericaineScheme, SourceTypography)
    }
    CompositionLocalProvider(LocalUrbinemaColors provides resolved.colors) {
        MaterialTheme(
            colorScheme = resolved.scheme,
            typography = resolved.typography,
            shapes = UrbinemaShapes,
            content = content,
        )
    }
}
