package fr.jsisie.urbinema.ui.map

import android.graphics.Paint
import android.graphics.Typeface
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculateCentroid
import androidx.compose.foundation.gestures.calculatePan
import androidx.compose.foundation.gestures.calculateZoom
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.MyLocation
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.FloatingActionButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalViewConfiguration
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.domain.map.CinemaMapGraph
import fr.jsisie.urbinema.domain.map.CinemaMapLayout
import fr.jsisie.urbinema.domain.map.CinemaMapNode
import fr.jsisie.urbinema.domain.map.MapCamera
import fr.jsisie.urbinema.domain.map.MapLayer
import fr.jsisie.urbinema.domain.map.MapNodeKind
import fr.jsisie.urbinema.ui.components.MarkWatchedDialog
import fr.jsisie.urbinema.ui.components.WatchedFilmTitle
import fr.jsisie.urbinema.ui.model.ExplorationState
import fr.jsisie.urbinema.ui.model.MovieSummaryUi
import fr.jsisie.urbinema.ui.model.TerritoryUi
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens
import kotlin.math.hypot
import kotlinx.coroutines.launch

internal val SkyNight = Color(0xFF07060D)
internal val SkyViolet = Color(0xFF7A5CB8)
internal val SkyGold = Color(0xFFE8C68A)
internal val SkyIvory = Color(0xFFF4EFE6)
internal val SkyLink = Color(0xFF8B7AC7)
internal val SkyDirector = Color(0xFF5EC8D8)
internal val SkyCountry = Color(0xFFE07A5F)
internal val SkyGenre = Color(0xFFD489C0)
internal val SkyDecade = Color(0xFFE0A45C)
internal val SkyCollection = Color(0xFF6EA8FF)

private data class SkyPalette(
    val isDark: Boolean,
    val sky: Color,
    val glow: Color,
    val ink: Color,
    val gold: Color,
    val sheet: Color,
    val fab: Color,
    val star: Color,
)

@Composable
private fun rememberSkyPalette(): SkyPalette {
    val colors = UrbinemaThemeTokens.colors
    return if (colors.isDark) {
        SkyPalette(
            isDark = true,
            sky = SkyNight,
            glow = Color(0xFF1B1430),
            ink = SkyIvory,
            gold = SkyGold,
            sheet = Color(0xFF12101A),
            fab = Color(0xFF16141F),
            star = Color.White,
        )
    } else {
        SkyPalette(
            isDark = false,
            sky = colors.background,
            glow = colors.surface,
            ink = colors.onBackground,
            gold = colors.accent,
            sheet = colors.surfaceElevated,
            fab = colors.surfaceElevated,
            star = colors.accentMuted,
        )
    }
}

