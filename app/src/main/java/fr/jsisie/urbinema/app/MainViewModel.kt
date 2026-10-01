package fr.jsisie.urbinema.app

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import fr.jsisie.urbinema.BuildConfig
import fr.jsisie.urbinema.R
import fr.jsisie.urbinema.app.startup.AppBootstrapper
import fr.jsisie.urbinema.data.db.ActivityEventEntity
import fr.jsisie.urbinema.data.db.BadgeEntity
import fr.jsisie.urbinema.data.db.CinemaCharacteristicEntity
import fr.jsisie.urbinema.data.db.CollectionCharacteristicCrossRef
import fr.jsisie.urbinema.data.db.CollectionCountryCrossRef
import fr.jsisie.urbinema.data.db.CollectionProgressRow
import fr.jsisie.urbinema.data.db.CollectionWithMovies
import fr.jsisie.urbinema.data.db.ContinentEntity
import fr.jsisie.urbinema.data.db.CountryContinentCrossRef
import fr.jsisie.urbinema.data.db.CountryEntity
import fr.jsisie.urbinema.data.db.CountryProgressRow
import fr.jsisie.urbinema.data.db.DirectorEntity
import fr.jsisie.urbinema.data.db.GenreEntity
import fr.jsisie.urbinema.data.db.LearningPathEntity
import fr.jsisie.urbinema.data.db.LearningPathFactEntity
import fr.jsisie.urbinema.data.db.LearningPathFigureEntity
import fr.jsisie.urbinema.data.db.LearningPathMovieCrossRef
import fr.jsisie.urbinema.data.db.LearningPathStepEntity
import fr.jsisie.urbinema.data.db.MovieDirectorBilling
import fr.jsisie.urbinema.data.db.MovieEntity
import fr.jsisie.urbinema.data.db.MovieWithRelations
import fr.jsisie.urbinema.data.db.QuestDifficulty
import fr.jsisie.urbinema.data.db.QuestEntity
import fr.jsisie.urbinema.data.db.RankingEntity
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.db.UserEntity
import fr.jsisie.urbinema.data.db.UserMovieCrossRef
import fr.jsisie.urbinema.data.db.UserProgressStateEntity
import fr.jsisie.urbinema.data.db.UserQuestStatus
import fr.jsisie.urbinema.data.preferences.LanguagePreference
import fr.jsisie.urbinema.data.preferences.PreferencesRepository
import fr.jsisie.urbinema.data.preferences.ThemePreference
import fr.jsisie.urbinema.data.repository.ProgressRepository
import fr.jsisie.urbinema.data.repository.ProgressionCoordinator
import fr.jsisie.urbinema.data.repository.WeeklyQuestCoordinator
import fr.jsisie.urbinema.data.media.MediaPaths
import fr.jsisie.urbinema.domain.FunctionalLimits
import fr.jsisie.urbinema.domain.badge.ProfileBadges
import fr.jsisie.urbinema.domain.collection.CollectionFollowRules
import fr.jsisie.urbinema.domain.collection.CollectionUnlockRules
import fr.jsisie.urbinema.domain.rank.RankDefaults
import fr.jsisie.urbinema.domain.map.CinemaMapGraph
import fr.jsisie.urbinema.domain.map.CinemaMapLayout
import fr.jsisie.urbinema.domain.map.ConstellationSeed
import fr.jsisie.urbinema.domain.map.MapLayer
import fr.jsisie.urbinema.domain.map.MapNodeKind
import fr.jsisie.urbinema.domain.map.MapSeed
import fr.jsisie.urbinema.domain.xp.XpEngine
import fr.jsisie.urbinema.ui.model.AppLanguage
import fr.jsisie.urbinema.ui.model.BadgeUi
import fr.jsisie.urbinema.ui.model.CollectionTrack
import fr.jsisie.urbinema.ui.model.CollectionUi
import fr.jsisie.urbinema.ui.model.PathFactUi
import fr.jsisie.urbinema.ui.model.PathFigureUi
import fr.jsisie.urbinema.ui.model.PathStepUi
import fr.jsisie.urbinema.ui.model.PathUi
import fr.jsisie.urbinema.ui.model.DevProgressUi
import fr.jsisie.urbinema.ui.model.DirectorUi
import fr.jsisie.urbinema.ui.model.ExplorationState
import fr.jsisie.urbinema.ui.model.FilmListSort
import fr.jsisie.urbinema.ui.model.HistoryUi
import fr.jsisie.urbinema.ui.model.HomeUiState
import fr.jsisie.urbinema.ui.model.listDirectorLabel
import fr.jsisie.urbinema.ui.model.LoadState
import fr.jsisie.urbinema.ui.model.DirectorCreditUi
import fr.jsisie.urbinema.ui.model.MovieSummaryUi
import fr.jsisie.urbinema.ui.model.sortedFilms
import fr.jsisie.urbinema.ui.model.MovieUi
import fr.jsisie.urbinema.ui.model.ProfileUiState
import fr.jsisie.urbinema.ui.model.QuestUi
import fr.jsisie.urbinema.ui.model.RankUi
import fr.jsisie.urbinema.ui.model.SearchHitUi
import fr.jsisie.urbinema.ui.model.SearchKind
import fr.jsisie.urbinema.ui.model.StatShareUi
import fr.jsisie.urbinema.ui.model.StatsCategory
import fr.jsisie.urbinema.ui.model.StatsListsUi
import fr.jsisie.urbinema.ui.model.TerritoryUi
import fr.jsisie.urbinema.ui.model.UrbinemaViewModel
import fr.jsisie.urbinema.ui.theme.UrbinemaThemeMode
import java.time.Instant
import java.time.LocalDate
import java.time.Year
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlin.math.roundToInt

/**
 * Application-level presentation model backed by Room flows.
 *
 * It deliberately maps database entities to UI models here, leaving both
 * Composables and the pure domain engines independent of persistence classes.
 */
