package fr.jsisie.urbinema.domain.map

import kotlin.math.PI
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.hypot
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

/** One Atlas dimension drawn at a time on the interactive map. */
enum class MapLayer {
    AROUND_FILM,
    CURRENTS,
    COUNTRIES,
    DECADES,
    GENRES,
    DIRECTORS,
    COLLECTIONS,
}

/** What a sky node represents. Territory layers use [TERRITORY]. */
enum class MapNodeKind {
    FILM,
    DIRECTOR,
    COUNTRY,
    GENRE,
    CURRENT,
    DECADE,
    COLLECTION,
    TERRITORY,
}

/**
 * One node of a film-centred constellation.
 *
 * [ring] 0 = the focus film, 1 = its own territories, 2 = other films
 * ordered by how many attributes they share with the focus.
 */
data class ConstellationSeed(
    val id: String,
    val kind: MapNodeKind,
    val ring: Int,
    val relatedness: Int = 0,
    val sharedIds: List<String> = emptyList(),
)

data class MapVec(val x: Float, val y: Float) {
    operator fun plus(other: MapVec) = MapVec(x + other.x, y + other.y)
    operator fun minus(other: MapVec) = MapVec(x - other.x, y - other.y)
    operator fun times(scale: Float) = MapVec(x * scale, y * scale)
    val length: Float get() = hypot(x, y)
}

data class MapSeed(
    val id: String,
    val group: String = "",
)

data class CinemaMapNode(
    val id: String,
    val x: Float,
    val y: Float,
    val group: String = "",
    val kind: MapNodeKind = MapNodeKind.TERRITORY,
    val ring: Int = 1,
)

data class CinemaMapEdge(
    val left: String,
    val right: String,
    val weight: Int = 1,
)

data class CinemaMapGroupLabel(
    val text: String,
    val x: Float,
    val y: Float,
)

data class CinemaMapBounds(
    val minX: Float,
    val minY: Float,
    val maxX: Float,
    val maxY: Float,
) {
    val width: Float get() = maxX - minX
    val height: Float get() = maxY - minY
    val centerX: Float get() = (minX + maxX) / 2f
    val centerY: Float get() = (minY + maxY) / 2f
}

data class CinemaMapGraph(
    val layer: MapLayer,
    val nodes: List<CinemaMapNode>,
    val edges: List<CinemaMapEdge>,
    val groupLabels: List<CinemaMapGroupLabel> = emptyList(),
    val bounds: CinemaMapBounds = CinemaMapBounds(-1f, -1f, 1f, 1f),
    val focusId: String? = null,
)

data class MapCamera(
    val scale: Float = 1f,
    val panX: Float = 0f,
    val panY: Float = 0f,
) {
    fun worldToScreenX(worldX: Float): Float = worldX * scale + panX
    fun worldToScreenY(worldY: Float): Float = worldY * scale + panY
    fun screenToWorldX(screenX: Float): Float = (screenX - panX) / scale
    fun screenToWorldY(screenY: Float): Float = (screenY - panY) / scale
}

/**
 * Deterministic sky layout for one map layer.
 *
 * Coordinates live in a unit-free world space centred on (0, 0). Compose
 * only applies [MapCamera] afterwards. No physics engine: a few relaxation
 * steps pull co-occurring territories together.
 */
object CinemaMapLayout {
    const val MIN_SCALE = 0.22f
    const val MAX_SCALE = 14f
    const val DEFAULT_HIT_RADIUS = 26f
    const val MAX_RELATED_FILMS = 12
    private const val MAX_EDGES = 100
    private val RING1_KIND_ORDER = listOf(
        MapNodeKind.DIRECTOR,
        MapNodeKind.COUNTRY,
        MapNodeKind.GENRE,
        MapNodeKind.CURRENT,
        MapNodeKind.DECADE,
        MapNodeKind.COLLECTION,
    )
    private val CONTINENT_ORDER = listOf(
        "EUROPE",
        "ASIA",
        "AFRICA",
        "NORTH_AMERICA",
        "SOUTH_AMERICA",
        "OCEANIA",
    )

