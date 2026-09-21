package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/** Values for the paper-inspired “Salle éclairée” theme. */
internal val SalleEclaireeColors = UrbinemaColors(
    background = Color(0xFFF5F1E8),
    surface = Color(0xFFFBF8F1),
    surfaceElevated = Color(0xFFFFFFFF),
    surfacePressed = Color(0xFFEBE5D8),
    outline = Color(0xFFDCD4C4),
    onBackground = Color(0xFF17171B),
    onBackgroundMuted = Color(0xA817171B),
    onBackgroundFaint = Color(0x6B17171B),
    accent = Color(0xFF8A6A2F),
    accentMuted = Color(0xFFB39B6E),
    cool = Color(0xFF3E5A70),
    rare = Color(0xFF5A6B7A),
    danger = Color(0xFF8E3F36),
)

internal val SalleEclaireeScheme = lightColorScheme(
    primary = SalleEclaireeColors.accent,
    onPrimary = SalleEclaireeColors.surfaceElevated,
    secondary = SalleEclaireeColors.cool,
    background = SalleEclaireeColors.background,
    onBackground = SalleEclaireeColors.onBackground,
    surface = SalleEclaireeColors.surface,
    onSurface = SalleEclaireeColors.onBackground,
    surfaceVariant = SalleEclaireeColors.surfaceElevated,
    onSurfaceVariant = SalleEclaireeColors.onBackgroundMuted,
    outline = SalleEclaireeColors.outline,
    error = SalleEclaireeColors.danger,
)
