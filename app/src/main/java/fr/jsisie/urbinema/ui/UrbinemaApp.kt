package fr.jsisie.urbinema.ui

import android.content.Context
import android.content.res.Configuration
import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.HelpOutline
import androidx.compose.material.icons.automirrored.outlined.MenuBook
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Badge
import androidx.compose.material.icons.outlined.CollectionsBookmark
import androidx.compose.material.icons.outlined.EmojiEvents
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Insights
import androidx.compose.material.icons.outlined.Map
import androidx.compose.material.icons.outlined.Menu
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Route
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.ImageShader
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.ShaderBrush
import androidx.compose.ui.graphics.TileMode
import kotlin.math.abs
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.sp
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.domain.collection.CollectionFollowRules
import fr.jsisie.urbinema.domain.map.CinemaMapGraph
import fr.jsisie.urbinema.domain.map.MapLayer
import fr.jsisie.urbinema.domain.map.MapNodeKind
import fr.jsisie.urbinema.ui.map.InteractiveMapScreen
import fr.jsisie.urbinema.ui.map.SkyMapExpandingSearch
import fr.jsisie.urbinema.ui.map.SkyMapSearchHits
import fr.jsisie.urbinema.ui.model.HelpTopic
import fr.jsisie.urbinema.ui.model.AppLanguage
import fr.jsisie.urbinema.ui.model.AtlasFilter
import fr.jsisie.urbinema.ui.model.ExplorationState
import fr.jsisie.urbinema.ui.model.PreviewUrbinemaViewModel
import fr.jsisie.urbinema.ui.model.SearchKind
import fr.jsisie.urbinema.ui.model.StatsCategory
import fr.jsisie.urbinema.ui.model.TerritoryUi
import fr.jsisie.urbinema.ui.model.UrbinemaViewModel
import fr.jsisie.urbinema.ui.screens.AppGuideDialog
import fr.jsisie.urbinema.ui.screens.AtlasScreen
import fr.jsisie.urbinema.ui.screens.BadgesScreen
import fr.jsisie.urbinema.ui.screens.BadgeUnlockedDialog
import fr.jsisie.urbinema.ui.screens.CollectionScreen
import fr.jsisie.urbinema.ui.screens.CollectionsScreen
import fr.jsisie.urbinema.ui.screens.DirectorScreen
import fr.jsisie.urbinema.ui.screens.HelpScreen
import fr.jsisie.urbinema.ui.screens.HistoryScreen
import fr.jsisie.urbinema.ui.screens.HomeScreen
import fr.jsisie.urbinema.ui.screens.LogoAboutDialog
import fr.jsisie.urbinema.ui.screens.collectionLockMessage
import fr.jsisie.urbinema.ui.model.CollectionUi
import fr.jsisie.urbinema.ui.screens.MovieScreen
import fr.jsisie.urbinema.ui.screens.NamedListScreen
import fr.jsisie.urbinema.ui.screens.OnboardingDialog
import fr.jsisie.urbinema.ui.screens.PathDetailScreen
import fr.jsisie.urbinema.ui.screens.PathsScreen
import fr.jsisie.urbinema.ui.screens.ProfileScreen
import fr.jsisie.urbinema.ui.screens.RankUpDialog
import fr.jsisie.urbinema.ui.screens.RanksScreen
import fr.jsisie.urbinema.ui.screens.SearchScreen
import fr.jsisie.urbinema.ui.screens.SettingsScreen
import fr.jsisie.urbinema.ui.screens.SourcesScreen
import fr.jsisie.urbinema.ui.screens.StatsScreen
import fr.jsisie.urbinema.ui.screens.TerritoryScreen
import fr.jsisie.urbinema.ui.theme.UrbinemaTheme
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeMode
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeTokens
import java.util.Locale
import kotlin.math.abs
import kotlinx.coroutines.launch

private object Routes {
    const val Home = "home"
    const val Collections = "collections"
    const val Atlas = "atlas"
    const val SkyMap = "atlas/sky"
    const val Progress = "progress"
    const val Profile = "profile"
    const val Settings = "settings"
    const val Movie = "movie/{movieCode}"
    const val Collection = "collection/{collectionCode}"
    const val Badges = "badges"
    const val Search = "search"
    const val Ranks = "ranks"
    const val Stats = "stats"
    const val StatsDetail = "stats/{category}"
    const val Director = "director/{directorCode}"
    const val Territory = "territory/{kind}/{code}"
    const val Help = "help/{topic}"
    const val Sources = "sources"
    const val History = "history"
    const val Path = "path/{pathCode}"
}