    /**
     * Places [seeds] and builds undirected edges from [bags] (one bag = codes
     * that share a film). Decade edges are the chronological neighbours instead.
     */
    fun build(
        layer: MapLayer,
        seeds: List<MapSeed>,
        bags: List<List<String>> = emptyList(),
        groupNames: Map<String, String> = emptyMap(),
    ): CinemaMapGraph {
        val unique = seeds.distinctBy { it.id }
        if (unique.isEmpty()) {
            return CinemaMapGraph(layer, emptyList(), emptyList())
        }
        val uncapped = when (layer) {
            MapLayer.DECADES -> sequentialEdges(unique.map { it.id })
            else -> cooccurrenceEdges(bags)
        }.filter { edge ->
            unique.any { it.id == edge.left } && unique.any { it.id == edge.right }
        }
        val edges = if (uncapped.size > MAX_EDGES) {
            uncapped.sortedByDescending { it.weight }.take(MAX_EDGES)
        } else {
            uncapped
        }
        val kind = layerKind(layer)
        val nodes = when (layer) {
            MapLayer.COUNTRIES, MapLayer.DIRECTORS -> clustered(unique, CONTINENT_ORDER, kind)
            MapLayer.DECADES -> timeline(unique, kind)
            MapLayer.CURRENTS, MapLayer.GENRES, MapLayer.COLLECTIONS, MapLayer.AROUND_FILM ->
                relaxed(unique, edges, kind)
        }
        val labels = groupLabels(nodes, groupNames)
        return CinemaMapGraph(
            layer = layer,
            nodes = nodes,
            edges = edges,
            groupLabels = labels,
            bounds = boundsOf(nodes, labels),
        )
    }

    /**
     * Drops ring-1 nodes that share a display label (director + homonymous
     * collection, for example) while keeping the more specific kind.
     */
    fun dedupeConstellation(
        members: List<ConstellationSeed>,
        labelOf: (ConstellationSeed) -> String,
    ): List<ConstellationSeed> {
        val focus = members.filter { it.ring == 0 }.distinctBy { it.id }
        val focusIds = focus.map { it.id }.toSet()
        val ring2 = members.filter { it.ring == 2 && it.id !in focusIds }.distinctBy { it.id }
        val seenLabels = mutableSetOf<String>()
        val ring1 = members.filter { it.ring == 1 }
            .distinctBy { it.kind to it.id }
            .sortedBy { seed ->
                val order = RING1_KIND_ORDER.indexOf(seed.kind)
                if (order < 0) 99 else order
            }
            .mapNotNull { seed ->
                val label = labelOf(seed).trim().lowercase()
                if (label.isNotEmpty() && !seenLabels.add(label)) null else seed
            }
        return focus + ring1 + ring2
    }

