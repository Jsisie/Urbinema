package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/** Light palette: white / grey paper, blue reserved for ink. */
internal val TirageColors = UrbinemaColors(
    background = Color(0xFFF2F2F4),
    surface = Color(0xFFF6F6F7),
    surfaceElevated = Color(0xFFF9F9FA),
    surfacePressed = Color(0xFFE6E8EB),
    outline = Color(0xFFC7CBD0),
    onBackground = Color(0xFF1C1E21),
    onBackgroundMuted = Color(0xA81C1E21),
    onBackgroundFaint = Color(0x6B1C1E21),
    accent = Color(0xFF0B8A9E),
    accentMuted = Color(0xFF4A7C88),
    cool = Color(0xFF3D5A66),
    rare = Color(0xFF5A7180),
    danger = Color(0xFF9A3B45),
    isDark = false,
)

internal val TirageScheme = lightColorScheme(
    primary = TirageColors.accent,
    onPrimary = TirageColors.surfaceElevated,
    secondary = TirageColors.cool,
    background = TirageColors.background,
    onBackground = TirageColors.onBackground,
    surface = TirageColors.surface,
    onSurface = TirageColors.onBackground,
    surfaceVariant = TirageColors.surfaceElevated,
    onSurfaceVariant = TirageColors.onBackgroundMuted,
    outline = TirageColors.outline,
    error = TirageColors.danger,
)
