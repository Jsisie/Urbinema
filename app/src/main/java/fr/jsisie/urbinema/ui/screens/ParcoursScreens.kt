package fr.jsisie.urbinema.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Image
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.data.media.MediaKind
import fr.jsisie.urbinema.ui.components.EditorialImage
import fr.jsisie.urbinema.ui.model.PathStepUi
import fr.jsisie.urbinema.ui.model.PathUi
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens

/** List of pedagogical paths. One large panel per path, not a collection card. */
@Composable
fun PathsScreen(paths: List<PathUi>, resetTick: Int = 0, onPath: (String) -> Unit) {
    val listState = rememberLazyListState()
    LaunchedEffect(resetTick) {
        if (resetTick == 0) return@LaunchedEffect
        listState.scrollToItem(0)
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize().background(UrbinemaThemeTokens.colors.background),
        state = listState,
        contentPadding = PaddingValues(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.lg),
    ) {
        item { ScreenTitle(R.string.progress) }
        items(paths, key = { it.id }) { path ->
            PathListPanel(path, onClick = { onPath(path.id) })
        }
    }
}

@Composable
private fun PathListPanel(path: PathUi, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(28.dp))
            .background(UrbinemaThemeTokens.colors.surface)
            .clickable(onClick = onClick)
            .padding(UrbinemaThemeTokens.dimens.lg),
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
    ) {
        Box(
            Modifier
                .width(3.dp)
                .height(148.dp)
                .background(UrbinemaThemeTokens.colors.line),
        )
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm)) {
            Text(
                path.periodLabel,
                style = MaterialTheme.typography.labelMedium,
                color = UrbinemaThemeTokens.colors.accent,
            )
            Text(path.name, style = MaterialTheme.typography.headlineMedium)
            Text(
                path.summary,
                style = MaterialTheme.typography.bodyLarge,
                color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                maxLines = 4,
            )
            Row(horizontalArrangement = Arrangement.spacedBy((-10).dp)) {
                path.steps.take(6).forEach { step ->
                    MovementBubble(step.imageCode, step.name, Modifier.size(36.dp))
                }
            }
        }
    }
}