    /**
     * Places one film at the origin, its territories on nearby kind sectors,
     * and a capped set of related films further out (closer = more in common).
     */
    fun buildAround(focusId: String, members: List<ConstellationSeed>): CinemaMapGraph {
        val focus = members.firstOrNull { it.ring == 0 && it.id == focusId }
            ?: members.firstOrNull { it.ring == 0 }
            ?: return CinemaMapGraph(MapLayer.AROUND_FILM, emptyList(), emptyList(), focusId = focusId)
        val ring1 = members.filter { it.ring == 1 }.distinctBy { it.kind to it.id }
        val ring2 = members.filter { it.ring == 2 && it.id != focus.id }
            .distinctBy { it.id }
            .sortedByDescending { it.relatedness }
            .take(MAX_RELATED_FILMS)
        val nodes = mutableListOf<CinemaMapNode>()
        val edges = mutableListOf<CinemaMapEdge>()
        nodes += CinemaMapNode(focus.id, 0f, 0f, kind = focus.kind, ring = 0)
        val angleOf = linkedMapOf<String, Float>()
        val kindsPresent = RING1_KIND_ORDER.filter { kind -> ring1.any { it.kind == kind } } +
            ring1.map { it.kind }.distinct().filter { it !in RING1_KIND_ORDER }
        val kindCount = kindsPresent.size.coerceAtLeast(1)
        kindsPresent.forEachIndexed { kindIndex, kind ->
            val group = ring1.filter { it.kind == kind }
            val sector = 2f * PI.toFloat() / kindCount
            val gap = sector * 0.18f
            val start = -PI.toFloat() / 2f + kindIndex * sector + gap / 2f
            val span = (sector - gap).coerceAtLeast(0.01f)
            val radius = 76f + kindIndex * 12f
            group.forEachIndexed { index, seed ->
                val t = if (group.size == 1) {
                    0.5f
                } else {
                    index.toFloat() / (group.size - 1).coerceAtLeast(1)
                }
                val angle = start + t * span
                angleOf[seed.id] = angle
                nodes += CinemaMapNode(
                    seed.id,
                    cos(angle) * radius,
                    sin(angle) * radius,
                    kind = seed.kind,
                    ring = 1,
                )
                edges += CinemaMapEdge(focus.id, seed.id, weight = 3)
            }
        }
        val maxRelated = ring2.maxOfOrNull { it.relatedness }?.coerceAtLeast(1) ?: 1
        ring2.forEachIndexed { index, seed ->
            val sharedAngles = seed.sharedIds.mapNotNull { angleOf[it] }
            val angle = if (sharedAngles.isEmpty()) {
                index * (2f * PI.toFloat() / ring2.size.coerceAtLeast(1))
            } else {
                val sinSum = sharedAngles.sumOf { sin(it.toDouble()) }
                val cosSum = sharedAngles.sumOf { cos(it.toDouble()) }
                atan2(sinSum, cosSum).toFloat() + index * 0.07f
            }
            val closeness = seed.relatedness.toFloat() / maxRelated
            val radius = 168f + (1f - closeness) * 78f
            nodes += CinemaMapNode(
                seed.id,
                cos(angle) * radius,
                sin(angle) * radius,
                kind = seed.kind,
                ring = 2,
            )
            edges += CinemaMapEdge(focus.id, seed.id, weight = 1)
            seed.sharedIds.distinct().forEach { shared ->
                if (ring1.any { it.id == shared }) {
                    edges += CinemaMapEdge(seed.id, shared, weight = 2)
                }
            }
        }
        return CinemaMapGraph(
            layer = MapLayer.AROUND_FILM,
            nodes = nodes,
            edges = edges,
            bounds = boundsOf(nodes, emptyList()),
            focusId = focus.id,
        )
    }

    /** Nearest node whose centre is within [radius] world units of the tap. */
    fun hitTest(graph: CinemaMapGraph, worldX: Float, worldY: Float, radius: Float): CinemaMapNode? {
        var best: CinemaMapNode? = null
        var bestDist = radius
        graph.nodes.forEach { node ->
            val dist = hypot(node.x - worldX, node.y - worldY)
            if (dist <= bestDist) {
                best = node
                bestDist = dist
            }
        }
        return best
    }

    /**
     * Camera that fits [graph] inside a viewport, with a small margin.
     * Empty graphs keep scale 1 and a zero pan.
     */
    fun fit(graph: CinemaMapGraph, viewportWidth: Float, viewportHeight: Float, margin: Float = 0.86f): MapCamera {
        if (graph.nodes.isEmpty() || viewportWidth <= 0f || viewportHeight <= 0f) return MapCamera()
        val width = graph.bounds.width.coerceAtLeast(80f)
        val height = graph.bounds.height.coerceAtLeast(80f)
        val scale = (min(viewportWidth / width, viewportHeight / height) * margin)
            .coerceIn(MIN_SCALE, MAX_SCALE)
        return MapCamera(
            scale = scale,
            panX = viewportWidth / 2f - graph.bounds.centerX * scale,
            panY = viewportHeight / 2f - graph.bounds.centerY * scale,
        )
    }

    /** Frames [node] near the viewport centre, zooming in if the camera was wide. */
    fun focus(
        node: CinemaMapNode,
        viewportWidth: Float,
        viewportHeight: Float,
        currentScale: Float,
    ): MapCamera {
        val scale = currentScale.coerceIn(1.65f, 3.8f)
        return MapCamera(
            scale = scale,
            panX = viewportWidth / 2f - node.x * scale,
            panY = viewportHeight / 2f - node.y * scale,
        )
    }

