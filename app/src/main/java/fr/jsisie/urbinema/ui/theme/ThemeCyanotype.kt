package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

/** Dark palette: Prussian night, pale writing, bronze for strokes only. */
internal val CyanotypeColors = UrbinemaColors(
    background = Color(0xFF0E1C24),
    surface = Color(0xFF152630),
    surfaceElevated = Color(0xFF1C3240),
    surfacePressed = Color(0xFF254050),
    outline = Color(0xFF2E5160),
    onBackground = Color(0xFFE6F0F2),
    onBackgroundMuted = Color(0x9EE6F0F2),
    onBackgroundFaint = Color(0x61E6F0F2),
    accent = Color(0xFF5ED4C4),
    accentMuted = Color(0xFF3E9A8E),
    line = Color(0xFFC46A4A),
    cool = Color(0xFF6BA3B5),
    rare = Color(0xFFB7D4DC),
    danger = Color(0xFFC45C6A),
    isDark = true,
)

internal val CyanotypeScheme = darkColorScheme(
    primary = CyanotypeColors.accent,
    onPrimary = CyanotypeColors.background,
    secondary = CyanotypeColors.cool,
    background = CyanotypeColors.background,
    onBackground = CyanotypeColors.onBackground,
    surface = CyanotypeColors.surface,
    onSurface = CyanotypeColors.onBackground,
    surfaceVariant = CyanotypeColors.surfaceElevated,
    onSurfaceVariant = CyanotypeColors.onBackgroundMuted,
    outline = CyanotypeColors.outline,
    error = CyanotypeColors.danger,
)
