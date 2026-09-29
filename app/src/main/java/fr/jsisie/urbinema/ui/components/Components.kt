package fr.jsisie.urbinema.ui.components

import androidx.annotation.StringRes
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.TextButton
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.pluralStringResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.data.media.MediaKind
import fr.jsisie.urbinema.ui.model.ExplorationState
import fr.jsisie.urbinema.ui.model.PreviewUrbinemaViewModel
import fr.jsisie.urbinema.ui.model.QuestUi
import fr.jsisie.urbinema.ui.model.TerritoryUi
import fr.jsisie.urbinema.ui.theme.UrbinemaTheme
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens

/** Displays an uppercase micro-label without forcing editorial copy into capitals. */
@Composable
fun SectionTitle(@StringRes title: Int, count: Int? = null, modifier: Modifier = Modifier) {
    val label = if (count == null) {
        stringResource(title)
    } else {
        stringResource(R.string.section_with_count, stringResource(title), count)
    }
    Text(
        text = label.uppercase(),
        style = MaterialTheme.typography.labelMedium,
        color = UrbinemaThemeTokens.colors.onBackgroundMuted,
        modifier = modifier.padding(top = UrbinemaThemeTokens.dimens.lg),
    )
}

/** Presents content on a flat outlined surface, avoiding decorative shadows. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun EditorialCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    onLongClick: (() -> Unit)? = null,
    highlighted: Boolean = false,
    content: @Composable ColumnScope.() -> Unit,
) {
    val interactive = when {
        onClick != null && onLongClick != null ->
            modifier.combinedClickable(onClick = onClick, onLongClick = onLongClick)
        onClick != null -> modifier.clickable(onClick = onClick)
        else -> modifier
    }
    Card(
        modifier = interactive.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = UrbinemaThemeTokens.colors.surface),
        border = androidx.compose.foundation.BorderStroke(
            if (highlighted) 2.dp else 1.dp,
            if (highlighted) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.outline,
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    ) {
        Column(
            modifier = Modifier.padding(UrbinemaThemeTokens.dimens.md),
            verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs),
            content = content,
        )
    }
}

/** Confirms a long-press “mark as watched” on a film row. */
@Composable
fun MarkWatchedDialog(title: String, onConfirm: () -> Unit, onDismiss: () -> Unit) {
    // Resolved outside the dialog window so the in-app language applies.
    val heading = stringResource(R.string.mark_watched)
    val body = stringResource(R.string.mark_watched_prompt, title)
    val confirm = stringResource(R.string.confirm)
    val cancel = stringResource(R.string.cancel)
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(heading) },
        text = { Text(body) },
        confirmButton = {
            TextButton(onClick = onConfirm) { Text(confirm) }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(cancel) }
        },
    )
}

/** Accessible progress bar with a numeric fallback to color. */
@Composable
fun LabeledProgress(progress: Int, modifier: Modifier = Modifier, emphasize: Boolean = false) {
    val description = stringResource(R.string.progress_percent, progress)
    Row(
        modifier = modifier.fillMaxWidth().semantics { contentDescription = description },
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        LinearProgressIndicator(
            progress = { progress.coerceIn(0, 100) / 100f },
            modifier = Modifier.weight(1f),
            color = UrbinemaThemeTokens.colors.accent,
            trackColor = UrbinemaThemeTokens.colors.surfacePressed,
            strokeCap = StrokeCap.Square,
        )
        Text(
            text = stringResource(R.string.percent_value, progress),
            style = MaterialTheme.typography.labelMedium,
            color = if (emphasize) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.onBackground,
        )
    }
}

@Composable
fun WatchedFilmTitle(title: String, watched: Boolean, modifier: Modifier = Modifier) {
    Text(
        title,
        modifier = modifier,
        color = if (watched) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.onBackground,
    )
}

/** Draws all five exploration states with redundant shape and stroke cues. */
@Composable
fun TerritoryRow(item: TerritoryUi, onClick: () -> Unit, modifier: Modifier = Modifier) {
    val colors = UrbinemaThemeTokens.colors
    val stateLabel = stringResource(
        when (item.state) {
            ExplorationState.Unexplored -> R.string.state_unexplored
            ExplorationState.InProgress -> R.string.state_in_progress
            ExplorationState.Explored -> R.string.state_explored
            ExplorationState.Completed -> R.string.state_completed
            ExplorationState.Mastered -> R.string.state_mastered
        }
    )
    val filmCountLabel = if (item.filmCount > 0) {
        pluralStringResource(R.plurals.film_count, item.filmCount, item.filmCount)
    } else {
        ""
    }
    val a11y = buildString {
        append(stringResource(R.string.territory_description, item.name, stateLabel))
        if (filmCountLabel.isNotEmpty()) append(", ").append(filmCountLabel)
    }
    Row(
        modifier = modifier.fillMaxWidth().heightIn(min = UrbinemaThemeTokens.dimens.touch)
            .clickable(onClick = onClick).semantics { contentDescription = a11y }
            .padding(vertical = UrbinemaThemeTokens.dimens.xs),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        Canvas(
            Modifier.size(32.dp).alpha(if (item.state == ExplorationState.Unexplored) 0.4f else 1f)
        ) {
            val strokeWidth = if (item.state >= ExplorationState.Completed) 2.dp.toPx() else 1.dp.toPx()
            val color = when (item.state) {
                ExplorationState.Unexplored -> colors.onBackgroundFaint
                ExplorationState.InProgress -> colors.cool
                ExplorationState.Explored -> colors.onBackground
                ExplorationState.Completed, ExplorationState.Mastered -> colors.accent
            }
            val effect = if (item.state == ExplorationState.Unexplored) {
                PathEffect.dashPathEffect(floatArrayOf(4.dp.toPx(), 3.dp.toPx()))
            } else null
            drawArc(
                color = color,
                startAngle = -90f,
                sweepAngle = if (item.state == ExplorationState.InProgress) item.progress * 3.6f else 360f,
                useCenter = false,
                topLeft = Offset(strokeWidth, strokeWidth),
                size = Size(size.width - strokeWidth * 2, size.height - strokeWidth * 2),
                style = Stroke(strokeWidth, pathEffect = effect),
            )
            if (item.state == ExplorationState.Mastered) drawCircle(color, radius = 3.dp.toPx())
        }
        Column(Modifier.weight(1f)) {
            Text(item.name, style = MaterialTheme.typography.titleMedium)
            Text(stateLabel, style = MaterialTheme.typography.bodyMedium, color = colors.onBackgroundMuted)
        }
        if (filmCountLabel.isNotEmpty()) {
            Text(
                filmCountLabel,
                style = MaterialTheme.typography.labelMedium,
                color = colors.onBackgroundFaint,
            )
        }
    }
}

