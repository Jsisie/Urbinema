package fr.jsisie.urbinema.app.di

import fr.jsisie.urbinema.app.MainViewModel
import fr.jsisie.urbinema.app.startup.AppBootstrapper
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.importer.CatalogImporter
import fr.jsisie.urbinema.data.preferences.PreferencesRepository
import fr.jsisie.urbinema.data.repository.CatalogRepository
import fr.jsisie.urbinema.data.repository.ProgressRepository
import fr.jsisie.urbinema.data.repository.ProgressionCoordinator
import fr.jsisie.urbinema.data.repository.WeeklyQuestCoordinator
import fr.jsisie.urbinema.domain.badge.BadgeRegistry
import fr.jsisie.urbinema.domain.collection.CollectionProgressEngine
import fr.jsisie.urbinema.domain.quest.DefaultQuestRules
import fr.jsisie.urbinema.domain.quest.QuestEngine
import fr.jsisie.urbinema.domain.rank.CatalogRankStatsEngine
import fr.jsisie.urbinema.domain.rank.RankDefaults
import fr.jsisie.urbinema.domain.rank.RankEngine
import fr.jsisie.urbinema.domain.xp.XpEngine
import org.koin.android.ext.koin.androidContext
import org.koin.core.module.dsl.viewModelOf
import org.koin.core.module.Module
import org.koin.dsl.module

private val applicationModule = module {
    single { UrbinemaDatabase.build(androidContext()) }
    single { CatalogImporter(get()) }
    single { CatalogRepository(get()) }
    single { ProgressRepository(get(), get()) }
    single { PreferencesRepository(androidContext()) }
    single { AppBootstrapper(androidContext(), get(), get()) }

    single { XpEngine() }
    single { RankEngine(RankDefaults.parameters) }
    single { CatalogRankStatsEngine() }
    single { BadgeRegistry.initial() }
    single { CollectionProgressEngine() }
    single { DefaultQuestRules.registry() }
    single { QuestEngine(get()) }
    single { WeeklyQuestCoordinator(get(), get(), get(), get(), get()) }
    single { ProgressionCoordinator(get(), get(), get(), get(), get()) }

    viewModelOf(::MainViewModel)
}

/** Modules loaded once by [fr.jsisie.urbinema.UrbinemaApplication]. */
val urbinemaModules: List<Module> = listOf(applicationModule)