private data class Destination(val route: String, @StringRes val label: Int, val icon: ImageVector)

private val tabs = listOf(
    Destination(Routes.Home, R.string.home, Icons.Outlined.Home),
    Destination(Routes.Atlas, R.string.atlas, Icons.Outlined.Map),
    Destination(Routes.Collections, R.string.collections_tab, Icons.AutoMirrored.Outlined.MenuBook),
    Destination(Routes.Progress, R.string.progress, Icons.Outlined.Route),
    Destination(Routes.Profile, R.string.profile, Icons.Outlined.Person),
)

/** Root Compose entry point, injectable with any domain-backed UI model. */
@Composable
fun UrbinemaApp(model: UrbinemaViewModel = PreviewUrbinemaViewModel) {
    LocalizedContent(model.language) {
        UrbinemaTheme(model.themeMode) {
            Box(
                Modifier
                    .fillMaxSize()
                    .then(
                        if (model.filmGrain) {
                            Modifier.filmGrain(dark = UrbinemaThemeTokens.colors.isDark)
                        } else {
                            Modifier
                        },
                    ),
            ) {
                UrbinemaNavigation(model, model.themeMode, model::setThemeMode)
                if (model.needsOnboarding) {
                    OnboardingDialog(
                        avatars = model.availableAvatars,
                        onConfirm = model::completeOnboarding,
                    )
                } else if (model.showAppGuide) {
                    AppGuideDialog(onFinished = model::dismissAppGuide)
                }
                model.rankUpCelebration?.let { name ->
                    RankUpDialog(rankName = name, onDismiss = model::dismissRankUp)
                }
                model.completedCollectionCelebration?.let { name ->
                    val resources = LocalContext.current.resources
                    val title = resources.getString(R.string.collection_completed_title)
                    val body = resources.getString(R.string.collection_completed_body, name)
                    val confirm = resources.getString(R.string.confirm)
                    AlertDialog(
                        onDismissRequest = model::dismissCollectionCelebration,
                        title = { Text(title) },
                        text = { Text(body) },
                        confirmButton = {
                            TextButton(onClick = model::dismissCollectionCelebration) {
                                Text(confirm)
                            }
                        },
                    )
                } ?: model.unlockedBadgeCelebration?.let { badge ->
                    BadgeUnlockedDialog(
                        badge = badge,
                        onDismiss = model::dismissBadgeCelebration,
                    )
                }
                if (model.followLimitReached) {
                    val cap = CollectionFollowRules.MAX_IN_PROGRESS_COLLECTIONS
                    AlertDialog(
                        onDismissRequest = model::dismissFollowLimit,
                        title = { Text(stringResource(R.string.follow_limit_title)) },
                        text = { Text(stringResource(R.string.follow_limit_body, cap)) },
                        confirmButton = {
                            TextButton(onClick = model::dismissFollowLimit) {
                                Text(stringResource(R.string.confirm))
                            }
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun LocalizedContent(language: AppLanguage, content: @Composable () -> Unit) {
    val context = LocalContext.current
    val localized = remember(language, context) {
        when (language) {
            AppLanguage.System -> context
            AppLanguage.French -> context.withLocale(Locale.FRENCH)
            AppLanguage.English -> context.withLocale(Locale.ENGLISH)
        }
    }
    CompositionLocalProvider(
        LocalContext provides localized,
        LocalConfiguration provides localized.resources.configuration,
    ) { content() }
}

private fun Context.withLocale(locale: Locale): Context {
    val config = Configuration(resources.configuration)
    config.setLocale(locale)
    config.setLocales(android.os.LocaleList(locale))
    return createConfigurationContext(config)
}

@Composable
private fun Modifier.filmGrain(dark: Boolean): Modifier {
    val tile = remember(dark) {
        grainTile(
            dark = dark,
            wash = if (dark) 0.033f else 0.032f,
            lightSpeck = if (dark) 0.076f else 0.07f,
            darkSpeck = if (dark) 0.092f else 0.09f,
        )
    }
    val brush = remember(tile) {
        ShaderBrush(ImageShader(tile, TileMode.Repeated, TileMode.Repeated))
    }
    return drawBehind { drawRect(brush) }
}

private fun grainTile(
    dark: Boolean,
    wash: Float,
    lightSpeck: Float,
    darkSpeck: Float,
): ImageBitmap {
    val size = 128
    val image = ImageBitmap(size, size)
    val canvas = Canvas(image)
    val washPaint = Paint().apply { color = Color.Black.copy(alpha = wash) }
    val lightPaint = Paint().apply { color = Color.White.copy(alpha = lightSpeck) }
    val darkPaint = Paint().apply { color = Color.Black.copy(alpha = darkSpeck) }
    canvas.drawRect(0f, 0f, size.toFloat(), size.toFloat(), washPaint)
    val step = 5f
    val lightR = if (dark) 1.4f else 1.3f
    val darkR = 1.5f
    var x = 0f
    while (x < size) {
        var y = 0f
        while (y < size) {
            val hash = abs((x * 127.1f + y * 311.7f).toInt())
            when (hash % 8) {
                0 -> canvas.drawCircle(Offset(x, y), lightR, lightPaint)
                1 -> canvas.drawCircle(Offset(x, y), darkR, darkPaint)
            }
            y += step
        }
        x += step
    }
    return image
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun UrbinemaNavigation(
    model: UrbinemaViewModel,
    themeMode: UrbinemaThemeMode,
    onThemeModeChange: (UrbinemaThemeMode) -> Unit,
) {
    val navController = rememberNavController()
    val openFilm = { code: String ->
        model.openMovie(code)
        navController.navigate(movieRoute(code))
    }
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val entry by navController.currentBackStackEntryAsState()
    val route = entry?.destination?.route ?: Routes.Home
    var activeTab by remember { mutableStateOf(Routes.Home) }
    var tabResetRoute by remember { mutableStateOf<String?>(null) }
    var tabResetTick by remember { mutableStateOf(0) }
    var atlasFilter by remember { mutableStateOf(AtlasFilter.Countries) }
    var mapLayer by rememberSaveable { mutableStateOf(MapLayer.AROUND_FILM) }
    var mapFocus by rememberSaveable { mutableStateOf("") }
    var skyQuery by remember { mutableStateOf("") }
    var skySearchOpen by remember { mutableStateOf(false) }
    var showLogoAbout by remember { mutableStateOf(false) }
    fun closeSkySearch() {
        skyQuery = ""
        skySearchOpen = false
    }
    LaunchedEffect(route) {
        if (route != Routes.SkyMap) closeSkySearch()
        if (route != Routes.Home) showLogoAbout = false
    }
    var showCollectionLock by remember { mutableStateOf<CollectionUi?>(null) }
    val isHome = route == Routes.Home
    val isProfile = route == Routes.Profile
    val isTab = tabs.any { it.route == route }
    val highlightedTab = when {
        isTab -> route
        route == Routes.Settings || route == Routes.Sources -> Routes.Profile
        route == Routes.SkyMap -> Routes.Atlas
        else -> activeTab
    }
    val pageHelpTopic = when (route) {
        Routes.Collections -> HelpTopic.Collections
        Routes.Atlas -> HelpTopic.Atlas
        Routes.SkyMap -> HelpTopic.InteractiveMap
        Routes.Progress -> HelpTopic.Progress
        else -> null
    }
    fun openCollection(code: String) {
        val collection = model.collections.firstOrNull { it.id == code }
        if (collection?.locked == true) {
            showCollectionLock = collection
        } else {
            navController.navigate(collectionRoute(code))
        }
    }
    showLogoAbout.takeIf { it }?.let {
        LogoAboutDialog(onDismiss = { showLogoAbout = false })
    }
    showCollectionLock?.let { locked ->
        val lockTitle = stringResource(R.string.collection_locked_title)
        val lockBody = collectionLockMessage(locked)
        val confirmLabel = stringResource(R.string.confirm)
        AlertDialog(
            onDismissRequest = { showCollectionLock = null },
            title = { Text(lockTitle) },
            text = { Text(lockBody) },
            confirmButton = {
                TextButton(onClick = { showCollectionLock = null }) {
                    Text(confirmLabel)
                }
            },
        )
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = isTab,
        drawerContent = {
            DrawerContent(
                onNavigate = { destination ->
                    scope.launch { drawerState.close() }
                    if (tabs.any { it.route == destination }) {
                        val reselected = highlightedTab == destination
                        selectTab(navController, destination, highlightedTab)
                        activeTab = destination
                        if (reselected) {
                            tabResetRoute = destination
                            tabResetTick++
                        }
                    } else {
                        navController.navigate(destination)
                    }
                },
            )
        },
    ) {
        Scaffold(
            containerColor = UrbinemaThemeTokens.colors.background,
            topBar = {
                TopAppBar(
                    title = {
                        when {
                            route == Routes.SkyMap -> Text(
                                stringResource(R.string.sky_map),
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                            route == Routes.History -> Text(
                                stringResource(R.string.history),
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                        }
                    },
                    navigationIcon = {
                        if (isTab) IconButton(onClick = { scope.launch { drawerState.open() } }) {
                            Icon(Icons.Outlined.Menu, stringResource(R.string.open_menu))
                        } else IconButton(onClick = { navController.popBackStack() }) {
                            Icon(Icons.AutoMirrored.Outlined.ArrowBack, stringResource(R.string.back))
                        }
                    },
                    actions = {
                        if (isHome) {
                            Image(
                                painter = painterResource(R.drawable.logo_urbinema),
                                contentDescription = stringResource(R.string.app_name),
                                modifier = Modifier
                                    .height(40.dp)
                                    .padding(end = UrbinemaThemeTokens.dimens.screen - 4.dp)
                                    .clickable { showLogoAbout = true },
                                contentScale = ContentScale.Fit,
                            )
                        }
                        if (route == Routes.Atlas) {
                            IconButton(onClick = { navController.navigate(helpRoute(HelpTopic.Atlas)) }) {
                                Icon(Icons.AutoMirrored.Outlined.HelpOutline, stringResource(R.string.help))
                            }
                            IconButton(onClick = { navController.navigate(Routes.SkyMap) }) {
                                Icon(Icons.Outlined.AutoAwesome, stringResource(R.string.sky_map_open))
                            }
                        } else if (route == Routes.SkyMap) {
                            SkyMapExpandingSearch(
                                expanded = skySearchOpen,
                                query = skyQuery,
                                onQueryChange = { skyQuery = it },
                                onExpand = { skySearchOpen = true },
                                onDismiss = { closeSkySearch() },
                            )
                            Spacer(Modifier.width(8.dp))
                            IconButton(onClick = { navController.navigate(helpRoute(HelpTopic.InteractiveMap)) }) {
                                Icon(Icons.AutoMirrored.Outlined.HelpOutline, stringResource(R.string.help))
                            }
                        } else if (pageHelpTopic != null) {
                            IconButton(onClick = { navController.navigate(helpRoute(pageHelpTopic)) }) {
                                Icon(Icons.AutoMirrored.Outlined.HelpOutline, stringResource(R.string.help))
                            }
                        }
                        if (isProfile) IconButton(onClick = { navController.navigate(Routes.Settings) }) {
                            Icon(Icons.Outlined.Settings, stringResource(R.string.settings))
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = UrbinemaThemeTokens.colors.background,
                        titleContentColor = UrbinemaThemeTokens.colors.onBackground,
                    ),
                )
            },
            bottomBar = {
                BottomBar(highlightedTab) { selected ->
                    val reselected = highlightedTab == selected
                    selectTab(navController, selected, highlightedTab)
                    activeTab = selected
                    if (reselected) {
                        tabResetRoute = selected
                        tabResetTick++
                    }
                }
            },
        ) { padding ->
            Box(Modifier.padding(padding).fillMaxSize()) {
            NavHost(navController, Routes.Home, Modifier.fillMaxSize()) {
                composable(Routes.Home) {
                    HomeScreen(
                        state = model.home,
                        resetTick = if (tabResetRoute == Routes.Home) tabResetTick else 0,
                        onRetry = model::retryBootstrap,
                        onOpenProfile = {
                            activeTab = Routes.Profile
                            selectTab(navController, Routes.Profile, Routes.Home)
                        },
                        onCollection = ::openCollection,
                        onSeeAllHistory = { navController.navigate(Routes.History) },
                    )
                }
                composable(Routes.History) {
                    HistoryScreen(model.home.history)
                }
                composable(Routes.Atlas) {
                    val directorTerritories = remember(model.directors) {
                        model.directors.map { director ->
                            val seen = director.films.count { it.watched }
                            val total = director.films.size
                            val percent = if (total == 0) 0 else seen * 100 / total
                            TerritoryUi(
                                director.id,
                                director.name,
                                R.string.directors,
                                percent,
                                explorationFrom(percent),
                                filmCount = total,
                            )
                        }
                    }
                    AtlasScreen(
                        countries = model.territories,
                        currents = model.currents,
                        decades = model.decades,
                        genres = model.genres,
                        directors = directorTerritories,
                        selectedFilter = atlasFilter,
                        onFilterChange = { atlasFilter = it },
                        resetTick = if (tabResetRoute == Routes.Atlas) tabResetTick else 0,
                    ) { filter, code ->
                        when (filter) {
                            AtlasFilter.Countries -> navController.navigate(territoryRoute("country", code))
                            AtlasFilter.Currents -> navController.navigate(territoryRoute("current", code))
                            AtlasFilter.Decades -> navController.navigate(territoryRoute("decade", code))
                            AtlasFilter.Genres -> navController.navigate(territoryRoute("genre", code))
                            AtlasFilter.Directors -> navController.navigate(directorRoute(code))
                        }
                    }
                }
                composable(Routes.SkyMap) {
                    val focus = mapFocus.ifBlank { model.defaultSkyMovieCode() }
                    val graph = remember(
                        mapLayer,
                        focus,
                        model.territories,
                        model.currents,
                        model.decades,
                        model.genres,
                        model.directors,
                        model.collections,
                        model.home.history,
                    ) { model.cinemaMap(mapLayer, focus) }
                    InteractiveMapScreen(
                        graph = graph,
                        territories = skyTerritories(model, mapLayer, graph),
                        layer = mapLayer,
                        onLayerChange = { mapLayer = it },
                        filmsOf = { code -> skyFilms(model, mapLayer, code, graph) },
                        onMovie = openFilm,
                        onMarkWatched = model::markMovieWatched,
                        onCenterFilm = {
                            mapFocus = it
                            mapLayer = MapLayer.AROUND_FILM
                        },
                        onOpenNode = { kind, code ->
                            if (kind == MapNodeKind.FILM) model.openMovie(code)
                            openMapNode(navController, kind, code, ::openCollection)
                        },
                    )
                }
                composable(Routes.Collections) {
                    CollectionsScreen(
                        collections = model.collections,
                        onCollection = ::openCollection,
                        resetTick = if (tabResetRoute == Routes.Collections) tabResetTick else 0,
                    )
                }
                composable(Routes.Progress) {
                    // Ancien onglet Parcours : rang, quêtes de la semaine, collections en cours.
                    // ProgressScreen est conservé pour le remettre plus tard (Accueil ou Profil).
                    // ProgressScreen(model.home, model.ranks)
                    PathsScreen(
                        paths = model.paths,
                        resetTick = if (tabResetRoute == Routes.Progress) tabResetTick else 0,
                    ) { code -> navController.navigate(pathRoute(code)) }
                }
                composable(
                    Routes.Path,
                    arguments = listOf(navArgument("pathCode") { type = NavType.StringType }),
                ) { pathEntry ->
                    val code = pathEntry.arguments?.getString("pathCode").orEmpty()
                    val path = model.paths.firstOrNull { it.id == code }
                    if (path != null) {
                        PathDetailScreen(
                            path = path,
                            onMovie = openFilm,
                            onDirector = { navController.navigate(directorRoute(it)) },
                        )
                    }
                }
                composable(Routes.Profile) {
                    ProfileScreen(
                        state = model.profile,
                        badges = model.badges,
                        onBadges = { navController.navigate(Routes.Badges) },
                        onRank = { navController.navigate(Routes.Ranks) },
                        resetTick = if (tabResetRoute == Routes.Profile) tabResetTick else 0,
                    )
                }
                composable(Routes.Settings) {
                    SettingsScreen(
                        themeMode = themeMode,
                        onThemeModeChange = onThemeModeChange,
                        language = model.language,
                        onLanguageChange = model::setLanguage,
                        filmGrain = model.filmGrain,
                        onFilmGrainChange = model::setFilmGrain,
                        username = model.profile.nickname,
                        onUsernameChange = model::setUsername,
                        ageYears = model.profile.ageYears,
                        onAgeChange = model::setAge,
                        avatarCode = model.profile.avatarCode,
                        availableAvatars = model.availableAvatars,
                        onAvatarChange = model::setAvatar,
                        onHelp = { navController.navigate(helpRoute(HelpTopic.All)) },
                        onReplayGuide = model::replayAppGuide,
                        onSources = { navController.navigate(Routes.Sources) },
                        onResetProgress = model::resetProgress,
                        showDevTools = model.devToolsAvailable,
                        devMode = model.devMode,
                        onDevModeChange = model::setDevMode,
                    )
                }
                composable(
                    Routes.Movie,
                    arguments = listOf(navArgument("movieCode") { type = NavType.StringType }),
                ) { movieEntry ->
                    val code = movieEntry.arguments?.getString("movieCode").orEmpty()
                    LaunchedEffect(code) { if (code.isNotBlank()) model.openMovie(code) }
                    val movie = model.movie
                    MovieScreen(
                        movie,
                        model::markCurrentMovieWatched,
                        { countryCode -> navController.navigate(territoryRoute("country", countryCode)) },
                        { directorCode -> navController.navigate(directorRoute(directorCode)) },
                        { genreCode -> navController.navigate(territoryRoute("genre", genreCode)) },
                        onShowOnMap = {
                            mapFocus = movie.id
                            mapLayer = MapLayer.AROUND_FILM
                            activeTab = Routes.Atlas
                            navController.navigate(Routes.SkyMap)
                        },
                    )
                }
                composable(
                    Routes.Collection,
                    arguments = listOf(navArgument("collectionCode") { type = NavType.StringType }),
                ) { collectionEntry ->
                    val code = collectionEntry.arguments?.getString("collectionCode")
                    val collection = model.collections.firstOrNull { it.id == code }
                    if (collection != null) {
                        CollectionScreen(
                            collection = collection,
                            onMovie = openFilm,
                            onFollow = { model.followCollection(collection.id) },
                            onUnfollow = { model.unfollowCollection(collection.id) },
                            onMarkWatched = model::markMovieWatched,
                        )
                    }
                }
                composable(Routes.Badges) {
                    BadgesScreen(model.badges, model::setShowcaseBadges)
                }
                composable(Routes.Search) {
                    SearchScreen(model::search, onMarkWatched = model::markMovieWatched) { hit ->
                        when (hit.kind) {
                            SearchKind.Movie -> openFilm(hit.id)
                            SearchKind.Country -> navController.navigate(territoryRoute("country", hit.id))
                            SearchKind.Current -> navController.navigate(territoryRoute("current", hit.id))
                            SearchKind.Collection -> openCollection(hit.id)
                            SearchKind.Director -> navController.navigate(directorRoute(hit.id))
                            SearchKind.Genre -> navController.navigate(territoryRoute("genre", hit.id))
                        }
                    }
                }
                composable(Routes.Ranks) { RanksScreen(model.ranks) }
                composable(Routes.Stats) {
                    StatsScreen(model.profile, model.statsLists) { category ->
                        navController.navigate("stats/${category.name}")
                    }
                }
                composable(
                    Routes.StatsDetail,
                    arguments = listOf(navArgument("category") { type = NavType.StringType }),
                ) { statsEntry ->
                    val category = statsEntry.arguments?.getString("category")
                        ?.let { runCatching { StatsCategory.valueOf(it) }.getOrNull() }
                        ?: StatsCategory.Films
                    val title = when (category) {
                        StatsCategory.Films -> R.string.films_seen
                        StatsCategory.Countries -> R.string.countries
                        StatsCategory.Decades -> R.string.decades
                        StatsCategory.Currents -> R.string.currents
                        StatsCategory.Continents -> R.string.continents
                        StatsCategory.Directors -> R.string.directors
                    }
                    NamedListScreen(
                        title,
                        category,
                        remember(category, model.profile.films) { model.statsShares(category) },
                    )
                }
                composable(
                    Routes.Director,
                    arguments = listOf(navArgument("directorCode") { type = NavType.StringType }),
                ) { directorEntry ->
                    val code = directorEntry.arguments?.getString("directorCode").orEmpty()
                    val director = model.director(code)
                    if (director != null) {
                        DirectorScreen(
                            director = director,
                            onMovie = openFilm,
                            onCollection = ::openCollection,
                            onMarkWatched = model::markMovieWatched,
                        )
                    }
                }
                composable(
                    Routes.Territory,
                    arguments = listOf(
                        navArgument("kind") { type = NavType.StringType },
                        navArgument("code") { type = NavType.StringType },
                    ),
                ) { territoryEntry ->
                    val kind = territoryEntry.arguments?.getString("kind").orEmpty()
                    val code = territoryEntry.arguments?.getString("code").orEmpty()
                    val collections = when (kind) {
                        "country" -> model.collectionsForCountry(code)
                        "current" -> model.collectionsForCurrent(code)
                        else -> emptyList()
                    }
                    val films = when (kind) {
                        "country" -> model.moviesForCountry(code)
                        "current" -> model.moviesForCurrent(code)
                        "decade" -> model.moviesForDecade(code)
                        "genre" -> model.moviesForGenre(code)
                        else -> emptyList()
                    }
                    val title = when (kind) {
                        "country" -> model.territories.firstOrNull { it.id == code }?.name ?: code
                        "current" -> model.currents.firstOrNull { it.id == code }?.name ?: code
                        "decade" -> model.decades.firstOrNull { it.id == code }?.name ?: code
                        else -> model.genres.firstOrNull { it.id == code }?.name ?: code
                    }
                    TerritoryScreen(
                        title = title,
                        collections = collections,
                        films = films,
                        onCollection = ::openCollection,
                        onMovie = openFilm,
                        onMarkWatched = model::markMovieWatched,
                    )
                }
                composable(
                    Routes.Help,
                    arguments = listOf(navArgument("topic") { type = NavType.StringType }),
                ) { helpEntry ->
                    val topic = helpEntry.arguments?.getString("topic")
                        ?.let { runCatching { HelpTopic.valueOf(it) }.getOrNull() }
                        ?: HelpTopic.All
                    HelpScreen(topic)
                }
                composable(Routes.Sources) { SourcesScreen() }
            }
            if (route == Routes.SkyMap && skySearchOpen && skyQuery.isNotBlank()) {
                SkyMapSearchHits(
                    hits = model.searchMovies(skyQuery),
                    onPick = { code ->
                        mapFocus = code
                        mapLayer = MapLayer.AROUND_FILM
                        closeSkySearch()
                    },
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(end = 12.dp, top = 8.dp),
                )
            }
            }
        }
    }
}

@Composable
private fun BottomBar(currentRoute: String, onSelect: (String) -> Unit) {
    NavigationBar(containerColor = UrbinemaThemeTokens.colors.surfaceElevated) {
        tabs.forEachIndexed { index, destination ->
            val selected = currentRoute == destination.route
            NavigationBarItem(
                selected = selected,
                onClick = { onSelect(destination.route) },
                icon = {
                    Icon(
                        destination.icon,
                        stringResource(destination.label),
                        Modifier.size(if (index == 2) 32.dp else 24.dp),
                    )
                },
                label = {
                    Text(
                        stringResource(destination.label),
                        maxLines = 1,
                        softWrap = false,
                        overflow = TextOverflow.Clip,
                        style = MaterialTheme.typography.labelSmall,
                        fontSize = 11.sp,
                    )
                },
                alwaysShowLabel = true,
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = UrbinemaThemeTokens.colors.line,
                    selectedTextColor = UrbinemaThemeTokens.colors.accent,
                    unselectedIconColor = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    unselectedTextColor = UrbinemaThemeTokens.colors.onBackgroundMuted,
                    indicatorColor = UrbinemaThemeTokens.colors.surfacePressed,
                ),
            )
        }
    }
}

@Composable
private fun DrawerContent(onNavigate: (String) -> Unit) {
    val entries = listOf(
        Destination(Routes.Ranks, R.string.all_ranks, Icons.Outlined.EmojiEvents),
        Destination(Routes.Badges, R.string.all_badges, Icons.Outlined.Badge),
        Destination(Routes.Collections, R.string.all_collections, Icons.Outlined.CollectionsBookmark),
        Destination(Routes.Search, R.string.search, Icons.Outlined.Search),
        Destination(Routes.Stats, R.string.detailed_statistics, Icons.Outlined.Insights),
    )
    ModalDrawerSheet(
        modifier = Modifier.fillMaxWidth(0.58f),
        drawerContainerColor = UrbinemaThemeTokens.colors.surfaceElevated,
    ) {
        Image(
            painter = painterResource(R.drawable.logo_urbinema),
            contentDescription = stringResource(R.string.app_name),
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    start = UrbinemaThemeTokens.dimens.screen,
                    end = UrbinemaThemeTokens.dimens.screen,
                    top = UrbinemaThemeTokens.dimens.lg,
                    bottom = UrbinemaThemeTokens.dimens.md,
                )
                .height(96.dp),
            contentScale = ContentScale.Fit,
        )
        Text(
            stringResource(R.string.exploration_indexes),
            modifier = Modifier.padding(
                start = UrbinemaThemeTokens.dimens.screen,
                end = UrbinemaThemeTokens.dimens.screen,
                bottom = UrbinemaThemeTokens.dimens.xxs,
            ),
        )
        entries.forEach {
            NavigationDrawerItem(
                label = { Text(stringResource(it.label)) },
                selected = false,
                onClick = { onNavigate(it.route) },
                icon = { Icon(it.icon, contentDescription = null) },
            )
        }
    }
}

private fun openMapNode(
    navController: NavHostController,
    kind: MapNodeKind,
    code: String,
    openCollection: (String) -> Unit,
) {
    when (kind) {
        MapNodeKind.FILM -> navController.navigate(movieRoute(code))
        MapNodeKind.DIRECTOR -> navController.navigate(directorRoute(code))
        MapNodeKind.COUNTRY, MapNodeKind.TERRITORY -> navController.navigate(territoryRoute("country", code))
        MapNodeKind.CURRENT -> navController.navigate(territoryRoute("current", code))
        MapNodeKind.DECADE -> navController.navigate(territoryRoute("decade", code))
        MapNodeKind.GENRE -> navController.navigate(territoryRoute("genre", code))
        MapNodeKind.COLLECTION -> openCollection(code)
    }
}

private fun skyTerritories(
    model: UrbinemaViewModel,
    layer: MapLayer,
    graph: CinemaMapGraph,
): Map<String, TerritoryUi> {
    if (layer == MapLayer.AROUND_FILM) {
        return graph.nodes.mapNotNull { node ->
            model.mapNodeUi(node.id, node.kind)?.let { node.id to it }
        }.toMap()
    }
    return when (layer) {
    MapLayer.COUNTRIES -> model.territories
    MapLayer.CURRENTS -> model.currents
    MapLayer.DECADES -> model.decades
    MapLayer.GENRES -> model.genres
    MapLayer.DIRECTORS -> model.directors.map { director ->
        val seen = director.films.count { it.watched }
        val total = director.films.size
        val percent = if (total == 0) 0 else seen * 100 / total
        TerritoryUi(
            director.id,
            director.name,
            R.string.directors,
            percent,
            explorationFrom(percent),
            filmCount = total,
        )
    }
    MapLayer.COLLECTIONS -> model.collections.map { collection ->
        TerritoryUi(
            collection.id,
            collection.name,
            R.string.all_collections,
            collection.progress,
            explorationFrom(collection.progress),
            collection.shortDescription,
            filmCount = collection.films.size,
        )
    }
    MapLayer.AROUND_FILM -> emptyList()
}.associateBy { it.id }
}

private fun skyFilms(
    model: UrbinemaViewModel,
    layer: MapLayer,
    code: String,
    graph: CinemaMapGraph,
) = when (layer) {
    MapLayer.AROUND_FILM -> {
        val kind = graph.nodes.firstOrNull { it.id == code }?.kind
        when (kind) {
            MapNodeKind.COUNTRY -> model.moviesForCountry(code)
            MapNodeKind.CURRENT -> model.moviesForCurrent(code)
            MapNodeKind.DECADE -> model.moviesForDecade(code)
            MapNodeKind.GENRE -> model.moviesForGenre(code)
            MapNodeKind.DIRECTOR -> model.director(code)?.films.orEmpty()
            MapNodeKind.COLLECTION -> model.collections.firstOrNull { it.id == code }?.films.orEmpty()
            else -> emptyList()
        }
    }
    MapLayer.COUNTRIES -> model.moviesForCountry(code)
    MapLayer.CURRENTS -> model.moviesForCurrent(code)
    MapLayer.DECADES -> model.moviesForDecade(code)
    MapLayer.GENRES -> model.moviesForGenre(code)
    MapLayer.DIRECTORS -> model.director(code)?.films.orEmpty()
    MapLayer.COLLECTIONS -> model.collections.firstOrNull { it.id == code }?.films.orEmpty()
}

private fun explorationFrom(percent: Int): ExplorationState = when {
    percent == 0 -> ExplorationState.Unexplored
    percent >= 100 -> ExplorationState.Mastered
    percent >= 75 -> ExplorationState.Completed
    percent > 0 -> ExplorationState.Explored
    else -> ExplorationState.InProgress
}

private fun selectTab(
    navController: NavHostController,
    route: String,
    highlightedTab: String,
) {
    if (highlightedTab == route) {
        if (navController.currentDestination?.route != route) {
            if (!navController.popBackStack(route, inclusive = false)) {
    navController.navigate(route) {
                    launchSingleTop = true
                    restoreState = true
                    popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                }
            }
        }
        return
    }
    navController.navigate(route) {
        popUpTo(navController.graph.findStartDestination().id) { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}

private fun helpRoute(topic: HelpTopic): String = "help/${topic.name}"

private fun collectionRoute(code: String): String = "collection/$code"

private fun movieRoute(code: String): String = "movie/$code"

private fun directorRoute(code: String): String = "director/$code"

private fun pathRoute(code: String): String = "path/$code"

private fun territoryRoute(kind: String, code: String): String = "territory/$kind/$code"
