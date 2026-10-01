package fr.jsisie.urbinema.data.preferences

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.urbinemaPreferences by preferencesDataStore("urbinema_preferences")

enum class ThemePreference { DARK, LIGHT, SYSTEM, CYANOTYPE, TIRAGE, RAYONNAGE, AFFICHE, VELOURS, NUIT_AMERICAINE }

enum class LanguagePreference { SYSTEM, FRENCH, ENGLISH }

data class BadgeCelebrationPrefs(
    val seeded: Boolean = false,
    val codes: Set<String> = emptySet(),
)

/** Stores only lightweight presentation preferences; Room owns user data. */
class PreferencesRepository(private val context: Context) {
    val themeMode: Flow<ThemePreference> = context.urbinemaPreferences.data.map { values ->
        values[THEME_MODE]?.let { stored ->
            ThemePreference.entries.firstOrNull { it.name == stored }
        } ?: ThemePreference.DARK
    }

    val language: Flow<LanguagePreference> = context.urbinemaPreferences.data.map { values ->
        values[LANGUAGE]?.let { stored ->
            LanguagePreference.entries.firstOrNull { it.name == stored }
        } ?: LanguagePreference.SYSTEM
    }

    val filmGrain: Flow<Boolean> = context.urbinemaPreferences.data.map { values ->
        values[FILM_GRAIN] ?: false
    }

    val devMode: Flow<Boolean> = context.urbinemaPreferences.data.map { values ->
        values[DEV_MODE] ?: false
    }

    val badgeCelebrations: Flow<BadgeCelebrationPrefs> = context.urbinemaPreferences.data.map { values ->
        BadgeCelebrationPrefs(
            seeded = values[BADGE_CELEBRATION_SEEDED] ?: false,
            codes = values[BADGE_CELEBRATION_CODES]
                ?.split('\u001f')
                ?.filter { it.isNotBlank() }
                ?.toSet()
                .orEmpty(),
        )
    }

    val tutorialCompleted: Flow<Boolean> = context.urbinemaPreferences.data.map { values ->
        values[TUTORIAL_COMPLETED] ?: true
    }

    suspend fun setTutorialCompleted(completed: Boolean) {
        context.urbinemaPreferences.edit { it[TUTORIAL_COMPLETED] = completed }
    }

    suspend fun setThemeMode(mode: ThemePreference) {
        context.urbinemaPreferences.edit { it[THEME_MODE] = mode.name }
    }

    suspend fun setLanguage(language: LanguagePreference) {
        context.urbinemaPreferences.edit { it[LANGUAGE] = language.name }
    }

    suspend fun setFilmGrain(enabled: Boolean) {
        context.urbinemaPreferences.edit { it[FILM_GRAIN] = enabled }
    }

    suspend fun setDevMode(enabled: Boolean) {
        context.urbinemaPreferences.edit { it[DEV_MODE] = enabled }
    }

    suspend fun setCelebratedBadges(codes: Set<String>) {
        context.urbinemaPreferences.edit { values ->
            values[BADGE_CELEBRATION_SEEDED] = true
            values[BADGE_CELEBRATION_CODES] = codes.sorted().joinToString("\u001f")
        }
    }

    private companion object {
        val THEME_MODE = stringPreferencesKey("theme_mode")
        val LANGUAGE = stringPreferencesKey("language")
        val FILM_GRAIN = booleanPreferencesKey("film_grain")
        val DEV_MODE = booleanPreferencesKey("dev_mode")
        val BADGE_CELEBRATION_SEEDED = booleanPreferencesKey("badge_celebration_seeded")
        val BADGE_CELEBRATION_CODES = stringPreferencesKey("badge_celebration_codes")
        val TUTORIAL_COMPLETED = booleanPreferencesKey("tutorial_completed")
    }
}
