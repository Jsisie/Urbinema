package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/*
 * The families deliberately use reliable Android fallbacks. Local Bodoni Moda
 * and Inter resources can replace these aliases later without touching screens.
 */
val UrbinemaDisplayFamily = FontFamily.Serif
val UrbinemaTextFamily = FontFamily.SansSerif

/** Typography scale for editorial display and highly readable body copy. */
val UrbinemaTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = UrbinemaDisplayFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 32.sp,
        lineHeight = 38.sp,
    ),
    displayMedium = TextStyle(
        fontFamily = UrbinemaDisplayFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 24.sp,
        lineHeight = 30.sp,
    ),
    titleLarge = TextStyle(
        fontFamily = UrbinemaTextFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp,
    ),
    titleMedium = TextStyle(
        fontFamily = UrbinemaTextFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 24.sp,
    ),
    bodyLarge = TextStyle(
        fontFamily = UrbinemaTextFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        lineHeight = 23.sp,
    ),
    bodyMedium = TextStyle(
        fontFamily = UrbinemaTextFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 20.sp,
    ),
    labelMedium = TextStyle(
        fontFamily = UrbinemaTextFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp,
    ),
)

val RankDisplayStyle = TextStyle(
    fontFamily = UrbinemaDisplayFamily,
    fontWeight = FontWeight.Medium,
    fontSize = 44.sp,
    lineHeight = 50.sp,
)