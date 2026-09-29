package fr.jsisie.urbinema.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.ErrorOutline
import androidx.compose.material.icons.outlined.Image
import androidx.compose.material.icons.outlined.KeyboardArrowDown
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.window.DialogProperties
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.sp
import fr.jsisie.urbinema.BuildConfig
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.ui.components.AvatarPicker
import fr.jsisie.urbinema.ui.components.CollectionMedallion
import fr.jsisie.urbinema.ui.components.EditorialCard
import fr.jsisie.urbinema.ui.components.FilmCountLabel
import fr.jsisie.urbinema.ui.components.EditorialImage
import fr.jsisie.urbinema.ui.components.LabeledProgress
import fr.jsisie.urbinema.ui.components.MarkWatchedDialog
import fr.jsisie.urbinema.ui.components.QuestCard
import fr.jsisie.urbinema.ui.components.SectionTitle
import fr.jsisie.urbinema.ui.components.TerritoryRow
import fr.jsisie.urbinema.ui.components.UserAvatar
import fr.jsisie.urbinema.ui.components.WatchedFilmTitle
import fr.jsisie.urbinema.domain.collection.CollectionUnlockRules
import fr.jsisie.urbinema.data.media.MediaKind
import fr.jsisie.urbinema.data.media.MediaPaths
import fr.jsisie.urbinema.ui.model.AppLanguage
import fr.jsisie.urbinema.ui.model.AtlasFilter
import fr.jsisie.urbinema.ui.model.FilmListSort
import fr.jsisie.urbinema.ui.model.filmIndexLetter
import fr.jsisie.urbinema.ui.model.filmSortKey
import fr.jsisie.urbinema.ui.model.sortedFilms
import fr.jsisie.urbinema.ui.model.BadgeRarity
import fr.jsisie.urbinema.ui.model.BadgeUi
import fr.jsisie.urbinema.ui.model.CollectionTrack
import fr.jsisie.urbinema.ui.model.CollectionUi
import fr.jsisie.urbinema.ui.model.DirectorUi
import fr.jsisie.urbinema.ui.model.HelpTopic
import fr.jsisie.urbinema.ui.model.HistoryUi
import fr.jsisie.urbinema.ui.model.HomeUiState
import fr.jsisie.urbinema.ui.model.LoadState
import fr.jsisie.urbinema.ui.model.MovieSummaryUi
import fr.jsisie.urbinema.ui.model.MovieUi
import fr.jsisie.urbinema.ui.model.ProfileUiState
import fr.jsisie.urbinema.ui.model.RankUi
import fr.jsisie.urbinema.ui.model.SearchHitUi
import fr.jsisie.urbinema.ui.model.SearchKind
import fr.jsisie.urbinema.ui.model.StatsCategory
import fr.jsisie.urbinema.ui.model.StatsListsUi
import fr.jsisie.urbinema.ui.model.TerritoryUi
import fr.jsisie.urbinema.ui.theme.RankDisplayStyle
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeMode
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens
import kotlinx.coroutines.launch

private val pageModifier: Modifier
    @Composable get() = Modifier.fillMaxSize().background(UrbinemaThemeTokens.colors.background)

@Composable
fun UiStatePane(state: LoadState, onRetry: () -> Unit = {}, content: @Composable () -> Unit) {
    when (state) {
        LoadState.Content -> content()
        LoadState.Loading -> Box(
            Modifier.fillMaxSize().background(
                if (UrbinemaThemeTokens.colors.isDark) UrbinemaThemeTokens.colors.background else Color.White,
            ),
            contentAlignment = Alignment.Center,
        ) {
            Image(
                painter = painterResource(R.drawable.logo_urbinema),
                contentDescription = stringResource(R.string.app_name),
                modifier = Modifier.size(220.dp),
                contentScale = ContentScale.Fit,
            )
        }
        LoadState.Empty -> MessagePane(R.string.empty_state, null)
        LoadState.Error -> MessagePane(R.string.error_state, onRetry)
    }
}

@Composable
private fun MessagePane(message: Int, onRetry: (() -> Unit)?) {
    Column(
        pageModifier.padding(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(Icons.Outlined.ErrorOutline, contentDescription = null, tint = UrbinemaThemeTokens.colors.cool)
        Text(stringResource(message), textAlign = TextAlign.Center)
        if (onRetry != null) Button(onClick = onRetry) {
            Icon(Icons.Outlined.Refresh, contentDescription = null)
            Text(stringResource(R.string.retry))
        }
    }
}

@Composable
fun HomeScreen(
    state: HomeUiState,
    onRetry: () -> Unit = {},
    onOpenProfile: () -> Unit = {},
    onCollection: (String) -> Unit,
    onSeeAllHistory: () -> Unit = {},
) {
    UiStatePane(state.loadState, onRetry) {
        Column(pageModifier) {
            Column(
                Modifier.fillMaxWidth()
                    .clickable(onClick = onOpenProfile)
                    .padding(horizontal = UrbinemaThemeTokens.dimens.screen, vertical = UrbinemaThemeTokens.dimens.sm),
            ) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(state.rank.uppercase(), style = MaterialTheme.typography.titleMedium)
                    Text(stringResource(R.string.level_value, state.level), style = MaterialTheme.typography.labelMedium)
                }
                LinearXp(state.xp, state.nextLevelXp)
            }
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(
                    horizontal = UrbinemaThemeTokens.dimens.screen,
                    vertical = UrbinemaThemeTokens.dimens.sm,
                ),
                verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
            ) {
                item { SectionTitle(R.string.weekly_quests) }
                items(state.quests) { QuestCard(it) }
                item { SectionTitle(R.string.current_collections) }
                if (state.collections.isEmpty()) {
                    item {
                        Text(
                            stringResource(R.string.empty_current_collections),
                            color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                        )
                    }
                } else {
                    item {
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md)) {
                            items(state.collections) { collection ->
                                CollectionMedallion(collection.name, collection.progress) { onCollection(collection.id) }
                            }
                        }
                    }
                }
                item { SectionTitle(R.string.history) }
                if (state.history.isEmpty()) item { Text(stringResource(R.string.journey_starts)) }
                items(state.history.take(HistoryUi.HOME_PREVIEW_LIMIT)) { event ->
                    HistoryEventRow(event)
                }
                if (state.history.size > HistoryUi.HOME_PREVIEW_LIMIT) {
                    item {
                        Button(onClick = onSeeAllHistory, modifier = Modifier.fillMaxWidth()) {
                            Text(stringResource(R.string.see_full_history))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun historyDate(label: String): String = when (label) {
    "today" -> stringResource(R.string.today)
    "yesterday" -> stringResource(R.string.yesterday)
    else -> label
}

@Composable
internal fun HistoryScreen(events: List<HistoryUi>) {
    if (events.isEmpty()) {
        Text(
            stringResource(R.string.journey_starts),
            modifier = pageModifier.padding(UrbinemaThemeTokens.dimens.screen),
        )
        return
    }
    LazyColumn(
        modifier = pageModifier,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
    ) {
        items(events) { event -> HistoryEventRow(event) }
    }
}

@Composable
private fun HistoryEventRow(event: HistoryUi) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md)) {
        Text(historyDate(event.dateLabel), color = UrbinemaThemeTokens.colors.onBackgroundMuted)
        Text(historyMessage(event))
    }
}

