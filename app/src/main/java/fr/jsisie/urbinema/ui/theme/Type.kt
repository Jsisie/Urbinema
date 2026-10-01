package fr.jsisie.urbinema.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import fr.jsisie.urbinema.R

/*
 * The default families use reliable Android fallbacks. Local Bodoni Moda
 * and Inter resources can replace these aliases later without touching screens.
 */
val UrbinemaDisplayFamily = FontFamily.Serif
val UrbinemaTextFamily = FontFamily.SansSerif

private val SourceSerifFamily = FontFamily(
    Font(R.font.source_serif_4_medium, FontWeight.Medium),
)

private val SourceSansFamily = FontFamily(
    Font(R.font.source_sans_3_regular, FontWeight.Normal),
    Font(R.font.source_sans_3_semibold, FontWeight.SemiBold),
)

/** Typography scale for editorial display and highly readable body copy. */
val UrbinemaTypography = urbinemaTypography(UrbinemaDisplayFamily, UrbinemaTextFamily)

/** Source Serif 4 + Source Sans 3, used by the Cyanotype and Tirage themes. */
val SourceTypography = urbinemaTypography(SourceSerifFamily, SourceSansFamily)

private fun urbinemaTypography(
    display: FontFamily,
    text: FontFamily,
): Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = display,
        fontWeight = FontWeight.Medium,
        fontSize = 32.sp,
        lineHeight = 38.sp,
    ),
    displayMedium = TextStyle(
        fontFamily = display,
        fontWeight = FontWeight.Medium,
        fontSize = 24.sp,
        lineHeight = 30.sp,
    ),
    titleLarge = TextStyle(
        fontFamily = text,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp,
    ),
    titleMedium = TextStyle(
        fontFamily = text,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 24.sp,
    ),
    bodyLarge = TextStyle(
        fontFamily = text,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        lineHeight = 23.sp,
    ),
    bodyMedium = TextStyle(
        fontFamily = text,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 20.sp,
    ),
    labelMedium = TextStyle(
        fontFamily = text,
        fontWeight = FontWeight.SemiBold,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp,
    ),
)

val RankDisplayStyle: TextStyle
    @Composable get() = MaterialTheme.typography.displayLarge.copy(
        fontSize = 44.sp,
        lineHeight = 50.sp,
    )