/** Small catalogue size, used wherever a list stands for a set of films. */
@Composable
fun FilmCountLabel(count: Int, modifier: Modifier = Modifier) {
    if (count <= 0) return
    Text(
        pluralStringResource(R.plurals.film_count, count, count),
        modifier = modifier,
        style = MaterialTheme.typography.labelMedium,
        color = UrbinemaThemeTokens.colors.onBackgroundFaint,
    )
}

/** Compact weekly quest, closer to a stadium than a full editorial card. */
@Composable
fun QuestCard(quest: QuestUi, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(28.dp),
        colors = CardDefaults.cardColors(containerColor = UrbinemaThemeTokens.colors.surface),
        border = androidx.compose.foundation.BorderStroke(1.dp, UrbinemaThemeTokens.colors.outline),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    ) {
        Column(
            Modifier.padding(horizontal = UrbinemaThemeTokens.dimens.md, vertical = UrbinemaThemeTokens.dimens.sm),
            verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs),
        ) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(stringResource(quest.title), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(R.string.xp_value, quest.rewardXp), color = UrbinemaThemeTokens.colors.accent)
            }
            Text(quest.condition, color = UrbinemaThemeTokens.colors.onBackgroundMuted, style = MaterialTheme.typography.bodyMedium)
            LabeledProgress(quest.progress * 100 / quest.target.coerceAtLeast(1))
        }
    }
}

/** Circular collection summary for the home journey carousel. */
@Composable
fun CollectionMedallion(name: String, progress: Int, onClick: () -> Unit) {
    Column(
        modifier = Modifier.width(120.dp).clickable(onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        Box(
            Modifier.size(72.dp).border(2.dp, UrbinemaThemeTokens.colors.accent, CircleShape),
            contentAlignment = Alignment.Center,
        ) {
            Text(stringResource(R.string.percent_value, progress), style = MaterialTheme.typography.labelMedium)
        }
        Text(
            name,
            style = MaterialTheme.typography.bodyMedium,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
        )
    }
}

@Composable
fun UserAvatar(
    code: String?,
    modifier: Modifier = Modifier,
    contentDescription: String? = null,
) {
    EditorialImage(
        kind = MediaKind.AVATAR,
        code = code.orEmpty(),
        contentDescription = contentDescription,
        modifier = modifier
            .clip(CircleShape)
            .background(UrbinemaThemeTokens.colors.surface),
        contentScale = ContentScale.Crop,
    ) {
        Icon(
            Icons.Outlined.Person,
            contentDescription = contentDescription,
            tint = UrbinemaThemeTokens.colors.onBackgroundMuted,
            modifier = Modifier.size(32.dp),
        )
    }
}

/**
 * Horizontal carousel of packaged avatars (onboarding + Settings).
 *
 * Ten portraits would overflow a wrapping row; this snaps while scrolling
 * and keeps a fixed height so it nests inside both AlertDialog and LazyColumn.
 */
@Composable
fun AvatarPicker(
    codes: List<String>,
    selectedCode: String?,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val listState = rememberLazyListState()
    val snapBehavior = rememberSnapFlingBehavior(lazyListState = listState)
    LaunchedEffect(selectedCode, codes) {
        val index = codes.indexOf(selectedCode)
        if (index >= 0) {
            val visible = listState.layoutInfo.visibleItemsInfo.any { it.index == index }
            if (!visible) listState.animateScrollToItem(index)
        }
    }
    LazyRow(
        state = listState,
        flingBehavior = snapBehavior,
        modifier = modifier
            .fillMaxWidth()
            .height(80.dp),
        contentPadding = PaddingValues(horizontal = UrbinemaThemeTokens.dimens.sm),
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        items(codes, key = { it }) { code ->
            val selected = code == selectedCode
            UserAvatar(
                code = code,
                contentDescription = stringResource(R.string.avatar_option),
                modifier = Modifier
                    .size(72.dp)
                    .border(
                        if (selected) 2.dp else 1.dp,
                        if (selected) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.outline,
                        CircleShape,
                    )
                    .clickable { onSelect(code) },
            )
        }
    }
}

@Preview
@Composable
private fun TerritoryRowPreview() {
    UrbinemaTheme {
        TerritoryRow(PreviewUrbinemaViewModel.territories.first(), {})
    }
}