@Composable
private fun historyMessage(event: HistoryUi): String = when (event.type) {
    HistoryUi.MOVIE_VALIDATED -> stringResource(R.string.history_movie_body, event.subject)
    HistoryUi.BADGE_EARNED -> stringResource(R.string.history_badge_body, event.subject)
    HistoryUi.QUEST_COMPLETED -> stringResource(R.string.history_quest_body)
    HistoryUi.RANK_UP -> stringResource(R.string.history_rank_body, event.subject)
    else -> event.subject.ifBlank { event.type }
}

@Composable
fun LinearXp(xp: Int, target: Int) {
    androidx.compose.material3.LinearProgressIndicator(
        progress = { xp.toFloat() / target.coerceAtLeast(1) },
        modifier = Modifier.fillMaxWidth().padding(top = UrbinemaThemeTokens.dimens.xs),
        color = UrbinemaThemeTokens.colors.accent,
        trackColor = UrbinemaThemeTokens.colors.surfacePressed,
    )
    Text(stringResource(R.string.xp_progress, xp, target), style = MaterialTheme.typography.labelMedium)
}

@Composable
fun AtlasScreen(
    countries: List<TerritoryUi>,
    currents: List<TerritoryUi>,
    decades: List<TerritoryUi>,
    genres: List<TerritoryUi>,
    directors: List<TerritoryUi>,
    onSelect: (AtlasFilter, String) -> Unit,
) {
    var selected by rememberSaveable { mutableStateOf(AtlasFilter.Countries) }
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    val raw = when (selected) {
        AtlasFilter.Countries -> countries
        AtlasFilter.Currents -> currents
        AtlasFilter.Decades -> decades
        AtlasFilter.Genres -> genres
        AtlasFilter.Directors -> directors
    }
    val indexed = selected != AtlasFilter.Decades
    val items = remember(raw, indexed) {
        if (indexed) raw.sortedBy { filmSortKey(it.name) } else raw
    }
    val filters = listOf(
        AtlasFilter.Currents to R.string.currents,
        AtlasFilter.Countries to R.string.countries,
        AtlasFilter.Decades to R.string.decades,
        AtlasFilter.Genres to R.string.genres,
        AtlasFilter.Directors to R.string.directors,
    )
    Box(pageModifier) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(end = if (indexed) 18.dp else 0.dp),
            state = listState,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        ) {
            item { ScreenTitle(R.string.atlas) }
            item {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                    items(filters) { (filter, label) ->
                        FilterChip(
                            selected == filter,
                            {
                                if (selected != filter) {
                                    selected = filter
                                    scope.launch { listState.scrollToItem(0) }
                                }
                            },
                            { Text(stringResource(label)) },
                        )
                    }
                }
            }
            item {
                Text(
                    stringResource(R.string.atlas_intro),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.md),
                )
            }
            items(items, key = { it.id }) { TerritoryRow(it, { onSelect(selected, it.id) }) }
            item { Text(stringResource(R.string.atlas_legend), style = MaterialTheme.typography.bodyMedium) }
        }
        if (indexed) {
            AlphabetScrubber(
                titles = items.map { it.name },
                plain = true,
                onLetter = { letter ->
                    val index = items.indexOfFirst { filmIndexLetter(it.name) == letter }
                    if (index >= 0) scope.launch { listState.scrollToItem(3 + index) }
                },
                modifier = Modifier
                    .align(Alignment.CenterEnd)
                    .fillMaxHeight()
                    .padding(vertical = 72.dp, horizontal = 2.dp),
            )
        }
    }
}

@Composable
fun ProgressScreen(state: HomeUiState, ranks: List<RankUi>) {
    val current = ranks.firstOrNull { it.current }
    LazyColumn(
        modifier = pageModifier,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        item { ScreenTitle(R.string.progress) }
        item {
            EditorialCard {
                val currentCode = current?.id ?: "RANK_01"
                if (rememberRankImage(currentCode)) {
                    RankArtwork(
                        code = currentCode,
                        name = state.rank,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(140.dp)
                            .padding(bottom = UrbinemaThemeTokens.dimens.sm),
                    )
                }
                Text(state.rank, style = MaterialTheme.typography.displayLarge)
                Text(stringResource(R.string.rank_out_of_ten, state.rankNumber), color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                if (current != null) {
                    Text(
                        current.longDescription,
                        modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.md),
                        color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    )
                }
            }
        }
        item { SectionTitle(R.string.current_quests) }
        items(state.quests) { QuestCard(it) }
        item { SectionTitle(R.string.current_collections) }
        if (state.collections.isEmpty()) {
            item {
                Text(
                    stringResource(R.string.empty_current_collections),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                )
            }
        } else {
            items(state.collections) { collection ->
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        collection.name,
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.weight(1f),
                    )
                    FilmCountLabel(collection.films.size)
                }
                LabeledProgress(collection.progress)
            }
        }
    }
}

