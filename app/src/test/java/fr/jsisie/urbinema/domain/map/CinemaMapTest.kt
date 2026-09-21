package fr.jsisie.urbinema.domain.map

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.hypot

class CinemaMapTest {
    @Test
    fun `countries of the same continent sit closer than distant continents`() {
        val graph = CinemaMapLayout.build(
            MapLayer.COUNTRIES,
            listOf(
                MapSeed("FRANCE", "EUROPE"),
                MapSeed("ITALY", "EUROPE"),
                MapSeed("JAPAN", "ASIA"),
            ),
        )
        val france = graph.nodes.single { it.id == "FRANCE" }
        val italy = graph.nodes.single { it.id == "ITALY" }
        val japan = graph.nodes.single { it.id == "JAPAN" }
        val europe = hypot(france.x - italy.x, france.y - italy.y)
        val far = hypot(france.x - japan.x, france.y - japan.y)
        assertTrue("europe=$europe far=$far", europe < far)
    }

    @Test
    fun `decades are ordered left to right`() {
        val graph = CinemaMapLayout.build(
            MapLayer.DECADES,
            listOf(MapSeed("1960"), MapSeed("1950"), MapSeed("1970")),
        )
        val xs = graph.nodes.associate { it.id to it.x }
        assertTrue(xs.getValue("1950") < xs.getValue("1960"))
        assertTrue(xs.getValue("1960") < xs.getValue("1970"))
        assertEquals(2, graph.edges.size)
    }

    @Test
    fun `cooccurrence edges are undirected and weighted`() {
        val edges = CinemaMapLayout.cooccurrenceEdges(
            listOf(
                listOf("FRANCE", "ITALY"),
                listOf("ITALY", "FRANCE"),
                listOf("JAPAN"),
            ),
        )
        assertEquals(1, edges.size)
        assertEquals(2, edges.single().weight)
    }

    @Test
    fun `hit test returns the nearest node inside the radius`() {
        val graph = CinemaMapLayout.build(
            MapLayer.GENRES,
            listOf(MapSeed("DRAME"), MapSeed("COMEDIE")),
        )
        val target = graph.nodes.first()
        val hit = CinemaMapLayout.hitTest(graph, target.x + 3f, target.y - 2f, 20f)
        assertEquals(target.id, hit?.id)
        val miss = CinemaMapLayout.hitTest(graph, target.x + 400f, target.y, 20f)
        assertEquals(null, miss)
    }

    @Test
    fun `fit then screen-world roundtrip keeps the centre`() {
        val graph = CinemaMapLayout.build(
            MapLayer.CURRENTS,
            listOf(MapSeed("A"), MapSeed("B"), MapSeed("C")),
        )
        val camera = CinemaMapLayout.fit(graph, 800f, 1200f)
        val sx = camera.worldToScreenX(graph.bounds.centerX)
        val sy = camera.worldToScreenY(graph.bounds.centerY)
        assertEquals(graph.bounds.centerX, camera.screenToWorldX(sx), 0.05f)
        assertEquals(graph.bounds.centerY, camera.screenToWorldY(sy), 0.05f)
        assertTrue(hypot(sx - 400f, sy - 600f) < 8f)
    }

    @Test
    fun `zoom around a point keeps that world point under the finger`() {
        val start = MapCamera(scale = 1f, panX = 40f, panY = 80f)
        val screenX = 200f
        val screenY = 300f
        val worldX = start.screenToWorldX(screenX)
        val worldY = start.screenToWorldY(screenY)
        val zoomed = CinemaMapLayout.zoomAround(start, screenX, screenY, 2f, 0f, 0f)
        assertEquals(worldX, zoomed.screenToWorldX(screenX), 0.05f)
        assertEquals(worldY, zoomed.screenToWorldY(screenY), 0.05f)
        assertNotNull(zoomed)
    }