    /** Pinch-zoom around a screen point, then apply the pan delta. */
    fun zoomAround(
        camera: MapCamera,
        screenX: Float,
        screenY: Float,
        zoom: Float,
        panDeltaX: Float,
        panDeltaY: Float,
    ): MapCamera {
        val newScale = (camera.scale * zoom).coerceIn(MIN_SCALE, MAX_SCALE)
        val worldX = camera.screenToWorldX(screenX)
        val worldY = camera.screenToWorldY(screenY)
        return MapCamera(
            scale = newScale,
            panX = screenX - worldX * newScale + panDeltaX,
            panY = screenY - worldY * newScale + panDeltaY,
        )
    }

    internal fun cooccurrenceEdges(bags: List<List<String>>): List<CinemaMapEdge> {
        val counts = linkedMapOf<String, Int>()
        bags.forEach { bag ->
            val codes = bag.distinct().sorted()
            for (i in codes.indices) {
                for (j in i + 1 until codes.size) {
                    val key = codes[i] + "\u0000" + codes[j]
                    counts[key] = (counts[key] ?: 0) + 1
                }
            }
        }
        return counts.map { (key, weight) ->
            val parts = key.split('\u0000')
            CinemaMapEdge(parts[0], parts[1], weight)
        }
    }

    private fun sequentialEdges(ids: List<String>): List<CinemaMapEdge> {
        val ordered = ids.sortedBy { it.toIntOrNull() ?: 0 }
        return ordered.zipWithNext { a, b -> CinemaMapEdge(a, b, 1) }
    }

    private fun sunflower(count: Int, radius: Float): List<MapVec> {
        if (count <= 0) return emptyList()
        val golden = PI.toFloat() * (3f - sqrt(5f))
        return (0 until count).map { index ->
            val r = radius * sqrt((index + 0.5f) / count)
            val angle = index * golden
            MapVec(r * cos(angle), r * sin(angle))
        }
    }

    private fun layerKind(layer: MapLayer): MapNodeKind = when (layer) {
        MapLayer.AROUND_FILM -> MapNodeKind.FILM
        MapLayer.CURRENTS -> MapNodeKind.CURRENT
        MapLayer.COUNTRIES -> MapNodeKind.COUNTRY
        MapLayer.DECADES -> MapNodeKind.DECADE
        MapLayer.GENRES -> MapNodeKind.GENRE
        MapLayer.DIRECTORS -> MapNodeKind.DIRECTOR
        MapLayer.COLLECTIONS -> MapNodeKind.COLLECTION
    }

    private fun clustered(
        seeds: List<MapSeed>,
        groupOrder: List<String>,
        kind: MapNodeKind,
    ): List<CinemaMapNode> {
        val grouped = linkedMapOf<String, MutableList<MapSeed>>()
        groupOrder.forEach { grouped[it] = mutableListOf() }
        grouped[""] = mutableListOf()
        seeds.forEach { seed ->
            val key = if (seed.group in grouped) seed.group else ""
            grouped.getValue(key).add(seed)
        }
        val occupied = grouped.filter { it.value.isNotEmpty() }
        val keys = occupied.keys.toList()
        val result = mutableListOf<CinemaMapNode>()
        keys.forEachIndexed { index, key ->
            val members = occupied.getValue(key).sortedBy { it.id }
            val center = if (keys.size == 1) {
                MapVec(0f, 0f)
            } else {
                val angle = -PI.toFloat() / 2f + index * (2f * PI.toFloat() / keys.size)
                MapVec(cos(angle) * 280f, sin(angle) * 280f)
            }
            val local = sunflower(members.size, 36f + 14f * sqrt(members.size.toFloat()))
            members.forEachIndexed { memberIndex, seed ->
                val pos = center + local[memberIndex]
                result += CinemaMapNode(seed.id, pos.x, pos.y, seed.group, kind = kind)
            }
        }
        return result
    }