@Composable
fun ProfileScreen(
    state: ProfileUiState,
    badges: List<BadgeUi>,
    onBadges: () -> Unit,
    onRank: () -> Unit,
) {
    LazyColumn(
        modifier = pageModifier,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = UrbinemaThemeTokens.dimens.xl),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(
                    UrbinemaThemeTokens.dimens.md,
                    Alignment.CenterHorizontally,
                ),
            ) {
                UserAvatar(
                    code = state.avatarCode,
                    contentDescription = stringResource(R.string.avatar),
                    modifier = Modifier.size(72.dp),
                )
                Text(
                    state.nickname,
                    style = MaterialTheme.typography.displayLarge,
                )
            }
        }
        item {
            val hasImage = rememberRankImage(state.rankCode)
            Column(
                modifier = Modifier
                    .padding(top = UrbinemaThemeTokens.dimens.xl, bottom = UrbinemaThemeTokens.dimens.md)
                    .clickable(onClick = onRank),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Box(
                    Modifier
                        .size(184.dp)
                        .border(2.dp, UrbinemaThemeTokens.colors.accent, MaterialTheme.shapes.medium)
                        .clip(MaterialTheme.shapes.medium),
                    contentAlignment = Alignment.Center,
                ) {
                    if (hasImage) {
                        RankArtwork(code = state.rankCode, name = state.rank, modifier = Modifier.fillMaxSize())
                    } else {
                        Text(state.rank, style = RankDisplayStyle, textAlign = TextAlign.Center)
                    }
                }
                if (hasImage) {
                    Text(
                        state.rank,
                        style = RankDisplayStyle,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.sm),
                    )
                }
            }
        }
        item {
            Column(Modifier.fillMaxWidth().padding(bottom = UrbinemaThemeTokens.dimens.xl)) {
                Text(stringResource(R.string.level_value, state.level), style = MaterialTheme.typography.titleMedium)
                LinearXp(state.xpIntoLevel, state.nextLevelXp)
            }
        }
        item { SectionTitle(R.string.earned_badges) }
        item {
            val shown = badges.filter { it.showcaseSlot != null }.sortedBy { it.showcaseSlot }
            if (shown.isEmpty()) {
                Text(
                    stringResource(R.string.no_badge_yet),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.lg),
                )
            } else {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = UrbinemaThemeTokens.dimens.lg),
                    horizontalArrangement = Arrangement.spacedBy(
                        UrbinemaThemeTokens.dimens.md,
                        Alignment.CenterHorizontally,
                    ),
                    verticalAlignment = Alignment.Top,
                ) {
                    shown.forEach { badge ->
                        BadgeTile(badge)
                    }
                }
            }
        }
        item { Button(onClick = onBadges) { Text(stringResource(R.string.see_all_badges)) } }
        item {
            Column(
                Modifier.fillMaxWidth().padding(top = UrbinemaThemeTokens.dimens.xl),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(stringResource(R.string.profile_stats, state.films, state.countries))
                Text(stringResource(R.string.profile_stats_more, state.decades, state.currents), color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                Text(
                    stringResource(R.string.profile_stats_extra, state.continents, state.directors),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                )
            }
        }
    }
}

@Composable
fun RanksScreen(ranks: List<RankUi>) {
    val ordered = remember(ranks) { ranks.sortedBy { it.order } }
    val listState = rememberLazyListState()
    val currentIndex = ordered.indexOfFirst { it.current }
    LaunchedEffect(currentIndex) {
        if (currentIndex >= 0) listState.scrollToItem(currentIndex + 1)
    }
    LazyColumn(
        modifier = pageModifier,
        state = listState,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        item { ScreenTitle(R.string.all_ranks) }
        itemsIndexed(ordered) { index, rank ->
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                val color = if (rank.current) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.onBackground
                Text(
                    stringResource(R.string.rank_out_of_ten, rank.order),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    style = MaterialTheme.typography.labelMedium,
                )
                if (rememberRankImage(rank.id)) {
                    RankArtwork(
                        code = rank.id,
                        name = rank.name,
                        modifier = Modifier
                            .padding(vertical = UrbinemaThemeTokens.dimens.sm)
                            .size(120.dp),
                        grayscale = !rank.current,
                    )
                }
                Text(rank.name, style = MaterialTheme.typography.headlineLarge, color = color, textAlign = TextAlign.Center)
                if (rank.current) {
                    Text(
                        rank.longDescription,
                        modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.sm, bottom = UrbinemaThemeTokens.dimens.md),
                        color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                        textAlign = TextAlign.Center,
                    )
                } else {
                    Text(
                        rank.description,
                        modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.xs),
                        color = UrbinemaThemeTokens.colors.onBackgroundFaint,
                        textAlign = TextAlign.Center,
                    )
                }
                if (index != ordered.lastIndex) {
                    Icon(
                        Icons.Outlined.KeyboardArrowDown,
                        contentDescription = null,
                        tint = UrbinemaThemeTokens.colors.accent,
                        modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.sm).size(32.dp),
                    )
                }
            }
        }
    }
}

@Composable
fun StatsScreen(state: ProfileUiState, lists: StatsListsUi, onOpen: (StatsCategory) -> Unit) {
    val rows = listOf(
        StatsCategory.Films to stringResource(R.string.profile_stat_films, state.films),
        StatsCategory.Countries to stringResource(R.string.profile_stat_countries, state.countries),
        StatsCategory.Decades to stringResource(R.string.profile_stat_decades, state.decades),
        StatsCategory.Currents to stringResource(R.string.profile_stat_currents, state.currents),
        StatsCategory.Continents to stringResource(R.string.profile_stat_continents, state.continents),
        StatsCategory.Directors to stringResource(R.string.profile_stat_directors, state.directors),
    )
    LazyColumn(
        modifier = pageModifier,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        item { ScreenTitle(R.string.detailed_statistics) }
        items(rows) { (category, label) ->
            EditorialCard(onClick = { onOpen(category) }) {
                Text(label, style = MaterialTheme.typography.titleMedium)
            }
        }
    }
}

@Composable
fun NamedListScreen(title: Int, values: List<String>) {
    LazyColumn(
        modifier = pageModifier,
        contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
    ) {
        item { ScreenTitle(title) }
        if (values.isEmpty()) item { Text(stringResource(R.string.empty_state)) }
        items(values) { Text(it, modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.sm)) }
    }
}