class MainViewModel(
    private val bootstrapper: AppBootstrapper,
    private val database: UrbinemaDatabase,
    private val progressRepository: ProgressRepository,
    private val xpEngine: XpEngine,
    private val preferencesRepository: PreferencesRepository,
    private val progressionCoordinator: ProgressionCoordinator,
    private val weeklyQuestCoordinator: WeeklyQuestCoordinator,
) : ViewModel(), UrbinemaViewModel {
    private var user: UserEntity? = null
    private var moviesWithRelations: List<MovieWithRelations> = emptyList()
    private var moviesByMovieId: Map<Long, MovieWithRelations> = emptyMap()
    private var orderedDirectorsByMovieId: Map<Long, List<DirectorEntity>> = emptyMap()
    private var filmsByDirectorId: Map<Long, List<MovieWithRelations>> = emptyMap()
    private var watched: List<UserMovieCrossRef> = emptyList()
    private var optimisticWatchedIds by mutableStateOf(emptySet<Long>())
    private var collectionsWithMovies: List<CollectionWithMovies> = emptyList()
    private var collectionProgress: Map<Long, CollectionProgressRow> = emptyMap()
    private var collectionCountryRefs: List<CollectionCountryCrossRef> = emptyList()
    private var collectionCharacteristicRefs: List<CollectionCharacteristicCrossRef> = emptyList()
    private var followedCollectionIds: Set<Long> = emptySet()
    private var countryEntities: List<CountryEntity> = emptyList()
    private var countryProgress: Map<Long, CountryProgressRow> = emptyMap()
    private var countryContinents: List<CountryContinentCrossRef> = emptyList()
    private var continentEntities: List<ContinentEntity> = emptyList()
    private var directorEntities: List<DirectorEntity> = emptyList()
    private var genreEntities: List<GenreEntity> = emptyList()
    private var characteristicEntities: List<CinemaCharacteristicEntity> = emptyList()
    private var badgeEntities: List<BadgeEntity> = emptyList()
    private var earnedBadgeCodesOrdered: List<String> = emptyList()
    private var rankings: List<RankingEntity> = emptyList()
    private var questEntities: List<QuestEntity> = emptyList()
    private var learningPaths: List<LearningPathEntity> = emptyList()
    private var learningPathSteps: List<LearningPathStepEntity> = emptyList()
    private var learningPathFacts: List<LearningPathFactEntity> = emptyList()
    private var learningPathFigures: List<LearningPathFigureEntity> = emptyList()
    private var learningPathMovies: List<LearningPathMovieCrossRef> = emptyList()
    private var assignedQuests: List<QuestUi> = emptyList()
    private var historyEvents: List<ActivityEventEntity> = emptyList()
    private var totalXp: Long = 0
    private var observedUserId: Long? = null
    private var observing = false
    private var bootstrapFailed = false
    private var catalogLoaded = false
    private var refreshJob: Job? = null
    private var followLimitDialog by mutableStateOf(false)
    private var guideVisible by mutableStateOf(false)
    private var rankUpName by mutableStateOf<String?>(null)
    private var rankCelebrationSeeded = false
    private var lastRankOrder = 1

    private var homeState by mutableStateOf(HomeUiState(loadState = LoadState.Loading))
    private var territoryState by mutableStateOf(emptyList<TerritoryUi>())
    private var currentState by mutableStateOf(emptyList<TerritoryUi>())
    private var decadeState by mutableStateOf(emptyList<TerritoryUi>())
    private var genreState by mutableStateOf(emptyList<TerritoryUi>())
    private var collectionState by mutableStateOf(emptyList<CollectionUi>())
    private var pathState by mutableStateOf(emptyList<PathUi>())
    private var badgeState by mutableStateOf(emptyList<BadgeUi>())
    private var rankState by mutableStateOf(emptyList<RankUi>())
    private var directorState by mutableStateOf(emptyList<DirectorUi>())
    private var movieState by mutableStateOf(
        MovieUi("", "", null, "", "", "", false),
    )
    private var profileState by mutableStateOf(ProfileUiState())
    private var statsState by mutableStateOf(StatsListsUi())
    private var selectedThemeMode by mutableStateOf(UrbinemaThemeMode.Dark)
    private var selectedLanguage by mutableStateOf(AppLanguage.System)
    private var grainEnabled by mutableStateOf(false)
    private var devModeEnabled by mutableStateOf(false)
    private var progressSnapshot: UserProgressStateEntity? = null
    private var scoreBaseline: Double? = null
    private var xpBaseline: Long? = null
    private var shownScoreGain: Double? = null
    private var shownXpGain: Long? = null
    private var showOnboarding by mutableStateOf(false)
    private var celebrationName by mutableStateOf<String?>(null)
    private var pendingBadgeCelebrations by mutableStateOf(listOf<BadgeUi>())
    private var completionBaselineReady = false
    private var lastCompletedCollectionIds = emptySet<String>()
    private var celebratedBadgeCodes = emptySet<String>()
    private var badgeCelebrationsSeeded = false
    private var badgeCelebrationPrefsReady = false
    private var progressHydrated = false
    private var earnedBadgesObserved = false
    private var userMoviesObserved = false

    override val home: HomeUiState get() = homeState
    override val territories: List<TerritoryUi> get() = territoryState
    override val currents: List<TerritoryUi> get() = currentState
    override val decades: List<TerritoryUi> get() = decadeState
    override val genres: List<TerritoryUi> get() = genreState
    override val collections: List<CollectionUi> get() = collectionState
    override val paths: List<PathUi> get() = pathState
    override val badges: List<BadgeUi> get() = badgeState
    override val ranks: List<RankUi> get() = rankState
    override val directors: List<DirectorUi> get() = directorState
    override val movie: MovieUi get() = movieState
    override val profile: ProfileUiState get() = profileState
    override val statsLists: StatsListsUi get() = statsState

    override fun statsShares(category: StatsCategory): List<StatShareUi> {
        if (category == StatsCategory.Films) {
            return statsState.films.map {
                StatShareUi("${it.title} · ${it.year}", sortKey = it.title, year = it.year)
            }
        }
        val watchedIds = HashSet<Long>().apply {
            watched.forEach { add(it.movieId) }
            addAll(optimisticWatchedIds)
        }
        val watchedMovies = moviesWithRelations.filter { it.movie.movieId in watchedIds }
        val total = watchedMovies.size
        fun pct(count: Int): Int = if (total == 0) 0 else ((count * 100.0) / total).roundToInt()
        return when (category) {
            StatsCategory.Films -> emptyList()
            StatsCategory.Countries -> countryEntities
                .filter { country ->
                    watchedMovies.any { rel -> rel.countries.any { it.countryId == country.countryId } }
                }
                .map { country ->
                    val count = watchedMovies.count { rel ->
                        rel.countries.any { it.countryId == country.countryId }
                    }
                    StatShareUi(localized(country.name, country.nameEn), pct(count))
                }
            StatsCategory.Decades -> watchedMovies
                .map { it.movie.releaseYear / 10 * 10 }
                .distinct()
                .sorted()
                .map { decade ->
                    val count = watchedMovies.count { it.movie.releaseYear / 10 * 10 == decade }
                    StatShareUi(decadeLabel(decade), pct(count), year = decade)
                }
            StatsCategory.Currents -> watchedMovies
                .flatMap { it.characteristics }
                .distinctBy { it.characteristicId }
                .map { current ->
                    val count = watchedMovies.count { rel ->
                        rel.characteristics.any { it.characteristicId == current.characteristicId }
                    }
                    StatShareUi(localized(current.name, current.nameEn), pct(count))
                }
            StatsCategory.Continents -> {
                val continentByCountryId = countryContinents.associate { it.countryId to it.continentId }
                val continentsById = continentEntities.associateBy { it.continentId }
                val watchedCountryIds = watchedMovies.flatMap { it.countries }.map { it.countryId }.toSet()
                countryContinents
                    .filter { it.countryId in watchedCountryIds }
                    .map { it.continentId }
                    .distinct()
                    .mapNotNull { id -> continentsById[id] }
                    .map { continent ->
                        val count = watchedMovies.count { rel ->
                            rel.countries.any { continentByCountryId[it.countryId] == continent.continentId }
                        }
                        StatShareUi(localized(continent.name, continent.nameEn), pct(count))
                    }
            }
            StatsCategory.Directors -> watchedMovies
                .flatMap { it.directors }
                .distinctBy { it.directorId }
                .map { director ->
                    val count = watchedMovies.count { rel ->
                        rel.directors.any { it.directorId == director.directorId }
                    }
                    StatShareUi(director.displayName, pct(count))
                }
        }
    }
    override val themeMode: UrbinemaThemeMode get() = selectedThemeMode
    override val language: AppLanguage get() = selectedLanguage
    override val filmGrain: Boolean get() = grainEnabled
    override val devToolsAvailable: Boolean get() = BuildConfig.DEV_TOOLS
    override val devMode: Boolean get() = devModeEnabled
    override val needsOnboarding: Boolean get() = showOnboarding
    override val completedCollectionCelebration: String? get() = celebrationName
    override val unlockedBadgeCelebration: BadgeUi? get() = pendingBadgeCelebrations.firstOrNull()
    override val followLimitReached: Boolean get() = followLimitDialog
    override val showAppGuide: Boolean get() = guideVisible
    override val rankUpCelebration: String? get() = rankUpName
    override val availableAvatars: List<String> get() = MediaPaths.PACKAGED_AVATAR_CODES

    init {
        retryBootstrap()
        viewModelScope.launch {
            preferencesRepository.themeMode.collectLatest {
                selectedThemeMode = when (it) {
                    ThemePreference.DARK -> UrbinemaThemeMode.Dark
                    ThemePreference.LIGHT -> UrbinemaThemeMode.Light
                    ThemePreference.SYSTEM -> UrbinemaThemeMode.System
                    ThemePreference.CYANOTYPE -> UrbinemaThemeMode.Cyanotype
                    ThemePreference.TIRAGE -> UrbinemaThemeMode.Tirage
                    ThemePreference.RAYONNAGE -> UrbinemaThemeMode.Rayonnage
                    ThemePreference.AFFICHE -> UrbinemaThemeMode.Affiche
                    ThemePreference.VELOURS -> UrbinemaThemeMode.Velours
                    ThemePreference.NUIT_AMERICAINE -> UrbinemaThemeMode.NuitAmericaine
                }
            }
        }
        viewModelScope.launch {
            preferencesRepository.language.collectLatest {
                selectedLanguage = when (it) {
                    LanguagePreference.SYSTEM -> AppLanguage.System
                    LanguagePreference.FRENCH -> AppLanguage.French
                    LanguagePreference.ENGLISH -> AppLanguage.English
                }
                refresh()
            }
        }
        viewModelScope.launch {
            preferencesRepository.filmGrain.collectLatest { grainEnabled = it }
        }
        viewModelScope.launch {
            preferencesRepository.devMode.collectLatest { stored ->
                devModeEnabled = BuildConfig.DEV_TOOLS && stored
                refresh()
            }
        }
        viewModelScope.launch {
            preferencesRepository.tutorialCompleted.collectLatest { completed ->
                guideVisible = !completed
            }
        }
        viewModelScope.launch {
            preferencesRepository.badgeCelebrations.collectLatest { prefs ->
                celebratedBadgeCodes = prefs.codes
                badgeCelebrationsSeeded = prefs.seeded
                badgeCelebrationPrefsReady = true
                refresh()
            }
        }
    }

    override fun retryBootstrap() {
        viewModelScope.launch {
            homeState = homeState.copy(loadState = LoadState.Loading)
            bootstrapFailed = false
            val ready = runCatching { bootstrapper.initialize() }
                .onFailure {
                    bootstrapFailed = true
                    Log.e(TAG, "Bootstrap failed", it)
                }
                .getOrDefault(false)
            if (!ready) bootstrapFailed = true
            observeDatabase()
        }
    }

    override fun setThemeMode(mode: UrbinemaThemeMode) {
        viewModelScope.launch {
            preferencesRepository.setThemeMode(
                when (mode) {
                    UrbinemaThemeMode.Dark -> ThemePreference.DARK
                    UrbinemaThemeMode.Light -> ThemePreference.LIGHT
                    UrbinemaThemeMode.System -> ThemePreference.SYSTEM
                    UrbinemaThemeMode.Cyanotype -> ThemePreference.CYANOTYPE
                    UrbinemaThemeMode.Tirage -> ThemePreference.TIRAGE
                    UrbinemaThemeMode.Rayonnage -> ThemePreference.RAYONNAGE
                    UrbinemaThemeMode.Affiche -> ThemePreference.AFFICHE
                    UrbinemaThemeMode.Velours -> ThemePreference.VELOURS
                    UrbinemaThemeMode.NuitAmericaine -> ThemePreference.NUIT_AMERICAINE
                }
            )
        }
    }

    override fun setLanguage(language: AppLanguage) {
        viewModelScope.launch {
            preferencesRepository.setLanguage(
                when (language) {
                    AppLanguage.System -> LanguagePreference.SYSTEM
                    AppLanguage.French -> LanguagePreference.FRENCH
                    AppLanguage.English -> LanguagePreference.ENGLISH
                }
            )
        }
    }

    override fun setFilmGrain(enabled: Boolean) {
        viewModelScope.launch { preferencesRepository.setFilmGrain(enabled) }
    }

    override fun setDevMode(enabled: Boolean) {
        if (!BuildConfig.DEV_TOOLS) return
        viewModelScope.launch { preferencesRepository.setDevMode(enabled) }
    }

    override fun setUsername(username: String) {
        val profile = user ?: return
        val normalized = username.trim()
        if (normalized.isEmpty() || normalized == profile.username) return
        viewModelScope.launch {
            database.progressDao().updateUsername(profile.userId, normalized)
        }
    }

    override fun setAge(age: Int) {
        val profile = user ?: return
        if (age !in MIN_AGE..MAX_AGE) return
        viewModelScope.launch {
            database.progressDao().updateBirthDate(profile.userId, birthDateFromAge(age))
            progressionCoordinator.recalculate(profile.userId)
        }
    }

    override fun setAvatar(code: String) {
        val profile = user ?: return
        val normalized = code.trim()
        if (normalized !in MediaPaths.PACKAGED_AVATAR_CODES || normalized == profile.avatarCode) return
        viewModelScope.launch {
            database.progressDao().updateAvatarCode(profile.userId, normalized)
        }
    }

    /**
     * Creates the local profile or completes a 0.1.6 leftover (pseudo without age).
     * Age is stored as 1 January of (current year − age). Avatar must be a packaged code.
     */
    override fun completeOnboarding(username: String, age: Int, avatarCode: String) {
        val normalized = username.trim()
        val avatar = avatarCode.trim()
        if (normalized.isEmpty() || age !in MIN_AGE..MAX_AGE) return
        if (avatar !in MediaPaths.PACKAGED_AVATAR_CODES) return
        val birthDate = birthDateFromAge(age)
        viewModelScope.launch {
            val existing = user
            if (existing != null) {
                database.progressDao().updateUsername(existing.userId, normalized)
                database.progressDao().updateBirthDate(existing.userId, birthDate)
                database.progressDao().updateAvatarCode(existing.userId, avatar)
                progressionCoordinator.recalculate(existing.userId)
                preferencesRepository.setTutorialCompleted(false)
                return@launch
            }
            val firstRank = database.progressDao().rankingByOrder(1) ?: return@launch
            runCatching {
                val userId = database.progressDao().insertUser(
                    UserEntity(
                        username = normalized,
                        birthDate = birthDate,
                        avatarCode = avatar,
                        rankingId = firstRank.rankingId,
                        createdAt = Instant.now(),
                    )
                )
                progressionCoordinator.recalculate(userId)
            }.onFailure { Log.e(TAG, "Onboarding profile insert failed", it) }
            preferencesRepository.setTutorialCompleted(false)
        }
    }

    /**
     * Marks the open film as seen (local date, once). Then rank/XP/badges and
     * weekly quests are recalculated from the validated set — not from this screen.
     */
    override fun markCurrentMovieWatched() {
        val currentMovie = moviesWithRelations.firstOrNull { it.movie.code == movieState.id } ?: return
        markMovie(currentMovie)
    }

    override fun markMovieWatched(code: String) {
        val movie = moviesWithRelations.firstOrNull { it.movie.code == code } ?: return
        markMovie(movie)
    }

    override fun replayAppGuide() {
        viewModelScope.launch { preferencesRepository.setTutorialCompleted(false) }
    }

    override fun dismissAppGuide() {
        viewModelScope.launch { preferencesRepository.setTutorialCompleted(true) }
    }

    override fun dismissRankUp() {
        rankUpName = null
    }

    /**
     * Marks a film as seen once. Film XP is granted only when it belongs to a
     * collection the profile currently follows.
     */
    private fun markMovie(currentMovie: MovieWithRelations) {
        val currentUser = user ?: return
        if (watched.any { it.movieId == currentMovie.movie.movieId }) return
        if (currentMovie.movie.movieId in optimisticWatchedIds) return
        optimisticWatchedIds = optimisticWatchedIds + currentMovie.movie.movieId
        paintFilmWatched(currentMovie.movie.code)
        if (movieState.id == currentMovie.movie.code) {
            movieState = movieState.copy(watched = true)
        }
        val awardXp = collectionsWithMovies.any { item ->
            item.collection.collectionId in followedCollectionIds &&
                item.movies.any { it.movieId == currentMovie.movie.movieId }
        }
        val film = currentMovie.movie
        val h = film.historicalDistance
        val a = film.artisticDemand
        val r = film.historicalRichness
        val c = film.culturalRichness
        val intrinsic = 1.0 + 2.0 * h + 2.0 * a + 2.0 * r + 3.0 * c
        val attenuated = kotlin.math.sqrt(intrinsic)
        val filmXp = if (awardXp) xpEngine.rewardForFilm() else 0
        Log.i(PROGRESS_TAG, "========== Film marqué Vu ==========")
        Log.i(
            PROGRESS_TAG,
            "Film ${film.code} «${film.frenchTitle ?: film.originalTitle}» (${film.releaseYear})",
        )
        Log.i(PROGRESS_TAG, "Axes: H(distance)=$h A(exigence)=$a R(importance)=$r C(richesse)=$c")
        Log.i(PROGRESS_TAG, "Poids brut W_f = 1 + 2H + 2A + 2R + 3C = ${"%.4f".format(intrinsic)}")
        Log.i(PROGRESS_TAG, "Poids atténué W' = sqrt(W_f) = ${"%.4f".format(attenuated)}  (ajouté au volume Vw)")
        Log.i(PROGRESS_TAG, "XP de ce film = $filmXp (collection suivie=$awardXp). Quêtes : Bronze 100 / Argent 250 / Or 500")
        viewModelScope.launch {
            progressRepository.markWatched(
                userId = currentUser.userId,
                movieId = currentMovie.movie.movieId,
                watchedOn = LocalDate.now(ZoneId.systemDefault()),
                activityPayloadJson = """{"version":1,"movieCode":"${currentMovie.movie.code}"}""",
                awardFilmXp = awardXp,
            )
            progressionCoordinator.recalculate(currentUser.userId)
            weeklyQuestCoordinator.onProgressChanged(currentUser.userId)
            val xp = database.progressDao().totalXp(currentUser.userId)
            val level = xpEngine.progress(xp, currentUser.maxLevelReached)
            Log.i(
                PROGRESS_TAG,
                "Après recalcul: XP total=$xp  niveau=${level.displayedLevel}  " +
                    "dansLeNiveau=${level.xpIntoLevel}  restantPourSuivant=${level.xpNeededForNextLevel}",
            )
        }
    }

    private fun watchedIdSet(): Set<Long> {
        val ids = HashSet<Long>(watched.size + optimisticWatchedIds.size)
        watched.forEach { ids.add(it.movieId) }
        ids.addAll(optimisticWatchedIds)
        return ids
    }

    private fun paintFilmWatched(code: String) {
        fun List<MovieSummaryUi>.mark(followedOnly: Boolean = false, followed: Boolean = true) =
            map { film ->
                if (film.id == code && (!followedOnly || followed)) film.copy(watched = true) else film
            }
        collectionState = collectionState.map { collection ->
            collection.copy(films = collection.films.mark(followedOnly = true, followed = collection.followed))
        }
        homeState = homeState.copy(
            collections = homeState.collections.map { collection ->
                collection.copy(films = collection.films.mark(followedOnly = true, followed = collection.followed))
            },
        )
        directorState = directorState.map { director ->
            director.copy(films = director.films.mark())
        }
    }

    override fun followCollection(code: String) {
        val currentUser = user ?: return
        val ui = collectionState.firstOrNull { it.id == code } ?: return
        if (ui.locked || ui.completed) return
        val inProgress = collectionState.count { it.followed && !it.completed }
        if (CollectionFollowRules.atFollowLimit(inProgress)) {
            followLimitDialog = true
            return
        }
        val collectionId = collectionsWithMovies.firstOrNull { it.collection.code == code }?.collection?.collectionId
            ?: return
        viewModelScope.launch {
            progressRepository.followCollection(currentUser.userId, collectionId)
        }
    }

    override fun unfollowCollection(code: String) {
        val currentUser = user ?: return
        val item = collectionsWithMovies.firstOrNull { it.collection.code == code } ?: return
        if (collectionState.firstOrNull { it.id == code }?.completed == true) return
        viewModelScope.launch {
            progressRepository.unfollowCollection(currentUser.userId, item.collection.collectionId)
        }
    }

    override fun setShowcaseBadges(codes: List<String>) {
        val currentUser = user ?: return
        val earned = earnedBadgeCodesOrdered.toSet()
        val encoded = ProfileBadges.encode(codes.filter { it in earned })
        viewModelScope.launch {
            database.progressDao().updateShowcaseBadgeCodes(
                currentUser.userId,
                encoded.ifBlank { null },
            )
        }
    }

    override fun movie(code: String): MovieUi? =
        moviesWithRelations.firstOrNull { it.movie.code == code }?.let(::toMovieUi)

    override fun openMovie(code: String) {
        moviesWithRelations.firstOrNull { it.movie.code == code }?.let { movieState = toMovieUi(it) }
    }

    override fun director(code: String): DirectorUi? = directorState.firstOrNull { it.id == code }

    /** Local search over films, countries, currents, collections, directors and genres. */
    override fun search(query: String): List<SearchHitUi> {
        val needle = query.trim()
        if (needle.isEmpty()) return emptyList()
        fun match(value: String) = value.contains(needle, ignoreCase = true)
        val movieHits = movieTitleHits(needle)
        val countryHits = territoryState.filter { match(it.name) || match(it.id) }.map {
            SearchHitUi(it.id, SearchKind.Country, it.name, "")
        }
        val currentHits = currentState.filter { match(it.name) || match(it.id) }.map {
            SearchHitUi(it.id, SearchKind.Current, it.name, "")
        }
        val collectionHits = collectionState.filter { match(it.name) }.map {
            SearchHitUi(it.id, SearchKind.Collection, it.name, it.shortDescription)
        }
        val directorHits = directorEntities.filter { match(it.displayName) || match(it.code) }.map {
            SearchHitUi(it.code, SearchKind.Director, it.displayName, "")
        }
        val genreHits = genreState.filter { match(it.name) || match(it.id) }.map {
            SearchHitUi(it.id, SearchKind.Genre, it.name, "")
        }
        return movieHits + countryHits + currentHits + collectionHits + directorHits + genreHits
    }

    override fun searchMovies(query: String): List<SearchHitUi> {
        val needle = query.trim()
        if (needle.isEmpty()) return emptyList()
        return movieTitleHits(needle).take(8)
    }

    private fun movieTitleHits(needle: String): List<SearchHitUi> {
        fun match(value: String) = value.contains(needle, ignoreCase = true)
        return moviesWithRelations.mapNotNull { rel ->
            val movie = rel.movie
            val french = movie.frenchTitle.orEmpty()
            val original = movie.originalTitle
            if (!match(french) && !match(original)) return@mapNotNull null
            val display = if (prefersEnglish()) original else french.ifBlank { original }
            val subtitle = buildString {
                append(listDirectorLabel(orderedDirectors(rel).map { it.displayName }))
                append(" · ")
                append(movie.releaseYear)
                if (french.isNotBlank() &&
                    !french.equals(original, ignoreCase = true) &&
                    match(original) &&
                    !match(french)
                ) {
                    append(" · ")
                    append(original)
                }
            }
            SearchHitUi(movie.code, SearchKind.Movie, display, subtitle)
        }.sortedWith(
            compareBy<SearchHitUi> { hit ->
                if (hit.title.startsWith(needle, ignoreCase = true)) 0 else 1
            }.thenBy { it.title.lowercase() },
        )
    }

    override fun collectionsForCountry(code: String): List<CollectionUi> =
        collectionState.filter { code in it.countryCodes }

    override fun collectionsForCurrent(code: String): List<CollectionUi> =
        collectionState.filter { code in it.characteristicCodes }

    override fun moviesForCountry(code: String): List<MovieSummaryUi> =
        moviesWithRelations.filter { rel -> rel.countries.any { it.code == code } }
            .map(::toWatchedSummary).sortedFilms(FilmListSort.TitleAsc)

    override fun moviesForCurrent(code: String): List<MovieSummaryUi> =
        moviesWithRelations.filter { rel -> rel.characteristics.any { it.code == code } }
            .map(::toWatchedSummary).sortedFilms(FilmListSort.TitleAsc)

    override fun moviesForDecade(code: String): List<MovieSummaryUi> =
        moviesWithRelations.filter { (it.movie.releaseYear / 10 * 10).toString() == code }
            .map(::toWatchedSummary).sortedFilms(FilmListSort.TitleAsc)

    override fun moviesForGenre(code: String): List<MovieSummaryUi> =
        moviesWithRelations.filter { rel -> rel.genres.any { it.code == code } }
            .map(::toWatchedSummary).sortedFilms(FilmListSort.TitleAsc)

    /**
     * Sky layout for one Atlas dimension, or a film-centred constellation.
     * Positions are stable for a given catalogue; glow still comes from [TerritoryUi].
     */
    override fun cinemaMap(layer: MapLayer, focusMovieCode: String): CinemaMapGraph {
        if (layer == MapLayer.AROUND_FILM) {
            val code = focusMovieCode.ifBlank { defaultSkyMovieCode() }
            return CinemaMapLayout.buildAround(code, constellationSeeds(code))
        }
        val continentCodeById = continentEntities.associate { it.continentId to it.code }
        val continentNameByCode = continentEntities.associate { it.code to localized(it.name, it.nameEn) }
        val continentByCountryId = countryContinents.associate { it.countryId to it.continentId }
        val continentByCountryCode = countryEntities.associate { country ->
            country.code to continentByCountryId[country.countryId]?.let { continentCodeById[it] }.orEmpty()
        }
        return when (layer) {
            MapLayer.AROUND_FILM -> CinemaMapGraph(layer, emptyList(), emptyList())
            MapLayer.COUNTRIES -> CinemaMapLayout.build(
                layer,
                territoryState.map { MapSeed(it.id, continentByCountryCode[it.id].orEmpty()) },
                moviesWithRelations.map { rel -> rel.countries.map { it.code } },
                continentNameByCode,
            )
            MapLayer.CURRENTS -> CinemaMapLayout.build(
                layer,
                currentState.map { MapSeed(it.id) },
                moviesWithRelations.map { rel -> rel.characteristics.map { it.code } },
            )
            MapLayer.DECADES -> CinemaMapLayout.build(
                layer,
                decadeState.map { MapSeed(it.id) },
            )
            MapLayer.GENRES -> CinemaMapLayout.build(
                layer,
                genreState.map { MapSeed(it.id) },
                moviesWithRelations.map { rel -> rel.genres.map { it.code } },
            )
            MapLayer.DIRECTORS -> CinemaMapLayout.build(
                layer,
                directorEntities.map { director ->
                    val films = moviesWithRelations.filter { rel ->
                        rel.directors.any { it.directorId == director.directorId }
                    }
                    val country = films.flatMap { it.countries }
                        .groupingBy { it.code }
                        .eachCount()
                        .maxByOrNull { it.value }
                        ?.key
                        .orEmpty()
                    MapSeed(director.code, continentByCountryCode[country].orEmpty())
                },
                moviesWithRelations.map { rel -> rel.directors.map { it.code } },
                continentNameByCode,
            )
            MapLayer.COLLECTIONS -> CinemaMapLayout.build(
                layer,
                collectionsWithMovies.map { MapSeed(it.collection.code) },
                moviesWithRelations.map { rel ->
                    collectionsWithMovies.filter { item ->
                        item.movies.any { it.movieId == rel.movie.movieId }
                    }.map { it.collection.code }
                },
            )
        }
    }

    /**
     * Wipes validations, follows, XP, badges and quests. Initiation lock comes
     * back: [CollectionUnlockRules.LOCKED_ORDINAL] until one Initiation film is seen.
     */
    override fun resetProgress() {
        val profile = user ?: return
        user = profile.copy(unlockedTrackOrdinal = CollectionUnlockRules.LOCKED_ORDINAL)
        watched = emptyList()
        optimisticWatchedIds = emptySet()
        followedCollectionIds = emptySet()
        rankCelebrationSeeded = false
        rankUpName = null
        scoreBaseline = null
        xpBaseline = null
        shownScoreGain = null
        shownXpGain = null
        refresh()
        viewModelScope.launch {
            progressRepository.resetProgress(profile.userId)
            progressionCoordinator.recalculate(profile.userId)
            weeklyQuestCoordinator.ensureCurrentWeek(profile.userId)
            completionBaselineReady = false
            lastCompletedCollectionIds = emptySet()
            celebratedBadgeCodes = emptySet()
            badgeCelebrationsSeeded = true
            progressHydrated = true
            pendingBadgeCelebrations = emptyList()
            preferencesRepository.setCelebratedBadges(emptySet())
        }
    }

    override fun dismissFollowLimit() {
        followLimitDialog = false
    }

    override fun dismissCollectionCelebration() {
        celebrationName = null
    }

    override fun dismissBadgeCelebration() {
        pendingBadgeCelebrations = pendingBadgeCelebrations.drop(1)
    }

    private fun observeDatabase() {
        if (observing) return
        observing = true
        viewModelScope.launch {
            runCatching { loadCatalogSnapshot() }
                .onFailure {
                    bootstrapFailed = true
                    Log.e(TAG, "Catalog snapshot failed", it)
                }
            catalogLoaded = true
            refreshNow()
        }
        viewModelScope.launch {
            database.progressDao().observeLocalUser().collectLatest {
                user = it
                refresh()
                if (it != null && observedUserId != it.userId) {
                    observedUserId = it.userId
                    observeUser(it)
                    viewModelScope.launch { progressionCoordinator.recalculate(it.userId) }
                }
            }
        }
    }

    /**
     * Catalogue is static after bootstrap import — load once instead of
     * 12 Room `@Relation` flows each triggering a full UI rebuild.
     */
    private suspend fun loadCatalogSnapshot() {
        val catalog = database.catalogDao()
        moviesWithRelations = catalog.allMoviesWithRelations()
        moviesByMovieId = moviesWithRelations.associateBy { it.movie.movieId }
        val byDirector = HashMap<Long, MutableList<MovieWithRelations>>()
        for (rel in moviesWithRelations) {
            for (director in rel.directors) {
                byDirector.getOrPut(director.directorId) { mutableListOf() }.add(rel)
            }
        }
        filmsByDirectorId = byDirector
        collectionsWithMovies = catalog.observeCollectionsWithMovies().first()
        collectionCountryRefs = catalog.observeCollectionCountries().first()
        collectionCharacteristicRefs = catalog.observeCollectionCharacteristics().first()
        countryEntities = catalog.observeCountries().first()
        continentEntities = catalog.observeContinents().first()
        countryContinents = catalog.observeCountryContinents().first()
        directorEntities = catalog.observeDirectors().first()
        val directorsById = directorEntities.associateBy { it.directorId }
        val billings: List<MovieDirectorBilling> = catalog.movieDirectorBillings()
        orderedDirectorsByMovieId = billings.groupBy { it.movieId }.mapValues { (_, rows) ->
            rows.sortedBy { it.billingOrder }.mapNotNull { directorsById[it.directorId] }
        }
        genreEntities = catalog.observeGenres().first()
        characteristicEntities = catalog.observeCharacteristics().first()
        badgeEntities = catalog.observeBadges().first()
        rankings = catalog.observeRankings().first()
        questEntities = catalog.observeQuests().first()
        learningPaths = catalog.allLearningPaths()
        learningPathSteps = catalog.allLearningPathSteps()
        learningPathFacts = catalog.allLearningPathFacts()
        learningPathFigures = catalog.allLearningPathFigures()
        learningPathMovies = catalog.allLearningPathMovies()
    }

    private fun observeUser(value: UserEntity) {
        val progress = database.progressDao()
        viewModelScope.launch { progress.observeUserMovies(value.userId).collectLatest { watched = it; userMoviesObserved = true; refresh() } }
        viewModelScope.launch {
            progress.observeFollowedCollectionIds(value.userId).collectLatest {
                followedCollectionIds = it.toSet()
                refresh()
            }
        }
        viewModelScope.launch { progress.observeTotalXp(value.userId).collectLatest { totalXp = it; refresh() } }
        viewModelScope.launch {
            progress.observeEarnedBadgeCodes(value.userId).collectLatest {
                earnedBadgeCodesOrdered = it
                earnedBadgesObserved = true
                refresh()
            }
        }
        viewModelScope.launch {
            progress.observeCollectionProgress(value.userId).collectLatest {
                collectionProgress = it.associateBy(CollectionProgressRow::collectionId)
                refresh()
            }
        }
        viewModelScope.launch {
            progress.observeCountryProgress(value.userId).collectLatest {
                countryProgress = it.associateBy(CountryProgressRow::countryId)
                refresh()
            }
        }
        viewModelScope.launch {
            progress.observeActivity(value.userId).collectLatest { events ->
                historyEvents = events
                refresh()
            }
        }
        viewModelScope.launch {
            progress.observeProgressState(value.userId).collectLatest { snapshot ->
                progressSnapshot = snapshot
                refresh()
            }
        }
        viewModelScope.launch {
            runCatching { weeklyQuestCoordinator.ensureCurrentWeek(value.userId) }
                .onFailure { Log.e(TAG, "Weekly quest assignment failed", it) }
            progress.observeQuestAssignmentsForWeek(
                value.userId,
                weeklyQuestCoordinator.currentWeekStartsAt(),
            ).collectLatest { assignments ->
                assignedQuests = assignments
                    .filter {
                        it.assignment.status == UserQuestStatus.ACTIVE ||
                            it.assignment.status == UserQuestStatus.COMPLETED
                    }
                    .sortedBy { it.definition.difficulty.ordinal }
                    .map {
                    QuestUi(
                        title = questTitle(it.definition.difficulty),
                        condition = it.definition.description,
                        rewardXp = it.assignment.xpRewardSnapshot,
                        progress = it.assignment.progress,
                        target = it.assignment.targetCountSnapshot,
                    )
                }
                refresh()
            }
        }
    }

    private fun refresh() {
        refreshJob?.cancel()
        refreshJob = viewModelScope.launch {
            delay(FunctionalLimits.UI_REFRESH_DEBOUNCE_MS)
            refreshNow()
        }
    }

    private fun refreshNow() {
        try {
            refreshUnsafe()
        } catch (error: Exception) {
            Log.e(TAG, "Failed to refresh UI from Room", error)
            if (moviesWithRelations.isEmpty()) {
                homeState = homeState.copy(loadState = LoadState.Error)
            }
        }
        showOnboarding = (user == null || user?.birthDate == null) &&
            !bootstrapFailed &&
            homeState.loadState == LoadState.Content
    }

    private fun refreshUnsafe() {
        val roomWatchedIds = watched.mapTo(hashSetOf(), UserMovieCrossRef::movieId)
        optimisticWatchedIds = optimisticWatchedIds.filterNot { it in roomWatchedIds }.toSet()
        val watchedIds = HashSet(roomWatchedIds).apply { addAll(optimisticWatchedIds) }
        val watchedMovies = moviesWithRelations.filter { it.movie.movieId in watchedIds }
        val level = xpEngine.progress(totalXp, user?.maxLevelReached ?: 1)
        val rank = rankings.firstOrNull { it.rankingId == user?.rankingId }
            ?: rankings.firstOrNull()
        noteRankChange(rank)
        val continentsById = continentEntities.associateBy { it.continentId }

        val countriesById = countryEntities.associateBy { it.countryId }
        val characteristicsById = characteristicEntities.associateBy { it.characteristicId }
        val countriesByCollection = collectionCountryRefs.groupBy { it.collectionId }.mapValues { (_, values) ->
            values.mapNotNull { countriesById[it.countryId]?.code }
        }
        val characteristicsByCollection = collectionCharacteristicRefs.groupBy { it.collectionId }.mapValues { (_, values) ->
            values.mapNotNull { characteristicsById[it.characteristicId]?.code }
        }
        val initiation = collectionsWithMovies.firstOrNull { it.collection.code == INITIATION_CODE }
        val initiationWatched = initiation?.movies?.count { movie -> movie.movieId in watchedIds } ?: 0
        val initiationFollowed = initiation?.collection?.collectionId in followedCollectionIds
        val profile = user
        val latchedOrdinal = profile?.unlockedTrackOrdinal ?: CollectionUnlockRules.LOCKED_ORDINAL
        val initiationOpen = CollectionUnlockRules.isInitiationOpen(initiationWatched, initiationFollowed)
        val qualifiedByTrack = CollectionTrack.entries.associateWith { track ->
            val inTrack = collectionsWithMovies.filter { collectionTrack(it.collection.track) == track }
            inTrack.count { item ->
                CollectionUnlockRules.isQualified(
                    watchedCount = item.movies.count { movie -> movie.movieId in watchedIds },
                    followed = item.collection.collectionId in followedCollectionIds,
                )
            } to inTrack.size
        }
        val openOrdinal = CollectionUnlockRules.latchedOpenOrdinal(
            initiationOpen = initiationOpen,
            tracks = CollectionTrack.entries.map { qualifiedByTrack.getValue(it) },
            latchedOrdinal = latchedOrdinal,
        )
        if (profile != null && initiationOpen && openOrdinal > profile.unlockedTrackOrdinal) {
            viewModelScope.launch {
                database.progressDao().advanceUnlockedTrackOrdinal(profile.userId, openOrdinal)
            }
        }

        collectionState = collectionsWithMovies.map { item ->
            val collection = item.collection
            val followed = collection.collectionId in followedCollectionIds
            val progress = collectionProgress[collection.collectionId]
            val rawProgress = percentage(progress?.watchedCount ?: 0, progress?.totalCount ?: 0)
            val filmSummaries = item.movies.map { movie ->
                val rel = moviesByMovieId[movie.movieId]
                toSummary(
                    rel ?: MovieWithRelations(movie, emptyList(), emptyList(), emptyList(), emptyList()),
                    watched = followed && movie.movieId in watchedIds,
                )
            }.sortedFilms(FilmListSort.YearAsc) // année croissante ; V3 : accessible → complexe
            val track = collectionTrack(collection.track)
            val lock = collectionLock(collection.code, track, openOrdinal, qualifiedByTrack)
            CollectionUi(
                id = collection.code,
                name = localized(collection.name, collection.nameEn),
                metadata = localized(collection.description, collection.descriptionEn),
                shortDescription = localized(collection.description, collection.descriptionEn),
                longDescription = localized(collection.longDescription, collection.longDescriptionEn),
                progress = if (followed) rawProgress else 0,
                films = filmSummaries,
                countryCodes = countriesByCollection[collection.collectionId].orEmpty(),
                characteristicCodes = characteristicsByCollection[collection.collectionId].orEmpty(),
                followed = followed,
                displayOrder = collection.displayOrder,
                track = track,
                locked = lock.locked,
                lockPreviousTrack = lock.previous,
                lockRequiredCollections = lock.requiredCollections,
                completed = followed && rawProgress >= 100,
            )
        }.sortedWith(compareBy<CollectionUi> { it.track.ordinal }.thenBy { it.displayOrder })
        pathState = learningPaths.map { path ->
            val steps = learningPathSteps.filter { it.pathId == path.pathId }.sortedBy { it.position }
            PathUi(
                id = path.code,
                name = localized(path.name, path.nameEn),
                summary = localized(path.summary, path.summaryEn),
                description = localized(path.description, path.descriptionEn),
                periodLabel = localized(path.periodLabel, path.periodLabelEn),
                steps = steps.map { step ->
                    val characteristic = characteristicEntities.firstOrNull { it.characteristicId == step.characteristicId }
                    PathStepUi(
                        id = step.code,
                        name = localized(step.name, step.nameEn),
                        periodLabel = localized(step.periodLabel, step.periodLabelEn),
                        description = localized(step.description, step.descriptionEn),
                        imageCode = characteristic?.code ?: step.code,
                        facts = learningPathFacts.filter { it.stepId == step.stepId }
                            .sortedBy { it.position }
                            .map { PathFactUi(localized(it.title, it.titleEn), localized(it.body, it.bodyEn)) },
                        figures = learningPathFigures.filter { it.stepId == step.stepId }
                            .sortedBy { it.position }
                            .map { figure ->
                                PathFigureUi(
                                    name = figure.displayName,
                                    role = localized(figure.role, figure.roleEn),
                                    directorCode = directorEntities.firstOrNull { it.directorId == figure.directorId }?.code,
                                )
                            },
                        movies = learningPathMovies.filter { it.stepId == step.stepId }
                            .sortedBy { it.position }
                            .mapNotNull { link -> moviesByMovieId[link.movieId]?.let { toSummary(it) } },
                        transition = localized(step.transitionText, step.transitionTextEn).takeIf { it.isNotBlank() },
                    )
                },
            )
        }
        val newlyCompleted = collectionState.filter { it.completed }.map { it.id }.toSet()
        if (!completionBaselineReady) {
            if (collectionsWithMovies.isNotEmpty()) {
                lastCompletedCollectionIds = newlyCompleted
                completionBaselineReady = true
            }
        } else {
            val justFinished = newlyCompleted - lastCompletedCollectionIds
            lastCompletedCollectionIds = newlyCompleted
            if (celebrationName == null) {
                celebrationName = justFinished.firstOrNull()?.let { code ->
                    collectionState.firstOrNull { it.id == code }?.name
                }
            }
        }
        territoryState = countryEntities.mapNotNull { country ->
            val progress = countryProgress[country.countryId]
            if ((progress?.totalCount ?: 0) <= 0) return@mapNotNull null
            territoryFromProgress(country.code, localized(country.name, country.nameEn), R.string.countries, progress)
        }
        currentState = characteristicEntities.mapNotNull { characteristic ->
            val total = moviesWithRelations.count { rel -> rel.characteristics.any { it.characteristicId == characteristic.characteristicId } }
            if (total <= 0) return@mapNotNull null
            val seen = watchedMovies.count { rel -> rel.characteristics.any { it.characteristicId == characteristic.characteristicId } }
            territoryFromCounts(characteristic.code, localized(characteristic.name, characteristic.nameEn), R.string.currents, seen, total)
        }
        decadeState = moviesWithRelations
            .map { it.movie.releaseYear / 10 * 10 }
            .distinct()
            .sorted()
            .map { decade ->
                val total = moviesWithRelations.count { it.movie.releaseYear / 10 * 10 == decade }
                val seen = watchedMovies.count { it.movie.releaseYear / 10 * 10 == decade }
                territoryFromCounts(decade.toString(), decadeLabel(decade), R.string.decades, seen, total)
            }
        genreState = genreEntities.mapNotNull { genre ->
            val total = moviesWithRelations.count { rel -> rel.genres.any { it.genreId == genre.genreId } }
            if (total <= 0) return@mapNotNull null
            val seen = watchedMovies.count { rel -> rel.genres.any { it.genreId == genre.genreId } }
            territoryFromCounts(genre.code, localized(genre.name, genre.nameEn), R.string.genres, seen, total)
        }
        val earnedCodes = earnedBadgeCodesOrdered.toSet()
        val showcase = ProfileBadges.resolve(earnedBadgeCodesOrdered, user?.showcaseBadgeCodes)
        badgeState = badgeEntities.sortedWith(compareBy({ it.difficulty }, { it.code })).map {
            BadgeUi(
                code = it.code,
                name = localized(it.name, it.nameEn),
                condition = localized(it.description, it.descriptionEn),
                earned = it.code in earnedCodes,
                difficulty = it.difficulty,
                showcaseSlot = showcase.indexOf(it.code).takeIf { slot -> slot >= 0 },
            )
        }
        if (!badgeCelebrationPrefsReady || !earnedBadgesObserved || !userMoviesObserved) {
            // Wait until Room + DataStore have a first snapshot before celebrating.
        } else if (!progressHydrated) {
            progressHydrated = true
            if (!badgeCelebrationsSeeded) {
                celebratedBadgeCodes = earnedCodes
                badgeCelebrationsSeeded = true
                viewModelScope.launch { preferencesRepository.setCelebratedBadges(earnedCodes) }
            }
        } else {
            val justEarned = earnedBadgeCodesOrdered.filter { it !in celebratedBadgeCodes }
            if (justEarned.isNotEmpty()) {
                celebratedBadgeCodes = celebratedBadgeCodes + justEarned.toSet()
                pendingBadgeCelebrations = pendingBadgeCelebrations +
                    justEarned.mapNotNull { code -> badgeState.firstOrNull { it.code == code } }
                viewModelScope.launch { preferencesRepository.setCelebratedBadges(celebratedBadgeCodes) }
            }
        }
        rankState = rankings.sortedBy { it.displayOrder }.map {
            RankUi(
                id = it.code,
                order = it.displayOrder,
                name = localized(it.name, it.nameEn),
                description = localized(it.description, it.descriptionEn),
                longDescription = localized(it.longDescription, it.longDescriptionEn).ifBlank {
                    localized(it.description, it.descriptionEn)
                },
                current = it.rankingId == rank?.rankingId,
            )
        }
        val collectionsByFilmId = HashMap<String, MutableList<CollectionUi>>()
        for (collection in collectionState) {
            for (film in collection.films) {
                collectionsByFilmId.getOrPut(film.id) { mutableListOf() }.add(collection)
            }
        }
        directorState = directorEntities.mapNotNull { director ->
            val rels = filmsByDirectorId[director.directorId].orEmpty()
            if (rels.isEmpty()) return@mapNotNull null
            val films = rels
                .map { rel -> toSummary(rel, watched = rel.movie.movieId in watchedIds) }
                .sortedFilms(FilmListSort.TitleAsc)
            val linked = LinkedHashMap<String, CollectionUi>()
            for (film in films) {
                for (collection in collectionsByFilmId[film.id].orEmpty()) {
                    linked.putIfAbsent(collection.id, collection)
                }
            }
            DirectorUi(
                director.code,
                director.displayName,
                films,
                linked.values.toList(),
                director.biographyFor(prefersEnglish()),
            )
        }

        moviesWithRelations.firstOrNull { it.movie.code == movieState.id }?.let { rel ->
            val ui = toMovieUi(rel)
            movieState = ui.copy(watched = movieState.watched || ui.watched)
        }

        val xpTarget = level.xpNeededForNextLevel
            ?.plus(level.xpIntoLevel)
            ?.toInt()
            ?: level.xpIntoLevel.toInt()
        val rankLong = rank?.longDescription ?: rank?.description.orEmpty()
        val dev = if (devModeEnabled) devSnapshot(level, rank?.displayOrder ?: 1) else null
        homeState = homeState.copy(
            loadState = when {
                !catalogLoaded -> LoadState.Loading
                moviesWithRelations.isNotEmpty() -> LoadState.Content
                bootstrapFailed -> LoadState.Error
                else -> LoadState.Empty
            },
            rank = rank?.name ?: "Novice",
            rankNumber = rank?.displayOrder ?: 1,
            rankLongDescription = rankLong,
            level = level.displayedLevel,
            xp = level.xpIntoLevel.toInt(),
            nextLevelXp = xpTarget,
            quests = assignedQuests,
            collections = collectionState.filter { it.followed && !it.completed && !it.locked },
            history = historyEvents.map { event ->
                HistoryUi(
                    dateLabel = formatHistoryDate(event.occurredAt.atZone(ZoneId.systemDefault()).toLocalDate()),
                    type = event.type,
                    subject = historySubject(event.type, event.payloadJson),
                )
            },
            dev = dev,
        )
        val watchedCountryIds = watchedMovies.flatMap { it.countries }.map { it.countryId }.toSet()
        val continentIds = countryContinents.filter { it.countryId in watchedCountryIds }.map { it.continentId }.toSet()
        profileState = ProfileUiState(
            nickname = user?.username ?: "",
            ageYears = user?.birthDate?.let { Year.now().value - it.year },
            rank = rank?.name ?: "Novice",
            rankCode = rank?.code ?: "RANK_01",
            rankNumber = rank?.displayOrder ?: 1,
            rankLongDescription = rankLong,
            level = level.displayedLevel,
            xp = totalXp.coerceAtMost(Int.MAX_VALUE.toLong()).toInt(),
            xpIntoLevel = level.xpIntoLevel.toInt(),
            nextLevelXp = xpTarget,
            films = watched.size,
            countries = countryProgress.values.count { it.watchedCount > 0 },
            decades = watchedMovies.map { it.movie.releaseYear / 10 }.distinct().size,
            currents = watchedMovies.flatMap { it.characteristics }.map { it.characteristicId }.distinct().size,
            continents = continentIds.size,
            directors = watchedMovies.flatMap { it.directors }.map { it.directorId }.distinct().size,
            avatarCode = user?.avatarCode,
            dev = dev,
        )
        statsState = StatsListsUi(
            films = watchedMovies.map(::toSummary),
            countries = countryEntities.filter { (countryProgress[it.countryId]?.watchedCount ?: 0) > 0 }
                .map { localized(it.name, it.nameEn) },
            decades = watchedMovies.map { it.movie.releaseYear / 10 * 10 }.distinct().sorted().map { decadeLabel(it) },
            currents = watchedMovies.flatMap { it.characteristics }.distinctBy { it.characteristicId }
                .map { localized(it.name, it.nameEn) },
            continents = continentIds.mapNotNull { id ->
                continentsById[id]?.let { localized(it.name, it.nameEn) }
            },
            directors = watchedMovies.flatMap { it.directors }.distinctBy { it.directorId }.map { it.displayName },
        )
    }

    override fun defaultSkyMovieCode(): String {
        val lastWatchedId = watched.firstOrNull()?.movieId
        if (lastWatchedId != null) {
            moviesWithRelations.firstOrNull { it.movie.movieId == lastWatchedId }?.movie?.code?.let { return it }
        }
        collectionsWithMovies.firstOrNull { it.collection.code == INITIATION_CODE }
            ?.movies?.firstOrNull()?.code?.let { return it }
        return moviesWithRelations.firstOrNull()?.movie?.code.orEmpty()
    }

    override fun mapNodeUi(id: String, kind: MapNodeKind): TerritoryUi? = when (kind) {
        MapNodeKind.FILM -> moviesWithRelations.firstOrNull { it.movie.code == id }?.let { rel ->
            val summary = toWatchedSummary(rel)
            TerritoryUi(
                summary.id,
                summary.title,
                R.string.films,
                if (summary.watched) 100 else 0,
                if (summary.watched) ExplorationState.Mastered else ExplorationState.Unexplored,
                listOfNotNull(summary.director.takeIf { it.isNotBlank() }, summary.year.toString())
                    .joinToString(" · "),
            )
        }
        MapNodeKind.COUNTRY -> territories.firstOrNull { it.id == id }
        MapNodeKind.CURRENT -> currents.firstOrNull { it.id == id }
        MapNodeKind.DECADE -> decades.firstOrNull { it.id == id }
        MapNodeKind.GENRE -> genres.firstOrNull { it.id == id }
        MapNodeKind.DIRECTOR -> directors.firstOrNull { it.id == id }?.let { director ->
            val seen = director.films.count { it.watched }
            val total = director.films.size
            val percent = if (total == 0) 0 else seen * 100 / total
            TerritoryUi(
                director.id,
                director.name,
                R.string.directors,
                percent,
                explorationFromProgress(percent),
                filmCount = total,
            )
        }
        MapNodeKind.COLLECTION -> collections.firstOrNull { it.id == id }?.let { collection ->
            TerritoryUi(
                collection.id,
                collection.name,
                R.string.all_collections,
                collection.progress,
                explorationFromProgress(collection.progress),
                collection.shortDescription,
                filmCount = collection.films.size,
            )
        }
        MapNodeKind.TERRITORY ->
            territories.firstOrNull { it.id == id }
                ?: currents.firstOrNull { it.id == id }
                ?: decades.firstOrNull { it.id == id }
                ?: genres.firstOrNull { it.id == id }
    }

    private fun explorationFromProgress(percent: Int): ExplorationState = when {
        percent <= 0 -> ExplorationState.Unexplored
        percent >= 100 -> ExplorationState.Mastered
        percent >= 75 -> ExplorationState.Completed
        else -> ExplorationState.Explored
    }

    private fun constellationSeeds(focusCode: String): List<ConstellationSeed> {
        val focus = moviesWithRelations.firstOrNull { it.movie.code == focusCode } ?: return emptyList()
        val seeds = mutableListOf<ConstellationSeed>()
        seeds += ConstellationSeed(focus.movie.code, MapNodeKind.FILM, 0)
        focus.directors.forEach { seeds += ConstellationSeed(it.code, MapNodeKind.DIRECTOR, 1) }
        focus.countries.forEach { seeds += ConstellationSeed(it.code, MapNodeKind.COUNTRY, 1) }
        focus.genres.forEach { seeds += ConstellationSeed(it.code, MapNodeKind.GENRE, 1) }
        focus.characteristics.forEach { seeds += ConstellationSeed(it.code, MapNodeKind.CURRENT, 1) }
        val decade = (focus.movie.releaseYear / 10 * 10).toString()
        seeds += ConstellationSeed(decade, MapNodeKind.DECADE, 1)
        collectionsWithMovies.filter { item ->
            item.movies.any { it.movieId == focus.movie.movieId }
        }.forEach { seeds += ConstellationSeed(it.collection.code, MapNodeKind.COLLECTION, 1) }
        val ring1Ids = seeds.filter { it.ring == 1 }.map { it.id }.toSet()
        val related = moviesWithRelations.mapNotNull { other ->
            if (other.movie.code == focusCode) return@mapNotNull null
            val shared = mutableListOf<String>()
            var score = 0
            other.directors.forEach { director ->
                if (focus.directors.any { it.directorId == director.directorId }) {
                    score += 4
                    shared += director.code
                }
            }
            collectionsWithMovies.filter { item ->
                item.movies.any { it.movieId == other.movie.movieId } &&
                    item.movies.any { it.movieId == focus.movie.movieId }
            }.forEach { item ->
                score += 3
                shared += item.collection.code
            }
            other.characteristics.forEach { current ->
                if (focus.characteristics.any { it.characteristicId == current.characteristicId }) {
                    score += 3
                    shared += current.code
                }
            }
            other.countries.forEach { country ->
                if (focus.countries.any { it.countryId == country.countryId }) {
                    score += 2
                    shared += country.code
                }
            }
            val otherDecade = (other.movie.releaseYear / 10 * 10).toString()
            if (otherDecade == decade) {
                score += 2
                shared += decade
            }
            other.genres.forEach { genre ->
                if (focus.genres.any { it.genreId == genre.genreId }) {
                    score += 1
                    shared += genre.code
                }
            }
            val kept = shared.filter { it in ring1Ids }
            if (score <= 0) null
            else ConstellationSeed(other.movie.code, MapNodeKind.FILM, 2, score, kept)
        }.sortedByDescending { it.relatedness }.take(CinemaMapLayout.MAX_RELATED_FILMS)
        seeds += related
        return CinemaMapLayout.dedupeConstellation(seeds, ::constellationLabel)
    }

    private fun orderedDirectors(rel: MovieWithRelations): List<DirectorEntity> {
        val ordered = orderedDirectorsByMovieId[rel.movie.movieId]
        return if (!ordered.isNullOrEmpty()) ordered else rel.directors
    }

    private fun toMovieUi(rel: MovieWithRelations): MovieUi {
        val movie = rel.movie
        val watchedIds = watchedIdSet()
        val directors = orderedDirectors(rel)
        val countryNames = rel.countries.joinToString(" · ") { localized(it.name, it.nameEn) }
        val genreNames = rel.genres.map { localized(it.name, it.nameEn) }
        return MovieUi(
            id = movie.code,
            originalTitle = movie.originalTitle,
            localizedTitle = if (prefersEnglish()) {
                null
            } else {
                movie.frenchTitle?.takeIf { it != movie.originalTitle }
            },
            credits = listOfNotNull(
                directors.joinToString(", ") { it.displayName }.takeIf { it.isNotBlank() },
                movie.releaseYear.toString(),
            ).joinToString(" · "),
            metadata = listOfNotNull(
                countryNames.takeIf { it.isNotBlank() },
                formatDuration(movie.durationMinutes),
                genreNames.joinToString(", ").takeIf { it.isNotBlank() },
            ).joinToString(" · "),
            synopsis = movie.synopsis.orEmpty(),
            watched = movie.movieId in watchedIds,
            countries = rel.countries.map {
                TerritoryUi(it.code, localized(it.name, it.nameEn), R.string.countries, 0, ExplorationState.Unexplored)
            },
            genres = rel.genres.map {
                TerritoryUi(it.code, localized(it.name, it.nameEn), R.string.genres, 0, ExplorationState.Unexplored)
            },
            directorIds = directors.map { it.code },
            releaseYear = movie.releaseYear,
            directorCredits = directors.map { DirectorCreditUi(it.code, it.displayName) },
        )
    }

    private fun toWatchedSummary(rel: MovieWithRelations): MovieSummaryUi {
        val watchedIds = watchedIdSet()
        return toSummary(rel, watched = rel.movie.movieId in watchedIds)
    }

    private fun toSummary(rel: MovieWithRelations, watched: Boolean = false): MovieSummaryUi = MovieSummaryUi(
        id = rel.movie.code,
        title = displayTitle(rel.movie),
        year = rel.movie.releaseYear,
        director = listDirectorLabel(orderedDirectors(rel).map { it.displayName }),
        watched = watched,
    )

    private fun collectionTrack(raw: String): CollectionTrack =
        CollectionTrack.entries.firstOrNull { it.name == raw } ?: when (raw) {
            "JOURNEY" -> CollectionTrack.CLUB
            "DEMANDING" -> CollectionTrack.CINEMATHEQUE
            else -> CollectionTrack.CLUB
        }

    private fun questUi(quest: QuestEntity): QuestUi = QuestUi(
        title = questTitle(quest.difficulty),
        condition = localized(quest.description, quest.descriptionEn),
        rewardXp = when (quest.difficulty) {
            QuestDifficulty.BRONZE -> 100
            QuestDifficulty.SILVER -> 250
            QuestDifficulty.GOLD -> 500
        },
        progress = 0,
        target = quest.targetCount,
    )

    private fun questTitle(difficulty: QuestDifficulty): Int = when (difficulty) {
        QuestDifficulty.BRONZE -> R.string.quest_bronze_title
        QuestDifficulty.SILVER -> R.string.quest_silver_title
        QuestDifficulty.GOLD -> R.string.quest_gold_title
    }

    private fun territoryFromProgress(
        id: String,
        name: String,
        category: Int,
        progress: CountryProgressRow?,
    ): TerritoryUi = territoryFromCounts(id, name, category, progress?.watchedCount ?: 0, progress?.totalCount ?: 0)

    private fun territoryFromCounts(
        id: String,
        name: String,
        category: Int,
        seen: Int,
        total: Int,
    ): TerritoryUi {
        val percent = percentage(seen, total)
        return TerritoryUi(
            id = id,
            name = name,
            category = category,
            progress = percent,
            filmCount = total,
            state = when {
                percent == 0 -> ExplorationState.Unexplored
                percent >= 100 -> ExplorationState.Mastered
                percent >= 75 -> ExplorationState.Completed
                percent > 0 -> ExplorationState.Explored
                else -> ExplorationState.InProgress
            },
        )
    }

    private fun constellationLabel(seed: ConstellationSeed): String = when (seed.kind) {
        MapNodeKind.FILM -> moviesWithRelations.firstOrNull { it.movie.code == seed.id }?.movie
            ?.let(::displayTitle)
            .orEmpty()
        MapNodeKind.DIRECTOR -> directorEntities.firstOrNull { it.code == seed.id }?.displayName.orEmpty()
        MapNodeKind.COUNTRY -> countryEntities.firstOrNull { it.code == seed.id }
            ?.let { localized(it.name, it.nameEn) }.orEmpty()
        MapNodeKind.GENRE -> genreEntities.firstOrNull { it.code == seed.id }
            ?.let { localized(it.name, it.nameEn) }.orEmpty()
        MapNodeKind.CURRENT -> characteristicEntities.firstOrNull { it.code == seed.id }
            ?.let { localized(it.name, it.nameEn) }.orEmpty()
        MapNodeKind.DECADE -> seed.id
        MapNodeKind.COLLECTION -> collectionsWithMovies.firstOrNull { it.collection.code == seed.id }
            ?.collection?.let { localized(it.name, it.nameEn) }.orEmpty()
        MapNodeKind.TERRITORY -> seed.id
    }

    private fun prefersEnglish(): Boolean = when (selectedLanguage) {
        AppLanguage.English -> true
        AppLanguage.French -> false
        AppLanguage.System -> java.util.Locale.getDefault().language.startsWith("en")
    }

    private fun localized(french: String?, english: String?): String {
        val fr = french?.trim().orEmpty()
        val en = english?.trim().orEmpty()
        return if (prefersEnglish()) en.ifBlank { fr } else fr.ifBlank { en }
    }

    private fun displayTitle(movie: MovieEntity): String =
        if (prefersEnglish()) movie.originalTitle else movie.frenchTitle ?: movie.originalTitle

    private fun DirectorEntity.biographyFor(english: Boolean): String {
        val french = biography?.trim().orEmpty()
        val englishText = biographyEn?.trim().orEmpty()
        return if (english) englishText.ifBlank { french } else french.ifBlank { englishText }
    }

    private fun decadeLabel(decade: Int): String {
        return if (prefersEnglish()) "${decade}s" else "Années $decade"
    }

    private fun historySubject(type: String, payloadJson: String): String {
        val payload = runCatching { Json.parseToJsonElement(payloadJson).jsonObject }.getOrNull()
        return when (type) {
            HistoryUi.MOVIE_VALIDATED -> {
                val code = payload?.get("movieCode")?.jsonPrimitive?.content
                val movie = moviesWithRelations.firstOrNull { it.movie.code == code }?.movie
                movie?.let(::displayTitle)
                    ?: code?.let(::titleFromEditorialCode)
                    ?: ""
            }
            HistoryUi.BADGE_EARNED -> {
                val code = payload?.get("badgeCode")?.jsonPrimitive?.content
                badgeEntities.firstOrNull { it.code == code }?.let { localized(it.name, it.nameEn) }
                    ?: code.orEmpty()
            }
            HistoryUi.RANK_UP -> {
                val code = payload?.get("rankCode")?.jsonPrimitive?.content
                rankings.firstOrNull { it.code == code }?.let { localized(it.name, it.nameEn) }
                    ?: code.orEmpty()
            }
            else -> ""
        }
    }

    private fun titleFromEditorialCode(code: String): String =
        code.substringBeforeLast('_')
            .split('_')
            .filter { it.isNotBlank() }
            .joinToString(" ") { part ->
                part.lowercase().replaceFirstChar { char -> char.titlecase() }
            }

    private fun devSnapshot(level: fr.jsisie.urbinema.domain.xp.LevelProgress, rankOrder: Int): DevProgressUi {
        val score = progressSnapshot?.score ?: 0.0
        val thresholds = RankDefaults.thresholds
        val floor = if (rankOrder <= 1) 0.0 else thresholds[rankOrder - 2]
        val next = thresholds.getOrNull(rankOrder - 1)
        val remaining = if (next == null) 0.0 else (next - score).coerceAtLeast(0.0)
        val span = if (next == null) 1.0 else (next - floor).coerceAtLeast(1e-9)
        val fraction = if (next == null) 1f else ((score - floor) / span).toFloat().coerceIn(0f, 1f)
        val into = level.xpIntoLevel
        val xpLeft = level.xpNeededForNextLevel
        val xpSpan = into + (xpLeft ?: 0L)
        val xpFraction = if (xpLeft == null) 1f else (into.toFloat() / xpSpan.coerceAtLeast(1)).coerceIn(0f, 1f)
        if (progressSnapshot != null) {
            val previousScore = scoreBaseline
            val previousXp = xpBaseline
            if (previousScore == null) {
                scoreBaseline = score
                xpBaseline = totalXp
            } else if (score != previousScore || totalXp != previousXp) {
                shownScoreGain = score - previousScore
                shownXpGain = totalXp - (previousXp ?: totalXp)
                scoreBaseline = score
                xpBaseline = totalXp
            }
        }
        return DevProgressUi(
            rankOrder = rankOrder,
            rawRank = progressSnapshot?.rawRankOrder ?: rankOrder,
            score = score,
            floor = floor,
            nextThreshold = next,
            remaining = remaining,
            fraction = fraction,
            lastScoreGain = shownScoreGain,
            weightedVolume = progressSnapshot?.weightedVolume ?: 0.0,
            diversity = progressSnapshot?.diversity ?: 0.0,
            depth = progressSnapshot?.depth ?: 0.0,
            xpIntoLevel = into.toInt(),
            xpRemaining = xpLeft?.toInt(),
            xpFraction = xpFraction,
            lastXpGain = shownXpGain?.toInt(),
        )
    }

    private fun collectionLock(
        code: String,
        track: CollectionTrack,
        openOrdinal: Int,
        qualifiedByTrack: Map<CollectionTrack, Pair<Int, Int>>,
    ): CollectionLockUi {
        if (devModeEnabled) return CollectionLockUi()
        if (code == INITIATION_CODE) return CollectionLockUi()
        if (!CollectionUnlockRules.isTrackLocked(track.ordinal, openOrdinal)) return CollectionLockUi()
        if (openOrdinal < 0) return CollectionLockUi(locked = true)
        val previous = CollectionTrack.entries[track.ordinal - 1]
        val size = qualifiedByTrack.getValue(previous).second
        return CollectionLockUi(
            locked = true,
            previous = previous,
            requiredCollections = CollectionUnlockRules.requiredStartedCount(size),
        )
    }

    private data class CollectionLockUi(
        val locked: Boolean = false,
        val previous: CollectionTrack? = null,
        val requiredCollections: Int = CollectionUnlockRules.MIN_STARTED_COLLECTIONS,
    )

    private fun formatHistoryDate(date: LocalDate): String {
        val today = LocalDate.now(ZoneId.systemDefault())
        return when (date) {
            today -> "today"
            today.minusDays(1) -> "yesterday"
            else -> date.format(DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM))
        }
    }

    private fun percentage(value: Int, total: Int): Int =
        if (total <= 0) 0 else (value * 100 / total).coerceIn(0, 100)

    private fun noteRankChange(rank: RankingEntity?) {
        val order = rank?.displayOrder ?: return
        if (user == null || !catalogLoaded) return
        if (!rankCelebrationSeeded) {
            lastRankOrder = order
            rankCelebrationSeeded = true
            return
        }
        if (order > lastRankOrder) {
            rankUpName = rank.name
        }
        lastRankOrder = order
    }

    private fun formatDuration(minutes: Int): String {
        val hours = minutes / 60
        val rest = minutes % 60
        return when {
            hours == 0 -> "$rest min"
            rest == 0 -> "${hours}h"
            else -> "${hours}h${rest.toString().padStart(2, '0')}"
        }
    }

    private companion object {
        const val TAG = "UrbinemaViewModel"
        const val PROGRESS_TAG = "UrbinemaProgress"
        const val INITIATION_CODE = "COLLECTION_INITIATION"
        const val MIN_AGE = FunctionalLimits.MIN_USER_AGE
        const val MAX_AGE = FunctionalLimits.MAX_USER_AGE

        fun birthDateFromAge(age: Int): LocalDate = LocalDate.of(Year.now().value - age, 1, 1)
    }
}