internal fun skyKindColor(kind: MapNodeKind): Color = when (kind) {
    MapNodeKind.FILM -> SkyIvory
    MapNodeKind.DIRECTOR -> SkyDirector
    MapNodeKind.COUNTRY -> SkyCountry
    MapNodeKind.GENRE -> SkyGenre
    MapNodeKind.CURRENT -> SkyViolet
    MapNodeKind.DECADE -> SkyDecade
    MapNodeKind.COLLECTION -> SkyCollection
    MapNodeKind.TERRITORY -> SkyIvory
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InteractiveMapScreen(
    graph: CinemaMapGraph,
    territories: Map<String, TerritoryUi>,
    layer: MapLayer,
    onLayerChange: (MapLayer) -> Unit,
    filmsOf: (String) -> List<MovieSummaryUi>,
    onMovie: (String) -> Unit,
    onMarkWatched: (String) -> Unit = {},
    onCenterFilm: (String) -> Unit,
    onOpenNode: (MapNodeKind, String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val palette = rememberSkyPalette()
    val scope = rememberCoroutineScope()
    val live = remember { LiveCamera() }
    var frame by remember { mutableIntStateOf(0) }
    var viewport by remember { mutableStateOf(IntSize.Zero) }
    var selectedId by remember { mutableStateOf<String?>(null) }
    val fitted = remember(graph, viewport) {
        if (viewport.width == 0) MapCamera()
        else CinemaMapLayout.fit(graph, viewport.width.toFloat(), viewport.height.toFloat())
    }
    LaunchedEffect(graph.layer, graph.focusId, viewport) {
        if (viewport.width == 0) return@LaunchedEffect
        animateCamera(live, fitted) { frame++ }
        selectedId = null
    }
    val infinite = rememberInfiniteTransition(label = "map-pulse")
    val pulse by infinite.animateFloat(
        initialValue = 0.88f,
        targetValue = 1.22f,
        animationSpec = infiniteRepeatable(
            tween(1_700, easing = FastOutSlowInEasing),
            RepeatMode.Reverse,
        ),
        label = "pulse",
    )
    val selected = selectedId?.let { id -> graph.nodes.firstOrNull { it.id == id } }
    val selectedTerritory = selectedId?.let { territories[it] }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)
    val layers = listOf(
        MapLayer.AROUND_FILM to R.string.sky_map_around,
        MapLayer.COUNTRIES to R.string.countries,
        MapLayer.DECADES to R.string.decades,
    )
    LaunchedEffect(layer) {
        if (layers.none { it.first == layer }) onLayerChange(MapLayer.AROUND_FILM)
    }
    Box(
        modifier
            .fillMaxSize()
            .background(palette.sky)
            .onSizeChanged { viewport = it },
    ) {
        val camera = remember(frame) { live.snapshot() }
        CinemaMapCanvas(
            graph = graph,
            territories = territories,
            camera = camera,
            selectedId = selectedId,
            pulse = pulse,
            palette = palette,
            onGestureCamera = { next ->
                live.set(next)
                frame++
            },
            onTapNode = { node ->
                if (graph.layer == MapLayer.AROUND_FILM &&
                    node.kind == MapNodeKind.FILM &&
                    node.id != graph.focusId
                ) {
                    onCenterFilm(node.id)
                    return@CinemaMapCanvas
                }
                selectedId = node.id
                if (viewport.width > 0) {
                    val target = CinemaMapLayout.focus(
                        node,
                        viewport.width.toFloat(),
                        viewport.height.toFloat(),
                        live.scale,
                    )
                    scope.launch { animateCamera(live, target) { frame++ } }
                }
            },
            modifier = Modifier.fillMaxSize(),
        )
        Column(
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
        ) {
            Text(
                stringResource(
                    if (layer == MapLayer.AROUND_FILM) R.string.sky_map_hint_around else R.string.sky_map_hint,
                ),
                color = palette.ink.copy(alpha = 0.55f),
                style = MaterialTheme.typography.bodyMedium,
            )
            Row(
                Modifier
                    .horizontalScroll(rememberScrollState())
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                layers.forEach { (value, label) ->
                    FilterChip(
                        selected = layer == value,
                        onClick = { onLayerChange(value) },
                        label = { Text(stringResource(label)) },
                        colors = FilterChipDefaults.filterChipColors(
                            containerColor = palette.ink.copy(alpha = 0.06f),
                            labelColor = palette.ink.copy(alpha = 0.8f),
                            selectedContainerColor = palette.gold.copy(alpha = 0.22f),
                            selectedLabelColor = palette.gold,
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            enabled = true,
                            selected = layer == value,
                            borderColor = palette.ink.copy(alpha = 0.12f),
                            selectedBorderColor = palette.gold.copy(alpha = 0.7f),
                        ),
                    )
                }
            }
        }
        FloatingActionButton(
            onClick = {
                if (viewport.width > 0) {
                    scope.launch { animateCamera(live, fitted) { frame++ } }
                }
            },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .navigationBarsPadding()
                .padding(end = 16.dp, bottom = 16.dp),
            containerColor = palette.fab,
            contentColor = palette.gold,
            elevation = FloatingActionButtonDefaults.elevation(0.dp, 0.dp),
            shape = CircleShape,
        ) {
            Icon(Icons.Outlined.MyLocation, stringResource(R.string.sky_map_recenter))
        }
        Column(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .navigationBarsPadding()
                .padding(start = 16.dp, bottom = 16.dp, end = 88.dp),
        ) {
            Text(
                stringResource(R.string.sky_map_legend),
                color = palette.ink.copy(alpha = 0.4f),
                style = MaterialTheme.typography.labelSmall,
            )
            SkyMapLegend(palette, Modifier.padding(top = 6.dp))
        }
    }
    if (selected != null && selectedTerritory != null) {
        val films = filmsOf(selected.id)
        ModalBottomSheet(
            onDismissRequest = { selectedId = null },
            sheetState = sheetState,
            containerColor = palette.sheet,
            contentColor = palette.ink,
        ) {
            NodeSheet(
                territory = selectedTerritory,
                films = films,
                kind = selected.kind,
                onMovie = onMovie,
                onMarkWatched = onMarkWatched,
                onOpenNode = { onOpenNode(selected.kind, selected.id) },
            )
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun NodeSheet(
    territory: TerritoryUi,
    films: List<MovieSummaryUi>,
    kind: MapNodeKind,
    onMovie: (String) -> Unit,
    onMarkWatched: (String) -> Unit,
    onOpenNode: () -> Unit,
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
    val stateLabel = stringResource(
        when (territory.state) {
            ExplorationState.Unexplored -> R.string.state_unexplored
            ExplorationState.InProgress -> R.string.state_in_progress
            ExplorationState.Explored -> R.string.state_explored
            ExplorationState.Completed -> R.string.state_completed
            ExplorationState.Mastered -> R.string.state_mastered
        },
    )
    val colors = UrbinemaThemeTokens.colors
    LazyColumn(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp),
        contentPadding = PaddingValues(bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Text(territory.name, style = MaterialTheme.typography.displayMedium, color = colors.accent)
            if (territory.subtitle.isNotBlank()) {
                Text(
                    territory.subtitle,
                    color = colors.onBackgroundMuted,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            if (kind != MapNodeKind.FILM) {
                Text(
                    "$stateLabel · ${territory.progress} %",
                    color = colors.onBackgroundMuted,
                    style = MaterialTheme.typography.bodyMedium,
                )
                LinearProgressIndicator(
                    progress = { territory.progress / 100f },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 12.dp)
                        .height(3.dp),
                    color = colors.accent,
                    trackColor = colors.surfacePressed,
                )
            }
            TextButton(onClick = onOpenNode, modifier = Modifier.padding(top = 4.dp)) {
                Text(
                    stringResource(
                        if (kind == MapNodeKind.FILM) R.string.sky_map_open_fiche else R.string.sky_map_open_place,
                    ),
                    color = colors.accent,
                )
            }
        }
        if (kind != MapNodeKind.FILM) {
            item {
                Text(
                    stringResource(R.string.section_with_count, stringResource(R.string.films), films.size),
                    style = MaterialTheme.typography.titleMedium,
                    color = colors.cool,
                    modifier = Modifier.padding(top = 8.dp),
                )
            }
            if (films.isEmpty()) {
                item { Text(stringResource(R.string.empty_territory), color = colors.onBackgroundMuted) }
            } else {
                items(films, key = { it.id }) { film ->
                    Column(
                        Modifier
                            .fillMaxWidth()
                            .combinedClickable(
                                onClick = { onMovie(film.id) },
                                onLongClick = if (film.watched) null else {
                                    { pending = film }
                                },
                            )
                            .padding(vertical = 6.dp),
                    ) {
                        WatchedFilmTitle(film.title, film.watched)
                        Text(
                            listOf(film.director, film.year.toString())
                                .filter { it.isNotBlank() }
                                .joinToString(" · "),
                            color = colors.onBackgroundMuted,
                            style = MaterialTheme.typography.bodyMedium,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
        }
        item { Spacer(Modifier.height(8.dp)) }
    }
}

@Composable
private fun CinemaMapCanvas(
    graph: CinemaMapGraph,
    territories: Map<String, TerritoryUi>,
    camera: MapCamera,
    selectedId: String?,
    pulse: Float,
    palette: SkyPalette,
    onGestureCamera: (MapCamera) -> Unit,
    onTapNode: (CinemaMapNode) -> Unit,
    modifier: Modifier = Modifier,
) {
    val touchSlop = LocalViewConfiguration.current.touchSlop
    val liveCamera = rememberUpdatedState(camera)
    val liveGraph = rememberUpdatedState(graph)
    val labelPaint = remember {
        Paint().apply {
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SERIF, Typeface.NORMAL)
        }
    }
    val groupPaint = remember {
        Paint().apply {
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.NORMAL)
        }
    }
    Canvas(
        modifier
            .fillMaxSize()
            .pointerInput(graph.layer) {
                awaitEachGesture {
                    val down = awaitFirstDown(requireUnconsumed = false)
                    val start = down.position
                    var dragged = false
                    var lastCamera = liveCamera.value
                    do {
                        val event = awaitPointerEvent()
                        val pressed = event.changes.filter { it.pressed }
                        if (pressed.size >= 2) {
                            dragged = true
                            val centroid = event.calculateCentroid()
                            lastCamera = CinemaMapLayout.zoomAround(
                                lastCamera,
                                centroid.x,
                                centroid.y,
                                event.calculateZoom(),
                                event.calculatePan().x,
                                event.calculatePan().y,
                            )
                            onGestureCamera(lastCamera)
                            event.changes.forEach { it.consume() }
                        } else if (pressed.size == 1) {
                            val change = pressed.first()
                            val delta = change.position - start
                            if (hypot(delta.x, delta.y) > touchSlop) {
                                dragged = true
                                val pan = event.calculatePan()
                                lastCamera = lastCamera.copy(
                                    panX = lastCamera.panX + pan.x,
                                    panY = lastCamera.panY + pan.y,
                                )
                                onGestureCamera(lastCamera)
                                change.consume()
                            }
                        }
                    } while (event.changes.any { it.pressed })
                    if (!dragged) {
                        val cam = liveCamera.value
                        val radius = CinemaMapLayout.DEFAULT_HIT_RADIUS / cam.scale.coerceAtLeast(0.35f)
                        CinemaMapLayout.hitTest(
                            liveGraph.value,
                            cam.screenToWorldX(start.x),
                            cam.screenToWorldY(start.y),
                            radius,
                        )?.let(onTapNode)
                    }
                }
            },
    ) {
        val cam = camera
        drawRect(
            Brush.radialGradient(
                colors = listOf(palette.glow, palette.sky),
                center = Offset(size.width * 0.35f, size.height * 0.28f),
                radius = size.maxDimension * 0.85f,
            ),
        )
        drawCircle(
            SkyViolet.copy(alpha = 0.07f),
            radius = 220.dp.toPx(),
            center = Offset(cam.worldToScreenX(-80f), cam.worldToScreenY(-40f)),
        )
        drawCircle(
            palette.gold.copy(alpha = 0.045f),
            radius = 180.dp.toPx(),
            center = Offset(cam.worldToScreenX(140f), cam.worldToScreenY(90f)),
        )
        val bounds = graph.bounds
        for (i in 0 until 70) {
            val hx = ((i * 73) % 1000) / 1000f
            val hy = ((i * 191) % 1000) / 1000f
            val wx = bounds.minX + hx * bounds.width
            val wy = bounds.minY + hy * bounds.height
            drawCircle(
                palette.star.copy(alpha = if (palette.isDark) 0.08f + (i % 4) * 0.04f else 0.12f),
                radius = 1.1.dp.toPx() + (i % 3) * 0.4.dp.toPx(),
                center = Offset(cam.worldToScreenX(wx), cam.worldToScreenY(wy)),
            )
        }
        val nodeById = graph.nodes.associateBy { it.id }
        graph.edges.forEach { edge ->
            val a = nodeById[edge.left] ?: return@forEach
            val b = nodeById[edge.right] ?: return@forEach
            val alpha = (0.10f + 0.04f * edge.weight.coerceAtMost(5)).coerceAtMost(0.28f)
            drawLine(
                SkyLink.copy(alpha = alpha),
                Offset(cam.worldToScreenX(a.x), cam.worldToScreenY(a.y)),
                Offset(cam.worldToScreenX(b.x), cam.worldToScreenY(b.y)),
                strokeWidth = 1.2.dp.toPx(),
                cap = StrokeCap.Round,
            )
        }
        graph.groupLabels.forEach { label ->
            groupPaint.color = SkyViolet.copy(alpha = 0.55f).toArgb()
            groupPaint.textSize = 11.sp.toPx()
            drawIntoCanvas { canvas ->
                canvas.nativeCanvas.drawText(
                    label.text.uppercase(),
                    cam.worldToScreenX(label.x),
                    cam.worldToScreenY(label.y),
                    groupPaint,
                )
            }
        }
        graph.nodes.forEach { node ->
            val territory = territories[node.id]
            val state = territory?.state ?: ExplorationState.Unexplored
            val selected = node.id == selectedId
            val isFilm = node.kind == MapNodeKind.FILM
            val color = when {
                node.ring == 0 -> palette.gold
                isFilm && state >= ExplorationState.Completed -> palette.gold
                isFilm -> palette.ink
                else -> skyKindColor(node.kind)
            }
            val base = when {
                node.ring == 0 -> 9.5.dp.toPx()
                isFilm -> 6.2.dp.toPx()
                state == ExplorationState.Unexplored -> 3.2.dp.toPx()
                state == ExplorationState.InProgress -> 4.6.dp.toPx()
                state == ExplorationState.Explored -> 5.4.dp.toPx()
                state == ExplorationState.Completed -> 6.4.dp.toPx()
                else -> 7.2.dp.toPx()
            }
            val radius = if (selected || node.ring == 0) base * pulse else base
            val center = Offset(cam.worldToScreenX(node.x), cam.worldToScreenY(node.y))
            if (state >= ExplorationState.InProgress || selected || isFilm) {
                drawCircle(color.copy(alpha = if (selected || node.ring == 0) 0.22f else 0.12f), radius * 3.1f, center)
            }
            if (state == ExplorationState.Unexplored && !isFilm) {
                drawCircle(
                    color,
                    radius,
                    center,
                    style = Stroke(
                        width = 1.2.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(5.dp.toPx(), 4.dp.toPx())),
                    ),
                )
            } else {
                drawCircle(color, radius, center)
            }
            if (state == ExplorationState.Mastered && !isFilm) {
                drawCircle(palette.sky, radius * 0.35f, center)
            }
            if (selected || node.ring == 0) {
                drawCircle(
                    palette.gold.copy(alpha = 0.9f),
                    radius + 5.dp.toPx(),
                    center,
                    style = Stroke(width = 1.4.dp.toPx()),
                )
            }
            val showLabel = selected ||
                node.ring == 0 ||
                graph.layer == MapLayer.AROUND_FILM ||
                state != ExplorationState.Unexplored ||
                graph.nodes.size <= 24 ||
                (graph.layer != MapLayer.DIRECTORS && cam.scale >= 1.15f) ||
                (graph.layer == MapLayer.DIRECTORS && cam.scale >= 1.85f)
            if (showLabel) {
                val name = territory?.name ?: node.id
                labelPaint.color = (when {
                    selected || node.ring == 0 || (isFilm && state >= ExplorationState.Completed) -> palette.gold
                    isFilm -> palette.ink
                    else -> skyKindColor(node.kind)
                })
                    .copy(alpha = if (state == ExplorationState.Unexplored && !isFilm) 0.55f else 0.92f)
                    .toArgb()
                labelPaint.textSize = if (selected || node.ring == 0) 13.sp.toPx() else 11.sp.toPx()
                drawIntoCanvas { canvas ->
                    canvas.nativeCanvas.drawText(
                        name,
                        center.x,
                        center.y + radius + 14.dp.toPx(),
                        labelPaint,
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun SkyMapLegend(palette: SkyPalette, modifier: Modifier = Modifier) {
    val items = listOf(
        Triple(palette.ink, R.string.sky_legend_film, false),
        Triple(palette.gold, R.string.sky_legend_watched, false),
        Triple(SkyDirector, R.string.directors, false),
        Triple(SkyCountry, R.string.countries, false),
        Triple(SkyGenre, R.string.genres, false),
        Triple(SkyViolet, R.string.currents, false),
        Triple(SkyDecade, R.string.decades, false),
        Triple(SkyCollection, R.string.all_collections, false),
    )
    FlowRow(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        items.forEach { (color, label, _) ->
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                Canvas(Modifier.size(8.dp)) {
                    drawCircle(color)
                }
                Text(
                    stringResource(label),
                    color = palette.ink.copy(alpha = 0.45f),
                    style = MaterialTheme.typography.labelSmall,
                )
            }
        }
    }
}

internal class LiveCamera {
    var scale: Float = 1f
    var panX: Float = 0f
    var panY: Float = 0f
    fun snapshot(): MapCamera = MapCamera(scale, panX, panY)
    fun set(camera: MapCamera) {
        scale = camera.scale
        panX = camera.panX
        panY = camera.panY
    }
}

internal suspend fun animateCamera(
    live: LiveCamera,
    target: MapCamera,
    onFrame: () -> Unit,
) {
    val start = live.snapshot()
    val progress = Animatable(0f)
    progress.animateTo(1f, spring(dampingRatio = 0.86f, stiffness = Spring.StiffnessMediumLow)) {
        val p = value
        live.set(
            MapCamera(
                scale = start.scale + (target.scale - start.scale) * p,
                panX = start.panX + (target.panX - start.panX) * p,
                panY = start.panY + (target.panY - start.panY) * p,
            ),
        )
        onFrame()
    }
}