@Composable
fun CollectionsScreen(collections: List<CollectionUi>, onCollection: (String) -> Unit) {
    var lockTarget by remember { mutableStateOf<CollectionUi?>(null) }
    lockTarget?.let { locked ->
        val lockTitle = stringResource(R.string.collection_locked_title)
        val lockBody = collectionLockMessage(locked)
        val confirmLabel = stringResource(R.string.confirm)
        AlertDialog(
            onDismissRequest = { lockTarget = null },
            title = { Text(lockTitle) },
            text = { Text(lockBody) },
            confirmButton = {
                TextButton(onClick = { lockTarget = null }) {
                    Text(confirmLabel)
                }
            },
        )
    }
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item { ScreenTitle(R.string.collections_tab) }
        item {
            Text(
                stringResource(R.string.collections_intro),
                color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                modifier = Modifier.padding(bottom = UrbinemaThemeTokens.dimens.md),
            )
        }
        CollectionTrack.entries.forEach { track ->
            val section = collections.filter { it.track == track }
            if (section.isEmpty()) return@forEach
            item(key = "track-${track.name}") {
                CollectionTrackHeader(stringResource(track.titleRes))
            }
            items(section, key = { it.id }) { collection ->
                EditorialCard(
                    Modifier
                        .padding(vertical = UrbinemaThemeTokens.dimens.xs)
                        .alpha(
                            when {
                                collection.locked -> 0.42f
                                collection.followed || collection.completed -> 1f
                                else -> 0.72f
                            },
                        ),
                    {
                        if (collection.locked) lockTarget = collection
                        else onCollection(collection.id)
                    },
                    highlighted = (collection.followed || collection.completed) && !collection.locked,
                ) {
                    Row(
                        Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(
                                collection.name,
                                style = MaterialTheme.typography.titleMedium,
                                color = if (collection.completed) {
                                    UrbinemaThemeTokens.colors.accent
                                } else {
                                    UrbinemaThemeTokens.colors.onBackground
                                },
                            )
                            Text(collection.shortDescription, color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                        }
                        if (collection.locked) {
                            Icon(
                                Icons.Outlined.Lock,
                                contentDescription = stringResource(R.string.collection_locked_title),
                                tint = UrbinemaThemeTokens.colors.onBackgroundMuted,
                            )
                        } else if (collection.completed) {
                            Icon(
                                Icons.Outlined.CheckCircle,
                                contentDescription = stringResource(R.string.collection_completed),
                                tint = UrbinemaThemeTokens.colors.accent,
                            )
                        }
                    }
                    LabeledProgress(collection.progress, emphasize = collection.completed || collection.followed)
                }
            }
        }
    }
}

@Composable
internal fun collectionLockMessage(collection: CollectionUi): String {
    val previous = collection.lockPreviousTrack
    return if (previous == null) {
        stringResource(R.string.collection_locked_body)
    } else {
        stringResource(
            R.string.collection_locked_track_body,
            stringResource(collection.track.titleRes),
            collection.lockRequiredCollections,
            stringResource(previous.titleRes),
            CollectionUnlockRules.MIN_FILMS_PER_COLLECTION,
        )
    }
}

@Composable
private fun CollectionTrackHeader(title: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = UrbinemaThemeTokens.dimens.lg, bottom = UrbinemaThemeTokens.dimens.sm),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
    ) {
        HorizontalDivider(Modifier.weight(1f), color = UrbinemaThemeTokens.colors.onBackgroundFaint)
        Text(
            title.uppercase(),
            style = MaterialTheme.typography.labelMedium,
            color = UrbinemaThemeTokens.colors.onBackgroundMuted,
            textAlign = TextAlign.Center,
        )
        HorizontalDivider(Modifier.weight(1f), color = UrbinemaThemeTokens.colors.onBackgroundFaint)
    }
}

@Composable
fun CollectionScreen(
    collection: CollectionUi,
    onMovie: (String) -> Unit,
    onFollow: () -> Unit,
    onUnfollow: () -> Unit,
    onMarkWatched: (String) -> Unit = {},
) {
    var pending by remember { mutableStateOf<MovieSummaryUi?>(null) }
    pending?.let { film ->
        MarkWatchedDialog(
            title = film.title,
            onConfirm = {
                onMarkWatched(film.id)
                pending = null
            },
            onDismiss = { pending = null },
        )
    }
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item {
            Text(
                collection.name,
                style = MaterialTheme.typography.displayLarge,
                color = if (collection.completed) UrbinemaThemeTokens.colors.accent else UrbinemaThemeTokens.colors.onBackground,
                modifier = Modifier.padding(bottom = UrbinemaThemeTokens.dimens.md).semantics { heading() },
            )
        }
        if (collection.locked) {
            item {
                Text(
                    collectionLockMessage(collection),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.padding(bottom = UrbinemaThemeTokens.dimens.md),
                )
            }
        } else {
            item {
                if (collection.completed) {
                    Button(
                        onClick = {},
                        enabled = false,
                        modifier = Modifier.fillMaxWidth().padding(bottom = UrbinemaThemeTokens.dimens.md),
                        colors = ButtonDefaults.buttonColors(
                            disabledContainerColor = UrbinemaThemeTokens.colors.surfacePressed,
                            disabledContentColor = UrbinemaThemeTokens.colors.onBackgroundMuted,
                        ),
                    ) { Text(stringResource(R.string.collection_completed)) }
                } else if (collection.followed) {
                    OutlinedButton(
                        onClick = onUnfollow,
                        modifier = Modifier.fillMaxWidth().padding(bottom = UrbinemaThemeTokens.dimens.md),
                    ) { Text(stringResource(R.string.unfollow_collection)) }
                } else {
                    Button(
                        onClick = onFollow,
                        modifier = Modifier.fillMaxWidth().padding(bottom = UrbinemaThemeTokens.dimens.md),
                        colors = ButtonDefaults.buttonColors(containerColor = UrbinemaThemeTokens.colors.accent),
                    ) { Text(stringResource(R.string.follow_collection)) }
                }
            }
        }
        item { Text(collection.shortDescription, color = UrbinemaThemeTokens.colors.onBackgroundMuted) }
        item {
            LabeledProgress(
                collection.progress,
                Modifier.padding(vertical = UrbinemaThemeTokens.dimens.lg),
                emphasize = collection.completed || collection.followed,
            )
        }
        item { Text(collection.longDescription.ifBlank { collection.shortDescription }, style = MaterialTheme.typography.bodyLarge) }
        item { SectionTitle(R.string.films, collection.films.size) }
        items(collection.films) { film ->
            EditorialCard(
                Modifier.padding(vertical = UrbinemaThemeTokens.dimens.xs).alpha(if (collection.locked) 0.42f else 1f),
                { if (!collection.locked) onMovie(film.id) },
                if (collection.locked || film.watched) null else {
                    { pending = film }
                },
            ) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column(Modifier.weight(1f)) {
                        WatchedFilmTitle(film.title, film.watched)
                        Text(
                            stringResource(R.string.search_result_year, film.year),
                            color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                        )
                    }
                    if (film.director.isNotBlank()) {
                        Text(film.director, color = UrbinemaThemeTokens.colors.onBackgroundMuted, textAlign = TextAlign.End)
                    }
                }
            }
        }
    }
}

@Composable
fun TerritoryScreen(
    title: String,
    collections: List<CollectionUi>,
    films: List<MovieSummaryUi>,
    onCollection: (String) -> Unit,
    onMovie: (String) -> Unit,
    onMarkWatched: (String) -> Unit = {},
) {
    AtlasFilmDirectory(
        title = title,
        collections = collections,
        films = films,
        onCollection = onCollection,
        onMovie = onMovie,
        onMarkWatched = onMarkWatched,
        alwaysShowFilmSection = false,
    )
}

