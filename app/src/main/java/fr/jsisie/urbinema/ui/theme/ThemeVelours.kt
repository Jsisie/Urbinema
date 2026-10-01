package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

/** Cinema velvet: wine seats, cream paper, blush ink, dusty sage. */
internal val VeloursColors = UrbinemaColors(
    background = Color(0xFF241318),
    surface = Color(0xFF2E1A22),
    surfaceElevated = Color(0xFF3A222C),
    surfacePressed = Color(0xFF462833),
    outline = Color(0xFF5A3542),
    onBackground = Color(0xFFF4E8E4),
    onBackgroundMuted = Color(0x9EF4E8E4),
    onBackgroundFaint = Color(0x61F4E8E4),
    accent = Color(0xFFE8A8A0),
    accentMuted = Color(0xFFC4847C),
    line = Color(0xFFC45C6A),
    cool = Color(0xFF7A9B8C),
    rare = Color(0xFFD4C0B8),
    danger = Color(0xFFC45C6A),
    isDark = true,
)

internal val VeloursScheme = darkColorScheme(
    primary = VeloursColors.accent,
    onPrimary = VeloursColors.background,
    secondary = VeloursColors.cool,
    background = VeloursColors.background,
    onBackground = VeloursColors.onBackground,
    surface = VeloursColors.surface,
    onSurface = VeloursColors.onBackground,
    surfaceVariant = VeloursColors.surfaceElevated,
    onSurfaceVariant = VeloursColors.onBackgroundMuted,
    outline = VeloursColors.outline,
    error = VeloursColors.danger,
)
