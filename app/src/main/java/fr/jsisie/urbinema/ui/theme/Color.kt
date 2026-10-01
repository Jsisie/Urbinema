package fr.jsisie.urbinema.ui.theme

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/** Semantic palette consumed by Urbinema UI instead of literal colors. */
@Immutable
data class UrbinemaColors(
    val background: Color,
    val surface: Color,
    val surfaceElevated: Color,
    val surfacePressed: Color,
    val outline: Color,
    val onBackground: Color,
    val onBackgroundMuted: Color,
    val onBackgroundFaint: Color,
    val accent: Color,
    val accentMuted: Color,
    val line: Color = accent,
    val progress: Color = line,
    val cool: Color,
    val rare: Color,
    val danger: Color,
    val isDark: Boolean,
)

internal val LocalUrbinemaColors = staticCompositionLocalOf { SalleObscureColors }