@Composable
fun DirectorScreen(
    director: DirectorUi,
    onMovie: (String) -> Unit,
    onCollection: (String) -> Unit,
    onMarkWatched: (String) -> Unit = {},
) {
    AtlasFilmDirectory(
        title = director.name,
        collections = director.collections,
        films = director.films,
        onCollection = onCollection,
        onMovie = onMovie,
        onMarkWatched = onMarkWatched,
        alwaysShowFilmSection = true,
    )
}

@Composable
private fun AtlasFilmDirectory(
    title: String,
    collections: List<CollectionUi>,
    films: List<MovieSummaryUi>,
    onCollection: (String) -> Unit,
    onMovie: (String) -> Unit,
    onMarkWatched: (String) -> Unit,
    alwaysShowFilmSection: Boolean,
) {
    var pending by remember { mutableStateOf<MovieSummaryUi?>(null) }
    pending?.let { film ->
        MarkWatchedDialog(
            title = film.title,
            onConfirm = {
                onMarkWatched(film.id)
                pending = null
            },
            onDismiss = { pending = null },
        )
    }
    var sortName by rememberSaveable { mutableStateOf(FilmListSort.TitleAsc.name) }
    val sort = FilmListSort.entries.firstOrNull { it.name == sortName } ?: FilmListSort.TitleAsc
    val sorted = remember(films, sort) { films.sortedFilms(sort) }
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    val titleSort = sort == FilmListSort.TitleAsc || sort == FilmListSort.TitleDesc
    val showIndex = titleSort && sorted.size >= 8
    var headerCount = 1
    if (collections.isNotEmpty()) headerCount += 1 + collections.size
    if (sorted.isNotEmpty() || alwaysShowFilmSection) headerCount += 2
    Box(pageModifier) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(end = if (showIndex) 18.dp else 0.dp),
            state = listState,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen),
        ) {
            item { ScreenTitle(title) }
            if (collections.isNotEmpty()) {
                item { SectionTitle(R.string.all_collections) }
                items(collections, key = { it.id }) { collection ->
                    EditorialCard(Modifier.padding(vertical = UrbinemaThemeTokens.dimens.xs), { onCollection(collection.id) }) {
                        Text(collection.name, style = MaterialTheme.typography.titleMedium)
                        Text(collection.shortDescription, color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                        FilmCountLabel(collection.films.size)
                    }
                }
            }
            if (sorted.isNotEmpty() || alwaysShowFilmSection) {
                item { SectionTitle(R.string.films, sorted.size) }
                item { FilmSortRow(sort) { sortName = it.name } }
                items(sorted, key = { it.id }) { film ->
                    EditorialCard(
                        Modifier.padding(vertical = UrbinemaThemeTokens.dimens.xs),
                        { onMovie(film.id) },
                        if (film.watched) null else {
                            { pending = film }
                        },
                    ) {
                        WatchedFilmTitle(film.title, film.watched)
                        val subtitle = if (film.director.isBlank()) film.year.toString()
                        else "${film.director} · ${film.year}"
                        Text(subtitle, color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                    }
                }
            }
            if (collections.isEmpty() && films.isEmpty() && !alwaysShowFilmSection) {
                item { Text(stringResource(R.string.empty_territory)) }
            }
        }
        if (showIndex) {
            AlphabetScrubber(
                titles = sorted.map { it.title },
                onLetter = { letter ->
                    // Same article-stripped letter as TitleAsc/Desc order (not raw "Les"/"L'").
                    val index = sorted.indexOfFirst { filmIndexLetter(it.title) == letter }
                    if (index >= 0) scope.launch { listState.scrollToItem(headerCount + index) }
                },
                modifier = Modifier
                    .align(Alignment.CenterEnd)
                    .fillMaxHeight()
                    .padding(vertical = 72.dp, horizontal = 2.dp),
            )
        }
    }
}

@Composable
private fun FilmSortRow(current: FilmListSort, onChange: (FilmListSort) -> Unit) {
    val options = listOf(
        FilmListSort.TitleAsc to R.string.sort_title_az,
        FilmListSort.TitleDesc to R.string.sort_title_za,
        FilmListSort.YearAsc to R.string.sort_year_asc,
        FilmListSort.YearDesc to R.string.sort_year_desc,
    )
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs),
        modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.xs, bottom = UrbinemaThemeTokens.dimens.sm),
    ) {
        items(options, key = { it.first.name }) { (value, label) ->
            FilterChip(current == value, { onChange(value) }, { Text(stringResource(label)) })
        }
    }
}

@Composable
private fun AlphabetScrubber(
    titles: List<String>,
    onLetter: (Char) -> Unit,
    modifier: Modifier = Modifier,
    plain: Boolean = false,
) {
    val letters = listOf('#') + ('A'..'Z').toList()
    val present = titles.mapTo(hashSetOf(), ::filmIndexLetter)
    val description = stringResource(R.string.alphabet_index_cd)
    fun letterAt(y: Float, height: Int): Char {
        if (height <= 0) return 'A'
        val index = ((y / height) * letters.size).toInt().coerceIn(0, letters.lastIndex)
        return letters[index]
    }
    Column(
        modifier = modifier
            .width(20.dp)
            .semantics { contentDescription = description }
            .pointerInput(titles) {
                detectTapGestures { offset -> onLetter(letterAt(offset.y, size.height)) }
            }
            .pointerInput(titles) {
                detectVerticalDragGestures { change, _ ->
                    onLetter(letterAt(change.position.y, size.height))
                }
            },
        verticalArrangement = Arrangement.SpaceEvenly,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        letters.forEach { letter ->
            Text(
                letter.toString(),
                style = MaterialTheme.typography.labelSmall,
                fontSize = 10.sp,
                color = when {
                    plain -> UrbinemaThemeTokens.colors.onBackground
                    letter in present -> UrbinemaThemeTokens.colors.accent
                    else -> UrbinemaThemeTokens.colors.onBackgroundMuted
                },
                modifier = Modifier.alpha(if (plain || letter in present) 1f else 0.35f),
            )
        }
    }
}

