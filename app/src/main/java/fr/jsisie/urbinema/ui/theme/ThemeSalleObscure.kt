package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color

/** Values for the default “Salle obscure” theme. */
internal val SalleObscureColors = UrbinemaColors(
    background = Color(0xFF0A0A0C),
    surface = Color(0xFF131317),
    surfaceElevated = Color(0xFF1C1C22),
    surfacePressed = Color(0xFF26262E),
    outline = Color(0xFF2E2E37),
    onBackground = Color(0xFFF4EFE6),
    onBackgroundMuted = Color(0x9EF4EFE6),
    onBackgroundFaint = Color(0x61F4EFE6),
    accent = Color(0xFFE8C68A),
    accentMuted = Color(0xFFA8895A),
    cool = Color(0xFF6E8FA8),
    rare = Color(0xFFC9D6E3),
    danger = Color(0xFFB4635A),
)

internal val SalleObscureScheme = darkColorScheme(
    primary = SalleObscureColors.accent,
    onPrimary = SalleObscureColors.background,
    secondary = SalleObscureColors.cool,
    background = SalleObscureColors.background,
    onBackground = SalleObscureColors.onBackground,
    surface = SalleObscureColors.surface,
    onSurface = SalleObscureColors.onBackground,
    surfaceVariant = SalleObscureColors.surfaceElevated,
    onSurfaceVariant = SalleObscureColors.onBackgroundMuted,
    outline = SalleObscureColors.outline,
    error = SalleObscureColors.danger,
)