/** Vertical chain of current bubbles. A "?" on the line opens the transition. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PathDetailScreen(
    path: PathUi,
    onMovie: (String) -> Unit,
    onDirector: (String) -> Unit,
) {
    var openedStep by rememberSaveable { mutableStateOf<String?>(null) }
    var openedTransition by rememberSaveable { mutableStateOf<Int?>(null) }
    val step = path.steps.firstOrNull { it.id == openedStep }
    val transition = openedTransition?.let { index -> path.steps.getOrNull(index)?.transition }
    val localizedContext = LocalContext.current
    val localizedConfiguration = LocalConfiguration.current
    if (transition != null) {
        Dialog(onDismissRequest = { openedTransition = null }) {
            Surface(
                modifier = Modifier
                    .padding(horizontal = 40.dp)
                    .widthIn(max = 280.dp),
                shape = MaterialTheme.shapes.medium,
                color = UrbinemaThemeTokens.colors.surfaceElevated,
                contentColor = UrbinemaThemeTokens.colors.onBackground,
            ) {
                Text(
                    transition,
                    modifier = Modifier.padding(UrbinemaThemeTokens.dimens.md),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
    if (step != null) {
        ModalBottomSheet(
            onDismissRequest = { openedStep = null },
            sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
            containerColor = UrbinemaThemeTokens.colors.surface,
        ) {
            CompositionLocalProvider(
                LocalContext provides localizedContext,
                LocalConfiguration provides localizedConfiguration,
            ) {
                PathStepSheet(step, onMovie, onDirector)
            }
        }
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize().background(UrbinemaThemeTokens.colors.background),
        contentPadding = PaddingValues(UrbinemaThemeTokens.dimens.screen),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        item {
            Text(
                path.periodLabel,
                style = MaterialTheme.typography.labelMedium,
                color = UrbinemaThemeTokens.colors.accent,
                modifier = Modifier.fillMaxWidth(),
            )
            Text(
                path.name,
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = UrbinemaThemeTokens.dimens.xs, bottom = UrbinemaThemeTokens.dimens.md),
            )
            Text(
                path.description,
                color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = UrbinemaThemeTokens.dimens.xl),
            )
        }
        items(path.steps.size, key = { path.steps[it].id }) { index ->
            val current = path.steps[index]
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                MovementBubble(
                    code = current.imageCode,
                    name = current.name,
                    modifier = Modifier
                        .size(132.dp)
                        .clickable { openedStep = current.id },
                )
                Text(
                    current.name,
                    style = MaterialTheme.typography.titleMedium,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .padding(top = UrbinemaThemeTokens.dimens.sm)
                        .width(220.dp)
                        .clickable { openedStep = current.id },
                )
                Text(
                    current.periodLabel,
                    style = MaterialTheme.typography.labelMedium,
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.xxs),
                )
                if (!current.transition.isNullOrBlank()) {
                    TransitionLink(onClick = { openedTransition = index })
                }
            }
        }
    }
}

@Composable
private fun TransitionLink(onClick: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier
                .padding(top = UrbinemaThemeTokens.dimens.sm)
                .width(1.dp)
                .height(28.dp)
                .background(UrbinemaThemeTokens.colors.line.copy(alpha = 0.7f)),
        )
        Box(
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .border(1.dp, UrbinemaThemeTokens.colors.line, CircleShape)
                .clickable(onClick = onClick),
            contentAlignment = Alignment.Center,
        ) {
            Text("?", color = UrbinemaThemeTokens.colors.accent, style = MaterialTheme.typography.titleMedium)
        }
        Box(
            Modifier
                .padding(bottom = UrbinemaThemeTokens.dimens.sm)
                .width(1.dp)
                .height(28.dp)
                .background(UrbinemaThemeTokens.colors.line.copy(alpha = 0.7f)),
        )
    }
}

@Composable
private fun MovementBubble(code: String, name: String, modifier: Modifier = Modifier) {
    EditorialImage(
        kind = MediaKind.MOVEMENT,
        code = code,
        contentDescription = name,
        modifier = modifier
            .clip(CircleShape)
            .border(1.dp, UrbinemaThemeTokens.colors.line.copy(alpha = 0.45f), CircleShape),
    ) {
        Box(Modifier.fillMaxSize().background(UrbinemaThemeTokens.colors.background), contentAlignment = Alignment.Center) {
            Icon(Icons.Outlined.Image, name, Modifier.size(22.dp), tint = UrbinemaThemeTokens.colors.onBackgroundMuted)
        }
    }
}

@Composable
private fun PathStepSheet(
    step: PathStepUi,
    onMovie: (String) -> Unit,
    onDirector: (String) -> Unit,
) {
    val maxSheet = (LocalConfiguration.current.screenHeightDp * 0.9f).dp
    Column(
        Modifier
            .fillMaxWidth()
            .heightIn(max = maxSheet)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = UrbinemaThemeTokens.dimens.screen, vertical = UrbinemaThemeTokens.dimens.md),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        Text(step.name, style = MaterialTheme.typography.headlineMedium)
        Text(step.periodLabel, color = UrbinemaThemeTokens.colors.accent, style = MaterialTheme.typography.labelMedium)
        Text(
            editorialInline(step.description),
            color = UrbinemaThemeTokens.colors.onBackgroundMuted,
            modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.sm, bottom = UrbinemaThemeTokens.dimens.md),
        )
        if (step.facts.isNotEmpty()) {
            Text(stringResource(R.string.path_facts), style = MaterialTheme.typography.titleMedium)
            step.facts.forEach { fact ->
                Text(editorialInline(fact.title), style = MaterialTheme.typography.titleSmall)
                Text(editorialInline(fact.body), color = UrbinemaThemeTokens.colors.onBackgroundMuted)
            }
        }
        if (step.figures.isNotEmpty()) {
            Text(
                stringResource(R.string.path_figures),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.md),
            )
            step.figures.forEach { figure ->
                val label = editorialInline("${figure.name} — ${figure.role}")
                if (figure.directorCode != null) {
                    Text(
                        label,
                        color = UrbinemaThemeTokens.colors.accent,
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onDirector(figure.directorCode) }
                            .padding(vertical = UrbinemaThemeTokens.dimens.xxs),
                    )
                } else {
                    Text(label, modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.xxs))
                }
            }
        }
        if (step.movies.isNotEmpty()) {
            Text(
                stringResource(R.string.path_films),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.md),
            )
            step.movies.forEach { movie ->
                Text(
                    "${movie.title} (${movie.year})",
                    color = UrbinemaThemeTokens.colors.accent,
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onMovie(movie.id) }
                        .padding(vertical = UrbinemaThemeTokens.dimens.xxs),
                )
            }
        }
    }
}

/** `**gras**` and `*italique*` from the path source, without leaving the stars on screen. */
private fun editorialInline(source: String): AnnotatedString = buildAnnotatedString {
    var index = 0
    while (index < source.length) {
        if (source.startsWith("**", index)) {
            val end = source.indexOf("**", index + 2)
            if (end > index) {
                withStyle(SpanStyle(fontWeight = FontWeight.SemiBold)) {
                    append(source.substring(index + 2, end))
                }
                index = end + 2
                continue
            }
        }
        if (source[index] == '*') {
            val end = source.indexOf('*', index + 1)
            if (end > index) {
                withStyle(SpanStyle(fontStyle = FontStyle.Italic)) {
                    append(source.substring(index + 1, end))
                }
                index = end + 1
                continue
            }
        }
        append(source[index])
        index++
    }
}
