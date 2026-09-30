package fr.jsisie.urbinema.ui.model

import androidx.annotation.StringRes
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.data.media.MediaPaths
import fr.jsisie.urbinema.domain.map.CinemaMapGraph
import fr.jsisie.urbinema.domain.map.CinemaMapLayout
import fr.jsisie.urbinema.domain.map.ConstellationSeed
import fr.jsisie.urbinema.domain.map.MapLayer
import fr.jsisie.urbinema.domain.map.MapNodeKind
import fr.jsisie.urbinema.domain.map.MapSeed
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeMode

enum class LoadState { Loading, Content, Empty, Error }
enum class ExplorationState { Unexplored, InProgress, Explored, Completed, Mastered }
enum class AppLanguage { System, French, English }
enum class SearchKind { Movie, Country, Current, Collection, Director, Genre }
enum class AtlasFilter { Countries, Currents, Decades, Genres, Directors }
enum class StatsCategory { Films, Countries, Decades, Currents, Continents, Directors }

data class QuestUi(
    @StringRes val title: Int,
    val condition: String,
    val rewardXp: Int,
    val progress: Int,
    val target: Int,
)

data class MovieSummaryUi(
    val id: String,
    val title: String,
    val year: Int,
    val director: String = "",
    val watched: Boolean = false,
)

enum class FilmListSort {
    TitleAsc,
    TitleDesc,
    YearAsc,
    YearDesc,
}

private val filmTitleCollator: java.text.Collator = java.text.Collator.getInstance(java.util.Locale.FRENCH).apply {
    strength = java.text.Collator.PRIMARY
}

/**
 * Leading articles ignored for A–Z order and the letter scrubber.
 * Longest match first so "les " wins over "le ", "l'" over bare "l".
 */
fun filmSortKey(title: String): String {
    var working = title.trim().trimStart('"', '\'', '«', '»', '“', '”', '‘', '’')
    val lower = working.lowercase()
    val article = LEADING_ARTICLES.firstOrNull { lower.startsWith(it) }
    if (article != null) {
        working = working.substring(article.length).trim()
    }
    return working.ifBlank { title.trim() }
}

/** Same article rules as [filmSortKey] — never the raw first character of "Les" / "L'". */
fun filmIndexLetter(title: String): Char {
    val key = filmSortKey(title)
    val first = key.firstOrNull { it.isLetter() }?.uppercaseChar() ?: return '#'
    return if (first in 'A'..'Z') first else '#'
}

/** Lists show two directors, then "..." when the film has more. */
fun listDirectorLabel(names: List<String>): String {
    val cleaned = names.map { it.trim() }.filter { it.isNotEmpty() }
    return when {
        cleaned.size <= 2 -> cleaned.joinToString(", ")
        else -> cleaned.take(2).joinToString(", ") + "..."
    }
}

fun List<MovieSummaryUi>.sortedFilms(sort: FilmListSort): List<MovieSummaryUi> = when (sort) {
    FilmListSort.TitleAsc -> sortedWith(compareByTitleAsc())
    FilmListSort.TitleDesc -> sortedWith(compareByTitleDesc())
    FilmListSort.YearAsc -> sortedWith(
        Comparator { left, right ->
            val byYear = left.year.compareTo(right.year)
            if (byYear != 0) byYear else compareByTitleAsc().compare(left, right)
        },
    )
    FilmListSort.YearDesc -> sortedWith(
        Comparator { left, right ->
            val byYear = right.year.compareTo(left.year)
            if (byYear != 0) byYear else compareByTitleAsc().compare(left, right)
        },
    )
}

private fun compareByTitleAsc(): Comparator<MovieSummaryUi> =
    Comparator { left, right ->
        val byTitle = filmTitleCollator.compare(filmSortKey(left.title), filmSortKey(right.title))
        if (byTitle != 0) byTitle else left.year.compareTo(right.year)
    }

private fun compareByTitleDesc(): Comparator<MovieSummaryUi> =
    Comparator { left, right ->
        val byTitle = filmTitleCollator.compare(filmSortKey(right.title), filmSortKey(left.title))
        if (byTitle != 0) byTitle else right.year.compareTo(left.year)
    }

private val LEADING_ARTICLES: List<String> = listOf(
    "the ", "les ", "los ", "las ", "die ", "der ", "das ",
    "une ", "un ", "le ", "la ", "el ", "il ", "lo ",
    "l'", "l’", "a ", "an ",
)

