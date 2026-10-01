package fr.jsisie.urbinema.data.importer

import androidx.room.withTransaction
import fr.jsisie.urbinema.data.db.BadgeEntity
import fr.jsisie.urbinema.data.db.CatalogVersionEntity
import fr.jsisie.urbinema.data.db.CinemaCharacteristicEntity
import fr.jsisie.urbinema.data.db.CollectionCharacteristicCrossRef
import fr.jsisie.urbinema.data.db.CollectionContinentCrossRef
import fr.jsisie.urbinema.data.db.CollectionCountryCrossRef
import fr.jsisie.urbinema.data.db.CollectionEntity
import fr.jsisie.urbinema.data.db.CollectionEraCrossRef
import fr.jsisie.urbinema.data.db.CollectionMovieCrossRef
import fr.jsisie.urbinema.data.db.ContinentEntity
import fr.jsisie.urbinema.data.db.CountryContinentCrossRef
import fr.jsisie.urbinema.data.db.CountryEntity
import fr.jsisie.urbinema.data.db.DirectorCharacteristicCrossRef
import fr.jsisie.urbinema.data.db.DirectorEntity
import fr.jsisie.urbinema.data.db.EraEntity
import fr.jsisie.urbinema.data.db.GenreEntity
import fr.jsisie.urbinema.data.db.LearningPathEntity
import fr.jsisie.urbinema.data.db.LearningPathFactEntity
import fr.jsisie.urbinema.data.db.LearningPathFigureEntity
import fr.jsisie.urbinema.data.db.LearningPathMovieCrossRef
import fr.jsisie.urbinema.data.db.LearningPathStepEntity
import fr.jsisie.urbinema.data.db.MediaAssetEntity
import fr.jsisie.urbinema.data.db.MediaStorageType
import fr.jsisie.urbinema.data.db.MovieCharacteristicCrossRef
import fr.jsisie.urbinema.data.db.MovieCountryCrossRef
import fr.jsisie.urbinema.data.db.MovieDirectorCrossRef
import fr.jsisie.urbinema.data.db.MovieEntity
import fr.jsisie.urbinema.data.db.MovieFormat
import fr.jsisie.urbinema.data.db.MovieGenreCrossRef
import fr.jsisie.urbinema.data.db.QuestDifficulty
import fr.jsisie.urbinema.data.db.QuestEntity
import fr.jsisie.urbinema.data.db.RankingEntity
import fr.jsisie.urbinema.data.db.CharacteristicTypeEntity
import fr.jsisie.urbinema.data.db.UrbinemaDatabase
import java.time.Clock
import java.time.Instant
import kotlinx.coroutines.CancellationException
import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.Json

sealed interface CatalogImportResult {
    data class Success(val version: Int) : CatalogImportResult
    data class Invalid(val errors: List<CatalogValidationError>) : CatalogImportResult
    data class Failure(val message: String, val cause: Throwable? = null) : CatalogImportResult
}

/**
 * Converts a validated JSON pack into Room.
 *
 * First install writes a fresh catalogue. Later APKs with a higher pack version
 * upsert editorial rows by stable code and never touch user_* tables.
 */
