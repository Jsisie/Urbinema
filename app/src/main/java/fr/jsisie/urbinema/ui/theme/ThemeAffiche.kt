package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

/**
 * Festival poster palette: ink navy, cream, vermillion, mustard, teal.
 * Inspired by film-festival print and apps that let more than two hues speak.
 */
internal val AfficheColors = UrbinemaColors(
    background = Color(0xFF161B2C),
    surface = Color(0xFF1E2538),
    surfaceElevated = Color(0xFF272F45),
    surfacePressed = Color(0xFF323B54),
    outline = Color(0xFF3E4860),
    onBackground = Color(0xFFF3EDE4),
    onBackgroundMuted = Color(0x9EF3EDE4),
    onBackgroundFaint = Color(0x61F3EDE4),
    accent = Color(0xFFE6B84D),
    accentMuted = Color(0xFFC4A45A),
    line = Color(0xFFE45B4A),
    cool = Color(0xFF3AA39A),
    rare = Color(0xFFF0C9A0),
    danger = Color(0xFFE45B4A),
    isDark = true,
)

internal val AfficheScheme = darkColorScheme(
    primary = AfficheColors.accent,
    onPrimary = AfficheColors.background,
    secondary = AfficheColors.cool,
    background = AfficheColors.background,
    onBackground = AfficheColors.onBackground,
    surface = AfficheColors.surface,
    onSurface = AfficheColors.onBackground,
    surfaceVariant = AfficheColors.surfaceElevated,
    onSurfaceVariant = AfficheColors.onBackgroundMuted,
    outline = AfficheColors.outline,
    error = AfficheColors.danger,
)