enum class CollectionTrack {
    GATEWAY,
    CLUB,
    DARKROOM,
    CINEMATHEQUE,
    OFFSCREEN,
    ;

    val titleRes: Int
        get() = when (this) {
            GATEWAY -> R.string.collection_track_gateway
            CLUB -> R.string.collection_track_journey
            DARKROOM -> R.string.collection_track_darkroom
            CINEMATHEQUE -> R.string.collection_track_demanding
            OFFSCREEN -> R.string.collection_track_offscreen
        }
}

enum class BadgeRarity {
    EXTRA,
    SUPPORTING,
    HEADLINER,
    ;

    val titleRes: Int
        get() = when (this) {
            EXTRA -> R.string.badge_rarity_extra
            SUPPORTING -> R.string.badge_rarity_supporting
            HEADLINER -> R.string.badge_rarity_headliner
        }

    companion object {
        fun fromDifficulty(difficulty: Int): BadgeRarity = when {
            difficulty <= 2 -> EXTRA
            difficulty == 3 -> SUPPORTING
            else -> HEADLINER
        }
    }
}

enum class HelpTopic {
    All,
    Collections,
    Atlas,
    InteractiveMap,
    Progress,
}

data class CollectionUi(
    val id: String,
    val name: String,
    val metadata: String,
    val shortDescription: String,
    val longDescription: String,
    val progress: Int,
    val films: List<MovieSummaryUi> = emptyList(),
    val countryCodes: List<String> = emptyList(),
    val characteristicCodes: List<String> = emptyList(),
    val followed: Boolean = false,
    val displayOrder: Int = 0,
    val track: CollectionTrack = CollectionTrack.GATEWAY,
    val locked: Boolean = false,
    val lockPreviousTrack: CollectionTrack? = null,
    val lockRequiredCollections: Int = 2,
    val completed: Boolean = false,
)

/** One pedagogical path, opened from the Parcours tab. */
data class PathUi(
    val id: String,
    val name: String,
    val summary: String,
    val description: String,
    val periodLabel: String,
    val steps: List<PathStepUi>,
)

/** A current bubble. `transition` is the text toward the next bubble. */
data class PathStepUi(
    val id: String,
    val name: String,
    val periodLabel: String,
    val description: String,
    val imageCode: String,
    val facts: List<PathFactUi>,
    val figures: List<PathFigureUi>,
    val movies: List<MovieSummaryUi>,
    val transition: String?,
)

data class PathFactUi(val title: String, val body: String)

/** `directorCode` is null when the person has no director fiche. */
data class PathFigureUi(val name: String, val role: String, val directorCode: String?)

data class HistoryUi(
    val dateLabel: String,
    val type: String,
    val subject: String = "",
) {
    companion object {
        const val MOVIE_VALIDATED = "MOVIE_VALIDATED"
        const val BADGE_EARNED = "BADGE_EARNED"
        const val QUEST_COMPLETED = "QUEST_COMPLETED"
        const val RANK_UP = "RANK_UP"
        const val HOME_PREVIEW_LIMIT = 30
    }
}

data class HomeUiState(
    val loadState: LoadState = LoadState.Content,
    val rank: String = "Novice",
    val rankNumber: Int = 1,
    val rankLongDescription: String = "",
    val level: Int = 1,
    val xp: Int = 0,
    val nextLevelXp: Int = 115,
    val quests: List<QuestUi> = emptyList(),
    val collections: List<CollectionUi> = emptyList(),
    val history: List<HistoryUi> = emptyList(),
    val dev: DevProgressUi? = null,
)

/** Exact rank score and XP, shown only while dev mode is on. */
data class DevProgressUi(
    val rankOrder: Int,
    val rawRank: Int,
    val score: Double,
    val floor: Double,
    val nextThreshold: Double?,
    val remaining: Double,
    val fraction: Float,
    val lastScoreGain: Double?,
    val weightedVolume: Double,
    val diversity: Double,
    val depth: Double,
    val xpIntoLevel: Int,
    val xpRemaining: Int?,
    val xpFraction: Float,
    val lastXpGain: Int?,
)

data class TerritoryUi(
    val id: String,
    val name: String,
    @StringRes val category: Int,
    val progress: Int,
    val state: ExplorationState,
    val subtitle: String = "",
    val filmCount: Int = 0,
)

data class DirectorCreditUi(val id: String, val name: String)

