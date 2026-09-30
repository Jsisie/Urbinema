package fr.jsisie.urbinema.app.startup

import android.content.Context
import android.util.Log
import fr.jsisie.urbinema.data.db.RankEngineConfigEntity
import fr.jsisie.urbinema.data.db.RankThresholdEntity
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import fr.jsisie.urbinema.data.importer.CatalogImportResult
import fr.jsisie.urbinema.data.importer.CatalogImporter
import fr.jsisie.urbinema.domain.model.TerritoryDimension
import fr.jsisie.urbinema.domain.rank.RankDefaults
import java.time.Clock
import java.time.Instant
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Idempotently prepares the local-first application on its first launch.
 *
 * Catalogue import and rank configuration are kept outside Activity/Compose
 * lifecycle code. The local profile is created by the onboarding screen.
 */
class AppBootstrapper(
    private val context: Context,
    private val database: UrbinemaDatabase,
    private val importer: CatalogImporter,
    private val clock: Clock = Clock.systemUTC(),
) {
    private val mutex = Mutex()

    /** Returns true when Room already has a catalogue version after the import attempt. */
    suspend fun initialize(): Boolean = mutex.withLock {
        val rankDao = database.rankConfigDao()
        try {
            val json = context.assets.open(CATALOG_ASSET).bufferedReader().use { it.readText() }
            when (val result = importer.importJson(json)) {
                is CatalogImportResult.Success -> Unit
                is CatalogImportResult.Invalid -> {
                    val detail = result.errors.joinToString { "${it.path}: ${it.message}" }
                    Log.e(TAG, "Catalogue invalid: $detail")
                }
                is CatalogImportResult.Failure -> {
                    Log.e(TAG, "Catalogue import failed: ${result.message}", result.cause)
                }
            }

            if (rankDao.latestCatalogVersion() != null &&
                rankDao.activeRankConfig()?.code != RankDefaults.CONFIG_CODE
            ) {
                activateDefaultRankConfiguration()
            }
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            Log.e(TAG, "Bootstrap failed", error)
        }
        rankDao.latestCatalogVersion() != null
    }

    private suspend fun activateDefaultRankConfiguration() {
        val parameters = RankDefaults.parameters
        val shares = parameters.dimensionShares
        val rankDao = database.rankConfigDao()
        rankDao.deactivateRankConfigs()
        rankDao.rankConfigByCode(RankDefaults.CONFIG_CODE)?.let { existing ->
            rankDao.activateRankConfig(existing.rankEngineConfigId)
            return
        }
        val configId = rankDao.insertRankConfig(
            RankEngineConfigEntity(
                code = RankDefaults.CONFIG_CODE,
                volumeLambda = parameters.volumeLambda,
                diversityLambda = parameters.diversityLambda,
                depthLambda = parameters.depthLambda,
                attenuationExponent = parameters.movieWeights.attenuationExponent,
                characteristicShare = shares.getValue(TerritoryDimension.CINEMA_CHARACTERISTIC),
                directorShare = shares.getValue(TerritoryDimension.DIRECTOR),
                countryShare = shares.getValue(TerritoryDimension.COUNTRY),
                decadeShare = shares.getValue(TerritoryDimension.DECADE),
                continentShare = shares.getValue(TerritoryDimension.CONTINENT),
                eraShare = shares.getValue(TerritoryDimension.ERA),
                genreShare = shares.getValue(TerritoryDimension.GENRE),
                formShare = shares.getValue(TerritoryDimension.FORM),
                isActive = true,
                createdAt = Instant.now(clock),
            )
        )
        rankDao.insertRankThresholds(
            RankDefaults.thresholds.mapIndexed { index, score ->
                RankThresholdEntity(
                    rankEngineConfigId = configId,
                    rankOrder = index + 2,
                    minimumScore = score,
                )
            }
        )
    }

    private companion object {
        const val CATALOG_ASSET = "catalog/catalog.json"
        const val TAG = "UrbinemaBootstrap"
    }
}
