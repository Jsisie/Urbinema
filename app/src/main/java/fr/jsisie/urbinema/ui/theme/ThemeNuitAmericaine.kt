package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

/**
 * Day-for-night: indigo storm, moonlight steel, tungsten copper.
 * Dark without the default black-and-gold pair.
 */
internal val NuitAmericaineColors = UrbinemaColors(
    background = Color(0xFF0B1018),
    surface = Color(0xFF141C28),
    surfaceElevated = Color(0xFF1C2636),
    surfacePressed = Color(0xFF263244),
    outline = Color(0xFF334158),
    onBackground = Color(0xFFDDE6F0),
    onBackgroundMuted = Color(0x9EDDE6F0),
    onBackgroundFaint = Color(0x61DDE6F0),
    accent = Color(0xFFE08A58),
    accentMuted = Color(0xFFB86E48),
    line = Color(0xFF7FA3C4),
    progress = Color(0xFF8FB4D0),
    cool = Color(0xFF6A90A8),
    rare = Color(0xFFC5D4E4),
    danger = Color(0xFFC45C6A),
    isDark = true,
)

internal val NuitAmericaineScheme = darkColorScheme(
    primary = NuitAmericaineColors.accent,
    onPrimary = NuitAmericaineColors.background,
    secondary = NuitAmericaineColors.cool,
    background = NuitAmericaineColors.background,
    onBackground = NuitAmericaineColors.onBackground,
    surface = NuitAmericaineColors.surface,
    onSurface = NuitAmericaineColors.onBackground,
    surfaceVariant = NuitAmericaineColors.surfaceElevated,
    onSurfaceVariant = NuitAmericaineColors.onBackgroundMuted,
    outline = NuitAmericaineColors.outline,
    error = NuitAmericaineColors.danger,
)
