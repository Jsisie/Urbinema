package fr.jsisie.urbinema

import android.app.Application
import fr.jsisie.urbinema.app.di.urbinemaModules
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin

/**
 * Process entry point.
 *
 * Dependency construction is centralized in Koin so activities and
 * Composables never instantiate infrastructure directly.
 */
class UrbinemaApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@UrbinemaApplication)
            modules(urbinemaModules)
        }
    }
}