data class MovieUi(
    val id: String,
    val originalTitle: String,
    val localizedTitle: String?,
    val credits: String,
    val metadata: String,
    val synopsis: String,
    val watched: Boolean,
    val countries: List<TerritoryUi> = emptyList(),
    val genres: List<TerritoryUi> = emptyList(),
    val directorIds: List<String> = emptyList(),
    val releaseYear: Int = 0,
    val directorCredits: List<DirectorCreditUi> = emptyList(),
)

data class BadgeUi(
    val code: String,
    val name: String,
    val condition: String,
    val earned: Boolean,
    val difficulty: Int = 1,
    val showcaseSlot: Int? = null,
) {
    val rarity: BadgeRarity get() = BadgeRarity.fromDifficulty(difficulty)
}

data class RankUi(
    val id: String,
    val order: Int,
    val name: String,
    val description: String,
    val longDescription: String,
    val current: Boolean,
)

data class ProfileUiState(
    val nickname: String = "Léo",
    val ageYears: Int? = null,
    val rank: String = "Novice",
    val rankCode: String = "RANK_01",
    val rankNumber: Int = 1,
    val rankLongDescription: String = "",
    val level: Int = 1,
    val xp: Int = 0,
    val xpIntoLevel: Int = 0,
    val nextLevelXp: Int = 115,
    val films: Int = 0,
    val countries: Int = 0,
    val decades: Int = 0,
    val currents: Int = 0,
    val continents: Int = 0,
    val directors: Int = 0,
    val avatarCode: String? = null,
    val dev: DevProgressUi? = null,
)

data class SearchHitUi(
    val id: String,
    val kind: SearchKind,
    val title: String,
    val subtitle: String,
)

data class DirectorUi(
    val id: String,
    val name: String,
    val films: List<MovieSummaryUi>,
    val collections: List<CollectionUi> = emptyList(),
    val biography: String = "",
)

data class StatsListsUi(
    val films: List<MovieSummaryUi> = emptyList(),
    val countries: List<String> = emptyList(),
    val decades: List<String> = emptyList(),
    val currents: List<String> = emptyList(),
    val continents: List<String> = emptyList(),
    val directors: List<String> = emptyList(),
)

/** UI-only contract, ready to be implemented by a domain-backed ViewModel. */
interface UrbinemaViewModel {
    val home: HomeUiState
    val territories: List<TerritoryUi>
    val currents: List<TerritoryUi>
    val decades: List<TerritoryUi>
    val genres: List<TerritoryUi>
    val collections: List<CollectionUi>
    val paths: List<PathUi>
    val badges: List<BadgeUi>
    val ranks: List<RankUi>
    val directors: List<DirectorUi>
    val movie: MovieUi
    val profile: ProfileUiState
    val statsLists: StatsListsUi
    val themeMode: UrbinemaThemeMode
    val language: AppLanguage
    val filmGrain: Boolean
    /** True only when `urbinema.devTools` was true at compile time. */
    val devToolsAvailable: Boolean get() = false
    val devMode: Boolean get() = false
    val needsOnboarding: Boolean
    val completedCollectionCelebration: String?
    val unlockedBadgeCelebration: String?
    val followLimitReached: Boolean
    val showAppGuide: Boolean
    val rankUpCelebration: String?
    val availableAvatars: List<String>
    fun setThemeMode(mode: UrbinemaThemeMode)
    fun setLanguage(language: AppLanguage)
    fun setFilmGrain(enabled: Boolean)
    fun setDevMode(enabled: Boolean) {}
    fun setUsername(username: String)
    fun setAge(age: Int)
    fun setAvatar(code: String)
    fun completeOnboarding(username: String, age: Int, avatarCode: String)
    fun markCurrentMovieWatched()
    fun markMovieWatched(code: String)
    fun followCollection(code: String)
    fun unfollowCollection(code: String)
    fun setShowcaseBadges(codes: List<String>)
    fun openMovie(code: String)
    fun movie(code: String): MovieUi?
    fun director(code: String): DirectorUi?
    fun search(query: String): List<SearchHitUi>
    fun collectionsForCountry(code: String): List<CollectionUi>
    fun collectionsForCurrent(code: String): List<CollectionUi>
    fun moviesForCountry(code: String): List<MovieSummaryUi>
    fun moviesForCurrent(code: String): List<MovieSummaryUi>
    fun moviesForDecade(code: String): List<MovieSummaryUi>
    fun moviesForGenre(code: String): List<MovieSummaryUi>
    fun cinemaMap(layer: MapLayer, focusMovieCode: String = ""): CinemaMapGraph
    fun defaultSkyMovieCode(): String
    fun mapNodeUi(id: String, kind: MapNodeKind): TerritoryUi?
    fun resetProgress()
    fun retryBootstrap()
    fun dismissCollectionCelebration()
    fun dismissBadgeCelebration()
    fun dismissFollowLimit()
    fun replayAppGuide()
    fun dismissAppGuide()
    fun dismissRankUp()
}

