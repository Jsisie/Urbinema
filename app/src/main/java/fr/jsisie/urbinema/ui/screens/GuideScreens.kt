package fr.jsisie.urbinema.ui.screens

import android.graphics.drawable.ColorDrawable
import android.os.Build
import android.view.WindowManager
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.ui.components.SectionTitle
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens

private val confettiPalette = listOf(
    Color(0xFFE8C68A),
    Color(0xFF7A5CB8),
    Color(0xFFE07A5F),
    Color(0xFF5EC8D8),
    Color(0xFFF4EFE6),
)

private fun DrawScope.drawConfetti(shift: Float) {
    repeat(36) { index ->
        val x = ((index * 97) % 1000) / 1000f * size.width
        val y = ((shift + index / 36f) % 1f) * size.height
        drawCircle(confettiPalette[index % confettiPalette.size], radius = 5f + (index % 3) * 2f, center = Offset(x, y))
    }
}

@Composable
fun AppGuideDialog(onFinished: () -> Unit) {
    val pages = listOf(
        R.string.guide_page_intro to R.string.guide_body_intro,
        R.string.guide_page_home to R.string.guide_body_home,
        R.string.guide_page_atlas to R.string.guide_body_atlas,
        R.string.guide_page_collections to R.string.guide_body_collections,
        R.string.guide_page_journey to R.string.guide_body_journey,
        R.string.guide_page_profile to R.string.guide_body_profile,
    )
    val page = androidx.compose.runtime.remember { androidx.compose.runtime.mutableIntStateOf(0) }
    val last = page.intValue == pages.lastIndex
    // Resolved outside the dialog window so the in-app language applies.
    val title = stringResource(pages[page.intValue].first)
    val body = stringResource(pages[page.intValue].second)
    val count = stringResource(R.string.guide_page_count, page.intValue + 1, pages.size)
    val skip = stringResource(R.string.guide_skip)
    val action = stringResource(if (last) R.string.guide_done else R.string.guide_next)
    val colors = UrbinemaThemeTokens.colors
    Dialog(
        onDismissRequest = {},
        properties = DialogProperties(usePlatformDefaultWidth = false, dismissOnBackPress = false, dismissOnClickOutside = false),
    ) {
        val dialogView = LocalView.current
        SideEffect {
            val window = (dialogView.parent as? DialogWindowProvider)?.window ?: return@SideEffect
            window.setBackgroundDrawable(ColorDrawable(android.graphics.Color.TRANSPARENT))
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                window.addFlags(WindowManager.LayoutParams.FLAG_BLUR_BEHIND)
                window.setDimAmount(0.2f)
                window.setBackgroundBlurRadius(120)
                window.attributes = window.attributes.apply { blurBehindRadius = 120 }
            } else {
                window.setDimAmount(0.72f)
            }
        }
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Surface(
                modifier = Modifier
                    .padding(horizontal = 24.dp)
                    .widthIn(max = 480.dp)
                    .fillMaxWidth()
                    .fillMaxHeight(0.6f),
                shape = MaterialTheme.shapes.large,
                color = colors.surface,
                contentColor = colors.onBackground,
            ) {
                Column(Modifier.padding(24.dp)) {
                    Column(
                        Modifier
                            .weight(1f)
                            .verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.Center,
                    ) {
                        Text(
                            title,
                            style = MaterialTheme.typography.displayMedium,
                            color = colors.onBackground,
                            textAlign = TextAlign.Start,
                        )
                        Text(
                            body,
                            modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.lg),
                            style = MaterialTheme.typography.bodyLarge,
                            color = colors.onBackgroundMuted,
                        )
                        Text(
                            count,
                            modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.xl),
                            color = colors.onBackgroundFaint,
                        )
                    }
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .padding(top = UrbinemaThemeTokens.dimens.md),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        TextButton(onClick = onFinished) { Text(skip, color = colors.onBackground) }
                        Button(onClick = {
                            if (last) onFinished() else page.intValue += 1
                        }) {
                            Text(action)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RankUpDialog(rankName: String, onDismiss: () -> Unit) {
    val title = stringResource(R.string.rank_up_title)
    val body = stringResource(R.string.rank_up_body, rankName)
    val confirm = stringResource(R.string.confirm)
    val colors = UrbinemaThemeTokens.colors
    val shift by rememberInfiniteTransition(label = "rank-confetti").animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(2_200, easing = LinearEasing)),
        label = "fall",
    )
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Box(
            Modifier
                .fillMaxSize()
                .drawWithContent {
                    drawContent()
                    drawConfetti(shift)
                },
            contentAlignment = Alignment.Center,
        ) {
            Surface(
                modifier = Modifier
                    .padding(horizontal = 28.dp)
                    .widthIn(max = 420.dp)
                    .fillMaxWidth(),
                shape = MaterialTheme.shapes.large,
                color = colors.surface,
                contentColor = colors.onBackground,
            ) {
                Column(
                    Modifier.padding(28.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
                ) {
                    Text(
                        title,
                        style = MaterialTheme.typography.displayMedium,
                        color = colors.onBackground,
                        textAlign = TextAlign.Center,
                    )
                    Text(
                        body,
                        style = MaterialTheme.typography.bodyLarge,
                        color = colors.onBackgroundMuted,
                        textAlign = TextAlign.Center,
                    )
                    Button(onClick = onDismiss) { Text(confirm) }
                }
            }
        }
    }
}

@Composable
fun SourcesScreen() {
    LazyColumn(
        Modifier.fillMaxSize().background(UrbinemaThemeTokens.colors.background),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        item { ScreenTitle(R.string.sources_title) }
        item { Text(stringResource(R.string.sources_intro), color = UrbinemaThemeTokens.colors.onBackgroundMuted) }
        item { SectionTitle(R.string.sources_books) }
        item { Text(stringResource(R.string.sources_book_allard)) }
        item { Text(stringResource(R.string.sources_book_muller)) }
        item { Text(stringResource(R.string.sources_book_philippe)) }
        item { Text(stringResource(R.string.sources_book_sadoul)) }
        item { Text(stringResource(R.string.sources_book_karthala)) }
        item { Text(stringResource(R.string.sources_book_ginsberg)) }
        item { Text(stringResource(R.string.sources_book_pinel)) }
        item { Text(stringResource(R.string.sources_book_thon)) }
        item { SectionTitle(R.string.sources_sites) }
        item { Text(stringResource(R.string.sources_site_tspdt)) }
        item { Text(stringResource(R.string.sources_site_letterboxd)) }
        item { Text(stringResource(R.string.sources_site_imdb)) }
        item { Text(stringResource(R.string.sources_site_senscritique)) }
        item { Text(stringResource(R.string.sources_site_sight)) }
        item { Text(stringResource(R.string.sources_site_ebert)) }
        item { Text(stringResource(R.string.sources_site_festivals)) }
        item { Text(stringResource(R.string.sources_site_kmdb)) }
        item { Text(stringResource(R.string.sources_site_cahiers)) }
        item { Text(stringResource(R.string.sources_site_criticism)) }
        item { Text(stringResource(R.string.sources_site_tmdb)) }
    }
}