@Composable
fun HelpScreen(topic: HelpTopic = HelpTopic.All) {
    val showAll = topic == HelpTopic.All
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item { ScreenTitle(R.string.help) }
        if (showAll || topic == HelpTopic.Collections) {
            item { SectionTitle(R.string.help_collections_title) }
            item { Text(stringResource(R.string.help_collections_body), style = MaterialTheme.typography.bodyLarge) }
        }
        if (showAll || topic == HelpTopic.Atlas) {
            item { SectionTitle(R.string.help_map_title) }
            item { Text(stringResource(R.string.help_map_body), style = MaterialTheme.typography.bodyLarge) }
        }
        if (showAll || topic == HelpTopic.InteractiveMap) {
            item { SectionTitle(R.string.help_sky_map_title) }
            item { Text(stringResource(R.string.help_sky_map_body), style = MaterialTheme.typography.bodyLarge) }
        }
        if (showAll) {
            item { SectionTitle(R.string.help_currents_title) }
            item { Text(stringResource(R.string.help_currents_body), style = MaterialTheme.typography.bodyLarge) }
        }
        if (showAll || topic == HelpTopic.Progress) {
            item { SectionTitle(if (showAll) R.string.help_rank_title else R.string.help_progress_title) }
            item {
                Text(
                    stringResource(if (showAll) R.string.rank_explanation_body else R.string.help_progress_body),
                    style = MaterialTheme.typography.bodyLarge,
                )
            }
        }
        if (showAll) {
            item { SectionTitle(R.string.help_badges_title) }
            item { Text(stringResource(R.string.help_badges_body), style = MaterialTheme.typography.bodyLarge) }
            item { SectionTitle(R.string.help_xp_title) }
            item { Text(stringResource(R.string.help_xp_body), style = MaterialTheme.typography.bodyLarge) }
        }
        item { SectionTitle(R.string.help_states_title) }
        item { Text(stringResource(R.string.help_states_body), style = MaterialTheme.typography.bodyLarge) }
    }
}

@Composable
fun BadgesScreen(badges: List<BadgeUi>, onSaveShowcase: (List<String>) -> Unit) {
    var earnedOnly by remember { mutableStateOf(false) }
    var selecting by remember { mutableStateOf(false) }
    val visible = badges.filter { !earnedOnly || it.earned }
    val earned = badges.filter { it.earned }
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    stringResource(R.string.all_badges),
                    style = MaterialTheme.typography.displayLarge,
                    modifier = Modifier.weight(1f).padding(bottom = UrbinemaThemeTokens.dimens.md).semantics { heading() },
                )
                if (earned.isNotEmpty()) {
                    IconButton(onClick = { selecting = true }) {
                        Icon(
                            Icons.Outlined.Settings,
                            contentDescription = stringResource(R.string.showcase_badges_cd),
                        )
                    }
                }
            }
        }
        item { FilterChip(earnedOnly, { earnedOnly = !earnedOnly }, { Text(stringResource(R.string.earned_only)) }) }
        BadgeRarity.entries.forEach { rarity ->
            val section = visible
                .filter { it.rarity == rarity }
                .sortedWith(compareBy({ it.difficulty }, { it.code }))
            if (section.isEmpty()) return@forEach
            item(key = "rarity-${rarity.name}") {
                CollectionTrackHeader(stringResource(rarity.titleRes))
            }
            items(section, key = { "${rarity.name}-${it.code}" }) { badge ->
                EditorialCard(Modifier.padding(vertical = UrbinemaThemeTokens.dimens.sm)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
                    ) {
                        BadgeArtwork(badge, Modifier.size(64.dp))
                        Column(Modifier.weight(1f)) {
                            Text(badge.name, style = MaterialTheme.typography.titleMedium)
                            Text(badge.condition, color = UrbinemaThemeTokens.colors.onBackgroundMuted)
                        }
                        if (badge.earned) {
                            Icon(
                                Icons.Outlined.Check,
                                contentDescription = stringResource(R.string.earned),
                                tint = UrbinemaThemeTokens.colors.accent,
                            )
                        }
                    }
                }
            }
        }
    }
    if (selecting) {
        ShowcaseBadgesDialog(
            earned = earned.sortedWith(compareBy({ it.difficulty }, { it.code })),
            initial = earned.filter { it.showcaseSlot != null }.sortedBy { it.showcaseSlot }.map { it.code },
            onDismiss = { selecting = false },
            onSave = { codes ->
                onSaveShowcase(codes)
                selecting = false
            },
        )
    }
}

@Composable
private fun ShowcaseBadgesDialog(
    earned: List<BadgeUi>,
    initial: List<String>,
    onDismiss: () -> Unit,
    onSave: (List<String>) -> Unit,
) {
    var draft by remember { mutableStateOf(initial) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.showcase_badges_title)) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm)) {
                Text(stringResource(R.string.showcase_badges_body))
                LazyColumn(Modifier.heightIn(max = 360.dp)) {
                    items(earned, key = { it.code }) { badge ->
                        val selected = badge.code in draft
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    draft = when {
                                        selected -> draft - badge.code
                                        draft.size < 3 -> draft + badge.code
                                        else -> draft
                                    }
                                }
                                .padding(vertical = UrbinemaThemeTokens.dimens.xs),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
                        ) {
                            BadgeArtwork(badge, Modifier.size(40.dp))
                            Text(badge.name, modifier = Modifier.weight(1f))
                            if (selected) {
                                Icon(
                                    Icons.Outlined.Check,
                                    contentDescription = stringResource(R.string.earned),
                                    tint = UrbinemaThemeTokens.colors.accent,
                                )
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { onSave(draft) }) { Text(stringResource(R.string.confirm)) }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(stringResource(R.string.cancel)) }
        },
    )
}