class CatalogImporter(
    private val database: UrbinemaDatabase,
    private val validator: CatalogValidator = CatalogValidator(),
    private val json: Json = Json {
        explicitNulls = false
        ignoreUnknownKeys = true
    },
    private val clock: Clock = Clock.systemUTC(),
) {
    /** Decodes and imports a pack; malformed JSON and constraint failures are reported without partial writes. */
    suspend fun importJson(content: String): CatalogImportResult {
        val pack = try {
            json.decodeFromString<CatalogPack>(content)
        } catch (error: SerializationException) {
            return CatalogImportResult.Failure("Malformed catalogue JSON", error)
        } catch (error: IllegalArgumentException) {
            return CatalogImportResult.Failure("Malformed catalogue JSON", error)
        }
        return import(pack)
    }

    /** Validates all references first, then persists every table under a Room transaction. */
    suspend fun import(pack: CatalogPack): CatalogImportResult {
        val report = validator.validate(pack)
        if (!report.isValid) return CatalogImportResult.Invalid(report.errors)

        return try {
            database.withTransaction {
                val current = database.rankConfigDao().latestCatalogVersion()
                if (current != null && current.version >= pack.version) {
                    return@withTransaction
                }
                persist(pack)
            }
            CatalogImportResult.Success(pack.version)
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            CatalogImportResult.Failure(error.message ?: "Catalogue import failed", error)
        }
    }

    private suspend fun <T> insertAll(values: List<T>, insert: suspend (List<T>) -> Unit) {
        if (values.isEmpty()) return
        values.chunked(INSERT_CHUNK).forEach { insert(it) }
    }

    /**
     * Upserts editorial rows by stable code. Cross-tables are cleared first so
     * a film leaving a collection actually leaves it. User_* tables are never
     * written here. Display orders are parked then restored to keep uniqueness
     * while rows move around.
     */
    private suspend fun persist(pack: CatalogPack) {
        val dao = database.catalogImportDao()
        val timestamp = Instant.parse(pack.generatedAt)
        remapRetiredMovies(pack.movieAliases)
        dao.parkCollectionDisplayOrders()
        dao.parkRankingDisplayOrders()
        dao.parkLearningPathDisplayOrders()
        dao.parkLearningPathStepPositions()
        dao.clearCountriesContinents()
        dao.clearDirectorsCharacteristics()
        dao.clearMoviesCountries()
        dao.clearMoviesDirectors()
        dao.clearMoviesGenres()
        dao.clearMoviesCharacteristics()
        dao.clearCollectionsMovies()
        dao.clearCollectionsCharacteristics()
        dao.clearCollectionsCountries()
        dao.clearCollectionsContinents()
        dao.clearCollectionsEras()
        dao.clearLearningPathMovies()
        dao.clearLearningPathFacts()
        dao.clearLearningPathFigures()

        val mediaIds = pack.mediaAssets.associate { value ->
            value.code to upsertMedia(
                MediaAssetEntity(
                    code = value.code,
                    storageType = MediaStorageType.valueOf(value.storageType),
                    path = value.path,
                    contentDescriptionKey = value.contentDescriptionKey,
                    mimeType = value.mimeType,
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        pack.characteristicTypes.forEach {
            dao.insertCharacteristicType(CharacteristicTypeEntity(it.typeCode, it.name))
        }
        val continentIds = pack.continents.associate { value ->
            value.code to upsertContinent(
                ContinentEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val countryIds = pack.countries.associate { value ->
            value.code to upsertCountry(
                CountryEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    isoCode = value.isoCode,
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val directorIds = pack.directors.associate { value ->
            value.code to upsertDirector(
                DirectorEntity(
                    code = value.code,
                    firstName = value.firstName,
                    lastName = value.lastName,
                    displayName = value.displayName,
                    biography = value.biography?.takeIf { it.isNotBlank() },
                    biographyEn = value.biographyEn?.takeIf { it.isNotBlank() },
                    portraitMediaId = value.portraitMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val characteristicIds = pack.characteristics.associate { value ->
            value.code to upsertCharacteristic(
                CinemaCharacteristicEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    typeCode = value.typeCode,
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val genreIds = pack.genres.associate { value ->
            value.code to upsertGenre(
                GenreEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    description = value.description,
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val eraIds = pack.eras.associate { value ->
            value.code to upsertEra(
                EraEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    startYear = value.startYear,
                    endYear = value.endYear,
                    description = value.description,
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val movieIds = pack.movies.associate { value ->
            value.code to upsertMovie(
                MovieEntity(
                    code = value.code,
                    originalTitle = value.originalTitle,
                    frenchTitle = value.frenchTitle,
                    releaseYear = value.releaseYear,
                    durationMinutes = value.durationMinutes,
                    format = MovieFormat.valueOf(value.format),
                    synopsis = value.synopsis,
                    posterMediaId = value.posterMediaCode.idIn(mediaIds),
                    historicalDistance = value.historicalDistance,
                    artisticDemand = value.artisticDemand,
                    historicalRichness = value.historicalRichness,
                    culturalRichness = value.culturalRichness,
                    isSilent = value.isSilent,
                    isBlackAndWhite = value.isBlackAndWhite,
                    isExperimental = value.isExperimental,
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }

        insertAll(pack.countries.flatMap { country ->
            country.continentCodes.map { CountryContinentCrossRef(countryIds.id(country.code), continentIds.id(it)) }
        }, dao::insertCountriesContinents)
        insertAll(pack.directors.flatMap { director ->
            director.characteristicCodes.map {
                DirectorCharacteristicCrossRef(directorIds.id(director.code), characteristicIds.id(it))
            }
        }, dao::insertDirectorsCharacteristics)
        insertAll(pack.movies.flatMap { movie ->
            movie.countries.map {
                MovieCountryCrossRef(movieIds.id(movie.code), countryIds.id(it.code), it.isPrimary)
            }
        }, dao::insertMoviesCountries)
        insertAll(pack.movies.flatMap { movie ->
            movie.directors.map {
                MovieDirectorCrossRef(movieIds.id(movie.code), directorIds.id(it.code), it.billingOrder)
            }
        }, dao::insertMoviesDirectors)
        insertAll(pack.movies.flatMap { movie ->
            movie.genreCodes.map { MovieGenreCrossRef(movieIds.id(movie.code), genreIds.id(it)) }
        }, dao::insertMoviesGenres)
        insertAll(pack.movies.flatMap { movie ->
            movie.characteristicCodes.map {
                MovieCharacteristicCrossRef(movieIds.id(movie.code), characteristicIds.id(it))
            }
        }, dao::insertMoviesCharacteristics)

        val collectionIds = pack.collections.associate { value ->
            value.code to upsertCollection(
                CollectionEntity(
                    code = value.code,
                    displayOrder = value.displayOrder,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    longDescription = value.longDescription,
                    longDescriptionEn = value.longDescriptionEn.blankToNull(),
                    track = value.track,
                    coverMediaId = value.coverMediaCode.idIn(mediaIds),
                    isPublished = value.isPublished,
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        insertAll(pack.collections.flatMap { collection ->
            collection.movies.map {
                CollectionMovieCrossRef(collectionIds.id(collection.code), movieIds.id(it.code), it.displayOrder)
            }
        }, dao::insertCollectionsMovies)
        insertAll(pack.collections.flatMap { collection ->
            collection.characteristicCodes.map {
                CollectionCharacteristicCrossRef(collectionIds.id(collection.code), characteristicIds.id(it))
            }
        }, dao::insertCollectionsCharacteristics)
        insertAll(pack.collections.flatMap { collection ->
            collection.countryCodes.map {
                CollectionCountryCrossRef(collectionIds.id(collection.code), countryIds.id(it))
            }
        }, dao::insertCollectionsCountries)
        insertAll(pack.collections.flatMap { collection ->
            collection.continentCodes.map {
                CollectionContinentCrossRef(collectionIds.id(collection.code), continentIds.id(it))
            }
        }, dao::insertCollectionsContinents)
        insertAll(pack.collections.flatMap { collection ->
            collection.eraCodes.map {
                CollectionEraCrossRef(collectionIds.id(collection.code), eraIds.id(it))
            }
        }, dao::insertCollectionsEras)

        pack.rankings.forEach { value ->
            upsertRanking(
                RankingEntity(
                    code = value.code,
                    displayOrder = value.displayOrder,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    longDescription = value.longDescription,
                    longDescriptionEn = value.longDescriptionEn.blankToNull(),
                    imageMediaId = value.imageMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        pack.badges.forEach { value ->
            upsertBadge(
                BadgeEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    difficulty = value.difficulty,
                    category = value.category,
                    iconMediaId = value.iconMediaCode.idIn(mediaIds),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        pack.quests.forEach { value ->
            upsertQuest(
                QuestEntity(
                    code = value.code,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    difficulty = QuestDifficulty.valueOf(value.difficulty),
                    ruleCode = value.ruleCode,
                    targetCount = value.targetCount,
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val pathIds = pack.paths.associate { value ->
            value.code to upsertLearningPath(
                LearningPathEntity(
                    code = value.code,
                    displayOrder = value.displayOrder,
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    summary = value.summary,
                    summaryEn = value.summaryEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    periodLabel = value.periodLabel,
                    periodLabelEn = value.periodLabelEn.blankToNull(),
                    isActive = value.isActive,
                    createdAt = timestamp,
                    updatedAt = timestamp,
                )
            )
        }
        val stepIds = pack.paths.flatMap { path ->
            path.steps.map { step -> path.code to step }
        }.associate { (pathCode, value) ->
            value.code to upsertLearningPathStep(
                LearningPathStepEntity(
                    code = value.code,
                    pathId = pathIds.id(pathCode),
                    position = value.position,
                    characteristicId = characteristicIds.id(value.characteristicCode),
                    name = value.name,
                    nameEn = value.nameEn.blankToNull(),
                    periodLabel = value.periodLabel,
                    periodLabelEn = value.periodLabelEn.blankToNull(),
                    description = value.description,
                    descriptionEn = value.descriptionEn.blankToNull(),
                    transitionText = value.transition,
                    transitionTextEn = value.transitionEn.blankToNull(),
                    isActive = value.isActive,
                )
            )
        }
        insertAll(pack.paths.flatMap { path ->
            path.steps.flatMap { step ->
                step.facts.mapIndexed { index, fact ->
                    LearningPathFactEntity(
                        stepId = stepIds.id(step.code),
                        position = index,
                        title = fact.title,
                        titleEn = fact.titleEn.blankToNull(),
                        body = fact.body,
                        bodyEn = fact.bodyEn.blankToNull(),
                    )
                }
            }
        }, dao::insertLearningPathFacts)
        insertAll(pack.paths.flatMap { path ->
            path.steps.flatMap { step ->
                step.figures.mapIndexed { index, figure ->
                    LearningPathFigureEntity(
                        stepId = stepIds.id(step.code),
                        position = index,
                        displayName = figure.displayName,
                        role = figure.role,
                        roleEn = figure.roleEn.blankToNull(),
                        directorId = figure.directorCode.idIn(directorIds),
                    )
                }
            }
        }, dao::insertLearningPathFigures)
        insertAll(pack.paths.flatMap { path ->
            path.steps.flatMap { step ->
                step.movies.mapIndexed { index, code ->
                    LearningPathMovieCrossRef(stepIds.id(step.code), movieIds.id(code), index)
                }
            }
        }, dao::insertLearningPathMovies)
        val pathCodes = pack.paths.map { it.code }
        if (pathCodes.isNotEmpty()) dao.deactivateLearningPathsNotIn(pathCodes)
        val stepCodes = pack.paths.flatMap { path -> path.steps.map { it.code } }
        if (stepCodes.isNotEmpty()) dao.deactivateLearningPathStepsNotIn(stepCodes)

        val movieCodes = pack.movies.map { it.code }
        if (movieCodes.isNotEmpty()) dao.deactivateMoviesNotIn(movieCodes)
        val collectionCodes = pack.collections.map { it.code }
        if (collectionCodes.isNotEmpty()) dao.deactivateCollectionsNotIn(collectionCodes)
        val countryCodes = pack.countries.map { it.code }
        if (countryCodes.isNotEmpty()) dao.deactivateCountriesNotIn(countryCodes)
        dao.insertCatalogVersion(
            CatalogVersionEntity(
                version = pack.version,
                generatedAt = timestamp,
                appliedAt = Instant.now(clock),
                movieCount = pack.movies.size,
            )
        )
    }

    /**
     * A duplicate removed from the pack must not stay as the film the user marked
     * watched: that row would lose its countries on the next import and crash startup.
     */
    private suspend fun remapRetiredMovies(aliases: List<MovieAliasImport>) {
        val dao = database.catalogImportDao()
        for (alias in aliases) {
            val from = dao.movieByCode(alias.from) ?: continue
            val to = dao.movieByCode(alias.to) ?: continue
            if (from.movieId == to.movieId) continue
            dao.dropUserMoviesAlreadyOnTarget(from.movieId, to.movieId)
            dao.moveUserMovies(from.movieId, to.movieId)
            dao.dropXpAlreadyOnTarget(from.movieId, to.movieId)
            dao.moveXpMovies(from.movieId, to.movieId)
        }
    }

    private suspend fun upsertMedia(value: MediaAssetEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.mediaByCode(value.code) ?: return dao.insertMedia(value)
        dao.updateMedia(value.copy(mediaAssetId = existing.mediaAssetId, createdAt = existing.createdAt))
        return existing.mediaAssetId
    }

    private suspend fun upsertContinent(value: ContinentEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.continentByCode(value.code) ?: return dao.insertContinent(value)
        dao.updateContinent(value.copy(continentId = existing.continentId, createdAt = existing.createdAt))
        return existing.continentId
    }

    private suspend fun upsertCountry(value: CountryEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.countryByCode(value.code) ?: return dao.insertCountry(value)
        dao.updateCountry(value.copy(countryId = existing.countryId, createdAt = existing.createdAt))
        return existing.countryId
    }

    private suspend fun upsertDirector(value: DirectorEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.directorByCode(value.code) ?: return dao.insertDirector(value)
        dao.updateDirector(value.copy(directorId = existing.directorId, createdAt = existing.createdAt))
        return existing.directorId
    }

    private suspend fun upsertCharacteristic(value: CinemaCharacteristicEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.characteristicByCode(value.code) ?: return dao.insertCharacteristic(value)
        dao.updateCharacteristic(value.copy(characteristicId = existing.characteristicId, createdAt = existing.createdAt))
        return existing.characteristicId
    }

    private suspend fun upsertGenre(value: GenreEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.genreByCode(value.code) ?: return dao.insertGenre(value)
        dao.updateGenre(value.copy(genreId = existing.genreId, createdAt = existing.createdAt))
        return existing.genreId
    }

    private suspend fun upsertEra(value: EraEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.eraByCode(value.code) ?: return dao.insertEra(value)
        dao.updateEra(value.copy(eraId = existing.eraId, createdAt = existing.createdAt))
        return existing.eraId
    }

    private suspend fun upsertMovie(value: MovieEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.movieByCode(value.code) ?: return dao.insertMovie(value)
        dao.updateMovie(value.copy(movieId = existing.movieId, createdAt = existing.createdAt))
        return existing.movieId
    }

    private suspend fun upsertCollection(value: CollectionEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.collectionByCode(value.code) ?: return dao.insertCollection(value)
        dao.updateCollection(value.copy(collectionId = existing.collectionId, createdAt = existing.createdAt))
        return existing.collectionId
    }

    private suspend fun upsertLearningPath(value: LearningPathEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.learningPathByCode(value.code) ?: return dao.insertLearningPath(value)
        dao.updateLearningPath(value.copy(pathId = existing.pathId, createdAt = existing.createdAt))
        return existing.pathId
    }

    private suspend fun upsertLearningPathStep(value: LearningPathStepEntity): Long {
        val dao = database.catalogImportDao()
        val existing = dao.learningPathStepByCode(value.code) ?: return dao.insertLearningPathStep(value)
        dao.updateLearningPathStep(value.copy(stepId = existing.stepId))
        return existing.stepId
    }

    private suspend fun upsertRanking(value: RankingEntity) {
        val dao = database.catalogImportDao()
        val existing = dao.rankingByCode(value.code)
        if (existing == null) dao.insertRanking(value)
        else dao.updateRanking(value.copy(rankingId = existing.rankingId, createdAt = existing.createdAt))
    }

    private suspend fun upsertBadge(value: BadgeEntity) {
        val dao = database.catalogImportDao()
        val existing = dao.badgeByCode(value.code)
        if (existing == null) dao.insertBadge(value)
        else dao.updateBadge(value.copy(badgeId = existing.badgeId, createdAt = existing.createdAt))
    }

    private suspend fun upsertQuest(value: QuestEntity) {
        val dao = database.catalogImportDao()
        val existing = dao.questByCode(value.code)
        if (existing == null) dao.insertQuest(value)
        else dao.updateQuest(value.copy(questId = existing.questId, createdAt = existing.createdAt))
    }

    private fun String?.blankToNull(): String? = this?.takeIf { it.isNotBlank() }

    private fun String?.idIn(ids: Map<String, Long>): Long? =
        this?.let { code -> ids.id(code) }
    private fun Map<String, Long>.id(code: String): Long =
        checkNotNull(this[code]) { "Validated reference disappeared: $code" }

    private companion object {
        const val INSERT_CHUNK = 100
    }
}
