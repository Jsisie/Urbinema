package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/** Warm library / wood archive: parchment, moss, walnut. */
internal val RayonnageColors = UrbinemaColors(
    background = Color(0xFFEFE8DC),
    surface = Color(0xFFF6F1E7),
    surfaceElevated = Color(0xFFFFFBF4),
    surfacePressed = Color(0xFFDCC4A4),
    outline = Color(0xFFC4A078),
    onBackground = Color(0xFF3A2416),
    onBackgroundMuted = Color(0xA83A2416),
    onBackgroundFaint = Color(0x6B3A2416),
    accent = Color(0xFF3D6B46),
    accentMuted = Color(0xFF6E8F6F),
    line = Color(0xFF7A3F1E),
    progress = Color(0xFF8B5E3C),
    cool = Color(0xFF5A6B52),
    rare = Color(0xFF7A8B70),
    danger = Color(0xFF9A4338),
    isDark = false,
)

internal val RayonnageScheme = lightColorScheme(
    primary = RayonnageColors.accent,
    onPrimary = RayonnageColors.surfaceElevated,
    secondary = RayonnageColors.cool,
    background = RayonnageColors.background,
    onBackground = RayonnageColors.onBackground,
    surface = RayonnageColors.surface,
    onSurface = RayonnageColors.onBackground,
    surfaceVariant = RayonnageColors.surfaceElevated,
    onSurfaceVariant = RayonnageColors.onBackgroundMuted,
    outline = RayonnageColors.outline,
    error = RayonnageColors.danger,
)