    private fun timeline(seeds: List<MapSeed>, kind: MapNodeKind): List<CinemaMapNode> {
        val ordered = seeds.sortedBy { it.id.toIntOrNull() ?: 0 }
        if (ordered.size == 1) {
            return listOf(CinemaMapNode(ordered[0].id, 0f, 0f, ordered[0].group, kind = kind))
        }
        val span = 520f
        return ordered.mapIndexed { index, seed ->
            val t = index.toFloat() / (ordered.size - 1).coerceAtLeast(1)
            val x = -span / 2f + t * span
            val y = sin(t * PI.toFloat()) * 48f
            CinemaMapNode(seed.id, x, y, seed.group, kind = kind)
        }
    }

    private fun relaxed(
        seeds: List<MapSeed>,
        edges: List<CinemaMapEdge>,
        kind: MapNodeKind,
    ): List<CinemaMapNode> {
        val initial = sunflower(seeds.size, 260f)
        val ordered = seeds.sortedBy { it.id }
        val nodes = ordered.mapIndexed { index, seed ->
            CinemaMapNode(seed.id, initial[index].x, initial[index].y, seed.group, kind = kind)
        }.toMutableList()
        val indexOf = nodes.mapIndexed { index, node -> node.id to index }.toMap()
        val iterations = if (nodes.size > 80) 12 else 36
        repeat(iterations) {
            val disp = Array(nodes.size) { MapVec(0f, 0f) }
            for (i in nodes.indices) {
                for (j in i + 1 until nodes.size) {
                    var dx = nodes[i].x - nodes[j].x
                    var dy = nodes[i].y - nodes[j].y
                    if (dx == 0f && dy == 0f) {
                        dx = 0.7f
                        dy = 0.3f
                    }
                    val dist = hypot(dx, dy).coerceAtLeast(8f)
                    val force = 650f / (dist * dist)
                    val fx = dx / dist * force
                    val fy = dy / dist * force
                    disp[i] = disp[i] + MapVec(fx, fy)
                    disp[j] = disp[j] - MapVec(fx, fy)
                }
            }
            edges.forEach { edge ->
                val i = indexOf[edge.left] ?: return@forEach
                val j = indexOf[edge.right] ?: return@forEach
                val dx = nodes[j].x - nodes[i].x
                val dy = nodes[j].y - nodes[i].y
                val dist = hypot(dx, dy).coerceAtLeast(8f)
                val rest = 88f
                val pull = (dist - rest) * 0.018f * edge.weight.coerceAtMost(6)
                val fx = dx / dist * pull
                val fy = dy / dist * pull
                disp[i] = disp[i] + MapVec(fx, fy)
                disp[j] = disp[j] - MapVec(fx, fy)
            }
            for (i in nodes.indices) {
                val step = disp[i]
                val len = step.length.coerceAtLeast(0.001f)
                val cap = 5.5f
                val scaled = if (len > cap) step * (cap / len) else step
                nodes[i] = nodes[i].copy(x = nodes[i].x + scaled.x, y = nodes[i].y + scaled.y)
            }
        }
        return nodes
    }

    private fun groupLabels(
        nodes: List<CinemaMapNode>,
        names: Map<String, String>,
    ): List<CinemaMapGroupLabel> {
        if (names.isEmpty()) return emptyList()
        return nodes.groupBy { it.group }
            .filterKeys { it.isNotBlank() && it in names }
            .map { (group, members) ->
                CinemaMapGroupLabel(
                    text = names.getValue(group),
                    x = members.map { it.x }.average().toFloat(),
                    y = members.minOf { it.y } - 28f,
                )
            }
    }

    private fun boundsOf(
        nodes: List<CinemaMapNode>,
        labels: List<CinemaMapGroupLabel>,
    ): CinemaMapBounds {
        val xs = nodes.map { it.x } + labels.map { it.x }
        val ys = nodes.map { it.y } + labels.map { it.y }
        val pad = 36f
        return CinemaMapBounds(
            minX = (xs.minOrNull() ?: 0f) - pad,
            minY = (ys.minOrNull() ?: 0f) - pad,
            maxX = (xs.maxOrNull() ?: 0f) + pad,
            maxY = (ys.maxOrNull() ?: 0f) + pad,
        )
    }
}

/** Angle of the vector from [from] to [to], for optional edge ticks. */
fun mapAngle(from: CinemaMapNode, to: CinemaMapNode): Float =
    atan2(to.y - from.y, to.x - from.x)