    @Test
    fun `focus places the node near the viewport centre`() {
        val node = CinemaMapNode("FRANCE", 120f, -40f)
        val camera = CinemaMapLayout.focus(node, 800f, 1200f, 1.2f)
        val sx = camera.worldToScreenX(node.x)
        val sy = camera.worldToScreenY(node.y)
        assertEquals(400f, sx, 0.5f)
        assertEquals(600f, sy, 0.5f)
        assertTrue(camera.scale >= 1.65f)
    }

    @Test
    fun `around a film keeps related films farther than its own territories`() {
        val graph = CinemaMapLayout.buildAround(
            "SEVEN_SAMURAI",
            listOf(
                ConstellationSeed("SEVEN_SAMURAI", MapNodeKind.FILM, 0),
                ConstellationSeed("AKIRA_KUROSAWA", MapNodeKind.DIRECTOR, 1),
                ConstellationSeed("JAPAN", MapNodeKind.COUNTRY, 1),
                ConstellationSeed("RASHOMON", MapNodeKind.FILM, 2, 6, listOf("AKIRA_KUROSAWA", "JAPAN")),
                ConstellationSeed("OTHER", MapNodeKind.FILM, 2, 1, listOf("JAPAN")),
            ),
        )
        val focus = graph.nodes.single { it.ring == 0 }
        val japan = graph.nodes.single { it.id == "JAPAN" }
        val closeFilm = graph.nodes.single { it.id == "RASHOMON" }
        val farFilm = graph.nodes.single { it.id == "OTHER" }
        val japanDist = hypot(japan.x - focus.x, japan.y - focus.y)
        val closeDist = hypot(closeFilm.x - focus.x, closeFilm.y - focus.y)
        val farDist = hypot(farFilm.x - focus.x, farFilm.y - focus.y)
        assertTrue("japan=$japanDist close=$closeDist", japanDist < closeDist)
        assertTrue("close=$closeDist far=$farDist", closeDist < farDist)
        assertEquals("SEVEN_SAMURAI", graph.focusId)
        val director = graph.nodes.single { it.id == "AKIRA_KUROSAWA" }
        assertTrue(
            "director and country should not share a radius",
            hypot(director.x, director.y) != japanDist,
        )
    }

    @Test
    fun `homonymous collection is dropped when the director is already present`() {
        val members = CinemaMapLayout.dedupeConstellation(
            listOf(
                ConstellationSeed("SEVEN_SAMURAI", MapNodeKind.FILM, 0),
                ConstellationSeed("AKIRA_KUROSAWA", MapNodeKind.DIRECTOR, 1),
                ConstellationSeed("COLLECTION_KUROSAWA", MapNodeKind.COLLECTION, 1),
                ConstellationSeed("JAPAN", MapNodeKind.COUNTRY, 1),
            ),
        ) { seed ->
            when (seed.id) {
                "AKIRA_KUROSAWA", "COLLECTION_KUROSAWA" -> "Akira Kurosawa"
                "JAPAN" -> "Japon"
                else -> seed.id
            }
        }
        assertEquals(setOf("AKIRA_KUROSAWA", "JAPAN"), members.filter { it.ring == 1 }.map { it.id }.toSet())
        assertEquals(MapNodeKind.DIRECTOR, members.single { it.id == "AKIRA_KUROSAWA" }.kind)
    }

    @Test
    fun `directors layer nodes keep the director kind`() {
        val graph = CinemaMapLayout.build(
            MapLayer.DIRECTORS,
            listOf(MapSeed("AKIRA_KUROSAWA", "ASIA"), MapSeed("AGNES_VARDA", "EUROPE")),
        )
        assertTrue(graph.nodes.all { it.kind == MapNodeKind.DIRECTOR })
    }

    @Test
    fun `pinch zoom can go well past the former 6_5 cap`() {
        val start = MapCamera(scale = 6f, panX = 0f, panY = 0f)
        val zoomed = CinemaMapLayout.zoomAround(start, 100f, 100f, 2f, 0f, 0f)
        assertTrue(zoomed.scale > 6.5f)
        assertTrue(zoomed.scale <= CinemaMapLayout.MAX_SCALE)
    }
}