@Composable
private fun BadgeTile(badge: BadgeUi) {
    Column(
        modifier = Modifier.width(88.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs),
    ) {
        BadgeArtwork(badge, Modifier.size(72.dp))
        Text(
            badge.name,
            style = MaterialTheme.typography.labelSmall,
            textAlign = TextAlign.Center,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun BadgeArtwork(badge: BadgeUi, modifier: Modifier = Modifier) {
    EditorialImage(
        kind = MediaKind.BADGE,
        code = badge.code,
        contentDescription = badge.name,
        modifier = modifier
            .clip(MaterialTheme.shapes.medium)
            .background(UrbinemaThemeTokens.colors.surface),
        contentScale = ContentScale.Fit,
        grayscale = !badge.earned,
    ) {
        Icon(
            Icons.Outlined.Image,
            contentDescription = null,
            tint = if (badge.earned) {
                UrbinemaThemeTokens.colors.accent
            } else {
                UrbinemaThemeTokens.colors.onBackgroundFaint
            },
            modifier = Modifier.size(28.dp),
        )
    }
}

@Composable
private fun rememberRankImage(code: String): Boolean {
    val context = LocalContext.current
    return remember(code) {
        MediaPaths.resolveExisting(context.assets, MediaKind.RANKING, code) != null
    }
}

@Composable
private fun RankArtwork(
    code: String,
    name: String,
    modifier: Modifier = Modifier,
    grayscale: Boolean = false,
) {
    EditorialImage(
        kind = MediaKind.RANKING,
        code = code,
        contentDescription = name,
        modifier = modifier.clip(MaterialTheme.shapes.medium),
        contentScale = ContentScale.Fit,
        grayscale = grayscale,
    ) { }
}

@Composable
fun SearchScreen(
    search: (String) -> List<SearchHitUi>,
    onMarkWatched: (String) -> Unit = {},
    onHit: (SearchHitUi) -> Unit,
) {
    var query by remember { mutableStateOf("") }
    var pending by remember { mutableStateOf<SearchHitUi?>(null) }
    pending?.let { hit ->
        MarkWatchedDialog(
            title = hit.title,
            onConfirm = {
                onMarkWatched(hit.id)
                pending = null
            },
            onDismiss = { pending = null },
        )
    }
    val results = search(query)
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item { ScreenTitle(R.string.search) }
        item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text(stringResource(R.string.search_hint)) },
                leadingIcon = { Icon(Icons.Outlined.Search, contentDescription = null) },
                singleLine = true,
            )
        }
        if (query.isBlank()) {
            item { Text(stringResource(R.string.search_invitation), modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.lg)) }
        } else if (results.isEmpty()) {
            item { Text(stringResource(R.string.search_no_results), modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.lg)) }
        } else {
            items(results) { hit ->
                EditorialCard(
                    Modifier.padding(vertical = UrbinemaThemeTokens.dimens.xs),
                    { onHit(hit) },
                    if (hit.kind != SearchKind.Movie) null else {
                        { pending = hit }
                    },
                ) {
                    Text(hit.title, style = MaterialTheme.typography.titleMedium)
                    Text(
                        hit.subtitle.ifBlank { stringResource(searchKindLabel(hit.kind)) },
                        color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    )
                }
            }
        }
    }
}

@Composable
private fun searchKindLabel(kind: SearchKind): Int = when (kind) {
    SearchKind.Movie -> R.string.films
    SearchKind.Country -> R.string.countries
    SearchKind.Current -> R.string.currents
    SearchKind.Collection -> R.string.all_collections
    SearchKind.Director -> R.string.directors
    SearchKind.Genre -> R.string.genres
}

@Composable
fun MovieScreen(
    movie: MovieUi,
    onWatched: () -> Unit,
    onCountry: (String) -> Unit,
    onDirector: (String) -> Unit,
    onGenre: (String) -> Unit,
    onShowOnMap: () -> Unit = {},
) {
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item {
            EditorialImage(
                kind = MediaKind.POSTER,
                code = movie.id,
                contentDescription = movie.localizedTitle ?: movie.originalTitle,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = UrbinemaThemeTokens.dimens.lg)
                    .aspectRatio(2f / 3f)
                    .background(UrbinemaThemeTokens.colors.surface),
            ) {
                Icon(Icons.Outlined.Image, stringResource(R.string.poster_placeholder), Modifier.size(48.dp))
            }
        }
        item { Text(movie.originalTitle, style = MaterialTheme.typography.displayLarge) }
        movie.localizedTitle?.let { localizedTitle ->
            item { Text(localizedTitle, style = MaterialTheme.typography.titleLarge, color = UrbinemaThemeTokens.colors.onBackgroundMuted) }
        }
        item {
            Text(
                movie.credits,
                modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.sm).clickable {
                    movie.directorIds.firstOrNull()?.let(onDirector)
                },
            )
        }
        item { Text(movie.metadata, color = UrbinemaThemeTokens.colors.onBackgroundMuted) }
        item {
            Button(
                onClick = onWatched,
                enabled = !movie.watched,
                modifier = Modifier.fillMaxWidth().padding(vertical = UrbinemaThemeTokens.dimens.lg),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (movie.watched) UrbinemaThemeTokens.colors.surfacePressed else UrbinemaThemeTokens.colors.accent,
                    disabledContainerColor = UrbinemaThemeTokens.colors.surfacePressed,
                    disabledContentColor = UrbinemaThemeTokens.colors.onBackgroundFaint,
                ),
            ) {
                Icon(Icons.Outlined.Check, contentDescription = null)
                Text(stringResource(if (movie.watched) R.string.watched else R.string.mark_watched))
            }
        }
        item {
            TextButton(onClick = onShowOnMap, modifier = Modifier.fillMaxWidth()) {
                Text(stringResource(R.string.sky_map_open_fiche_from_movie))
            }
        }
        item { SectionTitle(R.string.synopsis) }
        item { Text(movie.synopsis, style = MaterialTheme.typography.bodyLarge) }
        if (movie.genres.isNotEmpty()) {
            item { SectionTitle(R.string.genres) }
            item {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                    items(movie.genres) { genre ->
                        FilterChip(false, { onGenre(genre.id) }, { Text(genre.name) })
                    }
                }
            }
        }
        item { SectionTitle(R.string.territories) }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                items(movie.countries) { country ->
                    FilterChip(false, { onCountry(country.id) }, { Text(country.name) })
                }
            }
        }
    }
}