private val previewFilms = listOf(
    MovieSummaryUi("ROMA_CITTA_APERTA_1945", "Rome, ville ouverte", 1945, "Roberto Rossellini"),
    MovieSummaryUi("CLEO_DE_5_A_7_1962", "Cléo de 5 à 7", 1962, "Agnès Varda"),
    MovieSummaryUi("SEPT_SAMOURAIS_1954", "Les Sept Samouraïs", 1954, "Akira Kurosawa"),
)

/** Deterministic preview data that keeps Compose independent from unfinished data layers. */
object PreviewUrbinemaViewModel : UrbinemaViewModel {
    override val paths = emptyList<PathUi>()
    override val collections = listOf(
        CollectionUi(
            "COLLECTION_001",
            "Néoréalisme italien",
            "Italie · 1943–1952",
            "Les gestes fondateurs d'un cinéma tourné vers la rue et l'après-guerre.",
            "Né à Rome dans les ruines de 1943, le néoréalisme italien filme la vie ordinaire avec des non-comédiens, la lumière du jour et les rues encore marquées par l'Occupation. Rossellini, De Sica et Visconti en sont les voix les plus nettes.",
            35,
            listOf(previewFilms[0]),
            countryCodes = listOf("ITALY"),
            characteristicCodes = listOf("NEOREALISME_ITALIEN"),
        ),
        CollectionUi(
            "COLLECTION_002",
            "Nouvelle Vague",
            "France · 1958–1968",
            "Une liberté de tournage et de récit qui transforme le cinéma français.",
            "Autour de 1959, de jeunes critiques des Cahiers du cinéma passent derrière la caméra. Godard, Truffaut, Varda et Rivette inventent un cinéma parlé, improvisé, filmé dans Paris.",
            18,
            listOf(previewFilms[1]),
            countryCodes = listOf("FRANCE"),
            characteristicCodes = listOf("NOUVELLE_VAGUE_FRANCAISE"),
        ),
        CollectionUi(
            "COLLECTION_003",
            "Âge d'or japonais",
            "Japon · 1930–1960",
            "Quelques portes d'entrée vers l'âge d'or du cinéma japonais.",
            "Des années 1930 aux années 1960, le studio japonais produit des fresques, des mélodrames et des films de samouraïs d'une précision formelle rare. Kurosawa, Ozu et Mizoguchi en sont les sommets.",
            62,
            listOf(previewFilms[2]),
            countryCodes = listOf("JAPAN"),
            characteristicCodes = listOf("AGE_OR_CINEMA_JAPONAIS"),
        ),
    )
    override val home = HomeUiState(
        quests = listOf(
            QuestUi(R.string.quest_bronze_title, "Voir 1 film muet", 100, 1, 1),
            QuestUi(R.string.quest_silver_title, "Voir 3 films asiatiques", 250, 2, 3),
            QuestUi(R.string.quest_gold_title, "Voir 5 films sortis avant 1950", 500, 1, 5),
        ),
        collections = collections,
        history = listOf(
            HistoryUi("today", HistoryUi.MOVIE_VALIDATED, "Les Sept Samouraïs"),
            HistoryUi("yesterday", HistoryUi.BADGE_EARNED, "Premier Rideau"),
        ),
        rankLongDescription = "Découvre encore le cinéma. Culture très limitée ou principalement composée de films populaires / contemporains.",
    )
    override val territories = listOf(
        TerritoryUi("FRANCE", "France", R.string.countries, 82, ExplorationState.Mastered),
        TerritoryUi("JAPAN", "Japon", R.string.countries, 54, ExplorationState.Completed),
        TerritoryUi("IRAN", "Iran", R.string.countries, 24, ExplorationState.InProgress),
        TerritoryUi("SOUTH_KOREA", "Corée du Sud", R.string.countries, 8, ExplorationState.Explored),
        TerritoryUi("SENEGAL", "Sénégal", R.string.countries, 0, ExplorationState.Unexplored),
    )
    override val currents = listOf(
        TerritoryUi("NEOREALISME_ITALIEN", "Néoréalisme italien", R.string.currents, 35, ExplorationState.InProgress),
        TerritoryUi("NOUVELLE_VAGUE_FRANCAISE", "Nouvelle Vague française", R.string.currents, 18, ExplorationState.Explored),
        TerritoryUi("AGE_OR_CINEMA_JAPONAIS", "Âge d'or du cinéma japonais", R.string.currents, 62, ExplorationState.Completed),
    )
    override val decades = listOf(
        TerritoryUi("1950", "Années 1950", R.string.decades, 40, ExplorationState.InProgress),
        TerritoryUi("1960", "Années 1960", R.string.decades, 20, ExplorationState.Explored),
    )
    override val genres = listOf(
        TerritoryUi("DRAME", "Drame", R.string.genres, 50, ExplorationState.InProgress),
    )
    override val badges = listOf(
        BadgeUi("001", "Premier Rideau", "Voir son premier film", true, 1, showcaseSlot = 0),
        BadgeUi("005", "Passeport Cinéma", "Explorer 15 pays", true, 2, showcaseSlot = 1),
        BadgeUi("018", "Fantômes du Muet", "Voir 10 films muets", false, 3),
        BadgeUi("027", "Le Temps suspendu", "Voir 10 films de plus de 3 heures", false, 5),
    )
    override val ranks = listOf(
        RankUi("RANK_01", 1, "Novice", "Tu commences à tracer ta carte du cinéma.", home.rankLongDescription, true),
        RankUi("RANK_02", 2, "Amateur", "Ta curiosité prend forme.", "Le cinéma devient un intérêt régulier.", false),
        RankUi("RANK_05", 5, "Explorateur", "Tu parcours des cinématographies variées.", "La curiosité devient structurée.", false),
        RankUi("RANK_10", 10, "Maître", "Tu as parcouru presque intégralement le catalogue.", "Le sommet de l'exploration Urbinema.", false),
    )
    override val directors = listOf(
        DirectorUi("AKIRA_KUROSAWA", "Akira Kurosawa", listOf(previewFilms[2])),
        DirectorUi("ROBERTO_ROSSELLINI", "Roberto Rossellini", listOf(previewFilms[0])),
        DirectorUi("AGNES_VARDA", "Agnès Varda", listOf(previewFilms[1])),
    )
    override val movie = MovieUi(
        "SEPT_SAMOURAIS_1954",
        "七人の侍",
        "Les Sept Samouraïs",
        "Akira Kurosawa · 1954",
        "Japon · 3h27 · Drame",
        "Dans le Japon du XVIe siècle, des villageois engagent sept samouraïs pour protéger leurs récoltes.",
        false,
        countries = listOf(TerritoryUi("JAPAN", "Japon", R.string.countries, 0, ExplorationState.Unexplored)),
        genres = listOf(TerritoryUi("DRAME", "Drame", R.string.genres, 0, ExplorationState.Unexplored)),
        directorIds = listOf("AKIRA_KUROSAWA"),
    )
    override val profile = ProfileUiState(
        rankLongDescription = home.rankLongDescription,
        avatarCode = "AVATAR_01",
    )
    override val statsLists = StatsListsUi()
    override val themeMode = UrbinemaThemeMode.Dark
    override val language = AppLanguage.System
    override val filmGrain = false
    override val needsOnboarding = false
    override val completedCollectionCelebration: String? = null
    override val unlockedBadgeCelebration: String? = null
    override val followLimitReached: Boolean = false
    override val showAppGuide: Boolean = false
    override val rankUpCelebration: String? = null
    override val availableAvatars = MediaPaths.PACKAGED_AVATAR_CODES
    override fun setThemeMode(mode: UrbinemaThemeMode) = Unit
    override fun setLanguage(language: AppLanguage) = Unit
    override fun setFilmGrain(enabled: Boolean) = Unit
    override fun setUsername(username: String) = Unit
    override fun setAge(age: Int) = Unit
    override fun setAvatar(code: String) = Unit
    override fun completeOnboarding(username: String, age: Int, avatarCode: String) = Unit
    override fun markCurrentMovieWatched() = Unit
    override fun markMovieWatched(code: String) = Unit
    override fun followCollection(code: String) = Unit
    override fun unfollowCollection(code: String) = Unit
    override fun setShowcaseBadges(codes: List<String>) = Unit
    override fun openMovie(code: String) = Unit
    override fun movie(code: String): MovieUi? = movie.takeIf { it.id == code }
    override fun director(code: String): DirectorUi? = directors.firstOrNull { it.id == code }
    override fun search(query: String): List<SearchHitUi> {
        val needle = query.trim()
        if (needle.isEmpty()) return emptyList()
        fun match(value: String) = value.contains(needle, ignoreCase = true)
        return listOf(
            SearchHitUi(movie.id, SearchKind.Movie, movie.localizedTitle ?: movie.originalTitle, "1954"),
        ).filter {
            match(it.title) || match(movie.originalTitle) || match(movie.localizedTitle.orEmpty())
        }
    }
    override fun collectionsForCountry(code: String) = collections.filter { code in it.countryCodes }
    override fun collectionsForCurrent(code: String) = collections.filter { code in it.characteristicCodes }
    override fun moviesForCountry(code: String) = previewFilms
    override fun moviesForCurrent(code: String) = previewFilms
    override fun moviesForDecade(code: String) = previewFilms.filter { (it.year / 10 * 10).toString() == code }
    override fun moviesForGenre(code: String) = previewFilms
    override fun cinemaMap(layer: MapLayer, focusMovieCode: String): CinemaMapGraph {
        val seeds = when (layer) {
            MapLayer.AROUND_FILM -> {
                val code = focusMovieCode.ifBlank { previewFilms.first().id }
                return CinemaMapLayout.buildAround(
                    code,
                    listOf(
                        ConstellationSeed(code, MapNodeKind.FILM, 0),
                        ConstellationSeed("JAPAN", MapNodeKind.COUNTRY, 1),
                        ConstellationSeed("AKIRA_KUROSAWA", MapNodeKind.DIRECTOR, 1),
                        ConstellationSeed(previewFilms[0].id, MapNodeKind.FILM, 2, 3, listOf("JAPAN")),
                    ),
                )
            }
            MapLayer.COUNTRIES -> territories.map { MapSeed(it.id, if (it.id == "JAPAN") "ASIA" else "EUROPE") }
            MapLayer.CURRENTS -> currents.map { MapSeed(it.id) }
            MapLayer.DECADES -> decades.map { MapSeed(it.id) }
            MapLayer.GENRES -> genres.map { MapSeed(it.id) }
            MapLayer.DIRECTORS -> directors.map { MapSeed(it.id) }
            MapLayer.COLLECTIONS -> collections.map { MapSeed(it.id) }
        }
        return CinemaMapLayout.build(layer, seeds)
    }
    override fun defaultSkyMovieCode(): String = previewFilms.first().id
    override fun mapNodeUi(id: String, kind: MapNodeKind): TerritoryUi? = when (kind) {
        MapNodeKind.FILM -> previewFilms.firstOrNull { it.id == id }?.let {
            TerritoryUi(it.id, it.title, R.string.films, if (it.watched) 100 else 0, if (it.watched) ExplorationState.Mastered else ExplorationState.Unexplored)
        }
        MapNodeKind.COUNTRY -> territories.firstOrNull { it.id == id }
        MapNodeKind.CURRENT -> currents.firstOrNull { it.id == id }
        MapNodeKind.DECADE -> decades.firstOrNull { it.id == id }
        MapNodeKind.GENRE -> genres.firstOrNull { it.id == id }
        MapNodeKind.DIRECTOR -> directors.firstOrNull { it.id == id }?.let {
            TerritoryUi(it.id, it.name, R.string.directors, 0, ExplorationState.Unexplored)
        }
        MapNodeKind.COLLECTION -> collections.firstOrNull { it.id == id }?.let {
            TerritoryUi(it.id, it.name, R.string.all_collections, it.progress, ExplorationState.Unexplored)
        }
        MapNodeKind.TERRITORY -> territories.firstOrNull { it.id == id }
            ?: currents.firstOrNull { it.id == id }
            ?: decades.firstOrNull { it.id == id }
            ?: genres.firstOrNull { it.id == id }
    }
    override fun resetProgress() = Unit
    override fun retryBootstrap() = Unit
    override fun dismissCollectionCelebration() = Unit
    override fun dismissBadgeCelebration() = Unit
    override fun dismissFollowLimit() = Unit
    override fun replayAppGuide() = Unit
    override fun dismissAppGuide() = Unit
    override fun dismissRankUp() = Unit
}