@Composable
fun SettingsScreen(
    themeMode: UrbinemaThemeMode,
    onThemeModeChange: (UrbinemaThemeMode) -> Unit,
    language: AppLanguage,
    onLanguageChange: (AppLanguage) -> Unit,
    filmGrain: Boolean,
    onFilmGrainChange: (Boolean) -> Unit,
    username: String,
    onUsernameChange: (String) -> Unit,
    ageYears: Int?,
    onAgeChange: (Int) -> Unit,
    avatarCode: String?,
    availableAvatars: List<String>,
    onAvatarChange: (String) -> Unit,
    onHelp: () -> Unit = {},
    onReplayGuide: () -> Unit = {},
    onSources: () -> Unit = {},
    onResetProgress: () -> Unit = {},
) {
    var editedUsername by remember(username) { mutableStateOf(username) }
    var editedAge by remember(ageYears) { mutableStateOf(ageYears?.toString().orEmpty()) }
    var confirmReset by remember { mutableStateOf(false) }
    if (confirmReset) {
        AlertDialog(
            onDismissRequest = { confirmReset = false },
            title = { Text(stringResource(R.string.reset_data)) },
            text = { Text(stringResource(R.string.reset_data_body)) },
            confirmButton = {
                TextButton(onClick = { confirmReset = false; onResetProgress() }) { Text(stringResource(R.string.confirm)) }
            },
            dismissButton = {
                TextButton(onClick = { confirmReset = false }) { Text(stringResource(R.string.cancel)) }
            },
        )
    }
    LazyColumn(pageModifier, contentPadding = androidx.compose.foundation.layout.PaddingValues(UrbinemaThemeTokens.dimens.screen)) {
        item { ScreenTitle(R.string.settings) }
        item { SectionTitle(R.string.avatar) }
        item {
            AvatarPicker(
                codes = availableAvatars,
                selectedCode = avatarCode,
                onSelect = onAvatarChange,
                modifier = Modifier.padding(vertical = UrbinemaThemeTokens.dimens.sm),
            )
        }
        item { SectionTitle(R.string.username) }
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
            ) {
                OutlinedTextField(
                    value = editedUsername,
                    onValueChange = { editedUsername = it },
                    label = { Text(stringResource(R.string.username)) },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                Button(
                    onClick = { onUsernameChange(editedUsername) },
                    enabled = editedUsername.isNotBlank() && editedUsername.trim() != username,
                ) { Text(stringResource(R.string.save)) }
            }
        }
        item { SectionTitle(R.string.age) }
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.sm),
            ) {
                OutlinedTextField(
                    value = editedAge,
                    onValueChange = { value -> editedAge = value.filter(Char::isDigit).take(3) },
                    label = { Text(stringResource(R.string.age)) },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f),
                )
                val parsedAge = editedAge.toIntOrNull()
                Button(
                    onClick = { if (parsedAge != null) onAgeChange(parsedAge) },
                    enabled = parsedAge != null && parsedAge in 8..120 && parsedAge != ageYears,
                ) { Text(stringResource(R.string.save)) }
            }
        }
        item { SectionTitle(R.string.theme) }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                items(
                    listOf(
                        UrbinemaThemeMode.Dark to R.string.dark_theme,
                        UrbinemaThemeMode.Light to R.string.light_theme,
                        UrbinemaThemeMode.System to R.string.system_theme,
                    ),
                ) { (mode, label) ->
                    FilterChip(themeMode == mode, { onThemeModeChange(mode) }, { Text(stringResource(label)) })
                }
            }
        }
        item { SettingsSwitch(R.string.film_grain, filmGrain, onFilmGrainChange) }
        item {
            Text(
                stringResource(R.string.film_grain_help),
                color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        item { SectionTitle(R.string.language) }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                items(
                    listOf(
                        AppLanguage.System to R.string.language_system,
                        AppLanguage.French to R.string.language_french,
                        AppLanguage.English to R.string.language_english,
                    ),
                ) { (value, label) ->
                    FilterChip(language == value, { onLanguageChange(value) }, { Text(stringResource(label)) })
                }
            }
        }
        item { SectionTitle(R.string.help) }
        item {
            Button(
                onClick = onHelp,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = UrbinemaThemeTokens.colors.accent),
            ) { Text(stringResource(R.string.help_open)) }
        }
        item {
            OutlinedButton(
                onClick = onReplayGuide,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = UrbinemaThemeTokens.dimens.sm),
            ) { Text(stringResource(R.string.replay_guide)) }
        }
        item { SectionTitle(R.string.data) }
        item {
            Button(
                onClick = { confirmReset = true },
                colors = ButtonDefaults.buttonColors(containerColor = UrbinemaThemeTokens.colors.danger),
            ) { Text(stringResource(R.string.reset_data)) }
        }
        item { SectionTitle(R.string.about) }
        item {
            val uriHandler = LocalUriHandler.current
            Column(verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.xs)) {
                Text(stringResource(R.string.about_app_name))
                Text(stringResource(R.string.about_version, BuildConfig.VERSION_NAME))
                Text(stringResource(R.string.about_author))
                Text(
                    stringResource(R.string.about_github),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.clickable { uriHandler.openUri("https://github.com/jsisie") },
                )
                Text(stringResource(R.string.about_catalog))
                Text(stringResource(R.string.about_privacy))
                Text(
                    stringResource(R.string.about_credits),
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = UrbinemaThemeTokens.dimens.sm),
                )
                Text(
                    stringResource(R.string.about_tmdb),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.clickable { uriHandler.openUri("https://www.themoviedb.org") },
                )
                Text(
                    stringResource(R.string.about_flaticon),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.clickable { uriHandler.openUri("https://www.flaticon.com/free-icons/library") },
                )
                Text(
                    stringResource(R.string.about_avatars),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    modifier = Modifier.clickable { uriHandler.openUri("https://avatarmaker.com") },
                )
                Text(
                    stringResource(R.string.see_all_sources),
                    color = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier
                        .padding(top = UrbinemaThemeTokens.dimens.sm)
                        .clickable(onClick = onSources),
                )
            }
        }
    }
}

@Composable
fun OnboardingDialog(
    avatars: List<String>,
    onConfirm: (String, Int, String) -> Unit,
) {
    var username by rememberSaveable { mutableStateOf("") }
    var age by rememberSaveable { mutableStateOf("") }
    var avatarCode by rememberSaveable { mutableStateOf("") }
    val parsedAge = age.toIntOrNull()
    val canConfirm = username.isNotBlank() &&
        parsedAge != null &&
        parsedAge in 8..120 &&
        avatarCode.isNotBlank()
    AlertDialog(
        onDismissRequest = {},
        properties = DialogProperties(dismissOnBackPress = false, dismissOnClickOutside = false),
        title = { Text(stringResource(R.string.onboarding_title)) },
        text = {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(UrbinemaThemeTokens.dimens.md),
            ) {
                Text(stringResource(R.string.onboarding_body))
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it.take(24) },
                    label = { Text(stringResource(R.string.username)) },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedTextField(
                    value = age,
                    onValueChange = { age = it.filter(Char::isDigit).take(3) },
                    label = { Text(stringResource(R.string.age)) },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(stringResource(R.string.avatar), style = MaterialTheme.typography.titleMedium)
                AvatarPicker(
                    codes = avatars,
                    selectedCode = avatarCode.ifBlank { null },
                    onSelect = { avatarCode = it },
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    if (parsedAge != null && avatarCode.isNotBlank()) {
                        onConfirm(username.trim(), parsedAge, avatarCode)
                    }
                },
                enabled = canConfirm,
            ) { Text(stringResource(R.string.onboarding_continue)) }
        },
    )
}

@Composable
private fun SettingsSwitch(label: Int, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        Modifier.fillMaxWidth().height(64.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(stringResource(label))
        Switch(checked, onCheckedChange)
    }
}

@Composable
internal fun ScreenTitle(title: Int) {
    Text(
        stringResource(title),
        style = MaterialTheme.typography.displayLarge,
        modifier = Modifier.padding(bottom = UrbinemaThemeTokens.dimens.md).semantics { heading() },
    )
}

@Composable
private fun ScreenTitle(title: String) {
    Text(
        title,
        style = MaterialTheme.typography.displayLarge,
        modifier = Modifier.padding(bottom = UrbinemaThemeTokens.dimens.md).semantics { heading() },
    )
}
