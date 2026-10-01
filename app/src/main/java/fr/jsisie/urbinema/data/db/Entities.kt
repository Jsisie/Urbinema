package fr.jsisie.urbinema.data.db

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import java.time.Instant
import java.time.LocalDate

private const val RESTRICT = ForeignKey.RESTRICT
private const val CASCADE = ForeignKey.CASCADE
private const val SET_NULL = ForeignKey.SET_NULL

/** A local image or other packaged/private media. */
@Entity(tableName = "media_assets", indices = [Index("code", unique = true)])
data class MediaAssetEntity(
    @PrimaryKey(autoGenerate = true) val mediaAssetId: Long = 0,
    val code: String,
    val storageType: MediaStorageType,
    val path: String,
    val contentDescriptionKey: String? = null,
    val mimeType: String? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "movies",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["posterMediaId"], SET_NULL)],
    indices = [
        Index("code", unique = true), Index("originalTitle"), Index("frenchTitle"),
        Index("releaseYear"), Index("posterMediaId"),
    ],
)
data class MovieEntity(
    @PrimaryKey(autoGenerate = true) val movieId: Long = 0,
    val code: String,
    val originalTitle: String,
    val frenchTitle: String? = null,
    val releaseYear: Int,
    val durationMinutes: Int,
    val format: MovieFormat,
    val synopsis: String? = null,
    val posterMediaId: Long? = null,
    val historicalDistance: Double,
    val artisticDemand: Double,
    val historicalRichness: Double,
    val culturalRichness: Double,
    val isSilent: Boolean = false,
    val isBlackAndWhite: Boolean = false,
    val isExperimental: Boolean = false,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "countries",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("isoCode"), Index("imageMediaId")],
)
data class CountryEntity(
    @PrimaryKey(autoGenerate = true) val countryId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val isoCode: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "continents",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("imageMediaId")],
)
data class ContinentEntity(
    @PrimaryKey(autoGenerate = true) val continentId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "countries_continents",
    primaryKeys = ["countryId", "continentId"],
    foreignKeys = [
        ForeignKey(CountryEntity::class, ["countryId"], ["countryId"], RESTRICT),
        ForeignKey(ContinentEntity::class, ["continentId"], ["continentId"], RESTRICT),
    ],
    indices = [Index("continentId")],
)
data class CountryContinentCrossRef(val countryId: Long, val continentId: Long)

@Entity(
    tableName = "movies_countries",
    primaryKeys = ["movieId", "countryId"],
    foreignKeys = [
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
        ForeignKey(CountryEntity::class, ["countryId"], ["countryId"], RESTRICT),
    ],
    indices = [Index("countryId")],
)
data class MovieCountryCrossRef(val movieId: Long, val countryId: Long, val isPrimary: Boolean)

@Entity(
    tableName = "directors",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["portraitMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("portraitMediaId")],
)
data class DirectorEntity(
    @PrimaryKey(autoGenerate = true) val directorId: Long = 0,
    val code: String,
    val firstName: String? = null,
    val lastName: String,
    val displayName: String,
    val portraitMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
    val biography: String? = null,
    val biographyEn: String? = null,
)

@Entity(
    tableName = "movies_directors",
    primaryKeys = ["movieId", "directorId"],
    foreignKeys = [
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
        ForeignKey(DirectorEntity::class, ["directorId"], ["directorId"], RESTRICT),
    ],
    indices = [Index("directorId"), Index(value = ["movieId", "billingOrder"], unique = true)],
)
data class MovieDirectorCrossRef(val movieId: Long, val directorId: Long, val billingOrder: Int)

@Entity(tableName = "characteristic_types")
data class CharacteristicTypeEntity(
    @PrimaryKey val typeCode: String,
    val name: String,
)

@Entity(
    tableName = "cinema_characteristics",
    foreignKeys = [
        ForeignKey(CharacteristicTypeEntity::class, ["typeCode"], ["typeCode"], RESTRICT),
        ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL),
    ],
    indices = [Index("code", unique = true), Index("typeCode"), Index("imageMediaId")],
)
data class CinemaCharacteristicEntity(
    @PrimaryKey(autoGenerate = true) val characteristicId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val typeCode: String,
    val description: String? = null,
    val descriptionEn: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "directors_characteristics",
    primaryKeys = ["directorId", "characteristicId"],
    foreignKeys = [
        ForeignKey(DirectorEntity::class, ["directorId"], ["directorId"], RESTRICT),
        ForeignKey(CinemaCharacteristicEntity::class, ["characteristicId"], ["characteristicId"], RESTRICT),
    ],
    indices = [Index("characteristicId")],
)
data class DirectorCharacteristicCrossRef(val directorId: Long, val characteristicId: Long)

@Entity(
    tableName = "movies_characteristics",
    primaryKeys = ["movieId", "characteristicId"],
    foreignKeys = [
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
        ForeignKey(CinemaCharacteristicEntity::class, ["characteristicId"], ["characteristicId"], RESTRICT),
    ],
    indices = [Index("characteristicId")],
)
data class MovieCharacteristicCrossRef(val movieId: Long, val characteristicId: Long)

@Entity(
    tableName = "genres",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("imageMediaId")],
)
data class GenreEntity(
    @PrimaryKey(autoGenerate = true) val genreId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val description: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "movies_genres",
    primaryKeys = ["movieId", "genreId"],
    foreignKeys = [
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
        ForeignKey(GenreEntity::class, ["genreId"], ["genreId"], RESTRICT),
    ],
    indices = [Index("genreId")],
)
data class MovieGenreCrossRef(val movieId: Long, val genreId: Long)

@Entity(
    tableName = "eras",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("imageMediaId")],
)
data class EraEntity(
    @PrimaryKey(autoGenerate = true) val eraId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val startYear: Int,
    val endYear: Int,
    val description: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "collections",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["coverMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("displayOrder", unique = true), Index("coverMediaId")],
)
data class CollectionEntity(
    @PrimaryKey(autoGenerate = true) val collectionId: Long = 0,
    val code: String,
    val displayOrder: Int,
    val name: String,
    val nameEn: String? = null,
    val description: String? = null,
    val descriptionEn: String? = null,
    val longDescription: String? = null,
    val longDescriptionEn: String? = null,
    val coverMediaId: Long? = null,
    val isPublished: Boolean = false,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
    val track: String = "JOURNEY",
)

@Entity(
    tableName = "collections_movies",
    primaryKeys = ["collectionId", "movieId"],
    foreignKeys = [
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
    ],
    indices = [Index("movieId"), Index(value = ["collectionId", "displayOrder"], unique = true)],
)
data class CollectionMovieCrossRef(val collectionId: Long, val movieId: Long, val displayOrder: Int)

@Entity(
    tableName = "collections_characteristics",
    primaryKeys = ["collectionId", "characteristicId"],
    foreignKeys = [
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
        ForeignKey(CinemaCharacteristicEntity::class, ["characteristicId"], ["characteristicId"], RESTRICT),
    ],
    indices = [Index("characteristicId")],
)
data class CollectionCharacteristicCrossRef(val collectionId: Long, val characteristicId: Long)

@Entity(
    tableName = "collections_countries",
    primaryKeys = ["collectionId", "countryId"],
    foreignKeys = [
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
        ForeignKey(CountryEntity::class, ["countryId"], ["countryId"], RESTRICT),
    ],
    indices = [Index("countryId")],
)
data class CollectionCountryCrossRef(val collectionId: Long, val countryId: Long)

@Entity(
    tableName = "collections_continents",
    primaryKeys = ["collectionId", "continentId"],
    foreignKeys = [
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
        ForeignKey(ContinentEntity::class, ["continentId"], ["continentId"], RESTRICT),
    ],
    indices = [Index("continentId")],
)
data class CollectionContinentCrossRef(val collectionId: Long, val continentId: Long)

@Entity(
    tableName = "collections_eras",
    primaryKeys = ["collectionId", "eraId"],
    foreignKeys = [
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
        ForeignKey(EraEntity::class, ["eraId"], ["eraId"], RESTRICT),
    ],
    indices = [Index("eraId")],
)
data class CollectionEraCrossRef(val collectionId: Long, val eraId: Long)

/** A pedagogical path through cinema currents. Edited in the catalog `paths` array. */
@Entity(
    tableName = "learning_paths",
    indices = [Index("code", unique = true), Index("displayOrder", unique = true)],
)
data class LearningPathEntity(
    @PrimaryKey(autoGenerate = true) val pathId: Long = 0,
    val code: String,
    val displayOrder: Int,
    val name: String,
    val nameEn: String? = null,
    val summary: String,
    val summaryEn: String? = null,
    val description: String,
    val descriptionEn: String? = null,
    val periodLabel: String,
    val periodLabelEn: String? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

/** One current bubble on a path. `transitionText` leads to the next bubble. */
@Entity(
    tableName = "learning_path_steps",
    foreignKeys = [
        ForeignKey(LearningPathEntity::class, ["pathId"], ["pathId"], CASCADE),
        ForeignKey(CinemaCharacteristicEntity::class, ["characteristicId"], ["characteristicId"], RESTRICT),
    ],
    indices = [
        Index("code", unique = true),
        Index("pathId"),
        Index("characteristicId"),
        Index(value = ["pathId", "position"], unique = true),
    ],
)
data class LearningPathStepEntity(
    @PrimaryKey(autoGenerate = true) val stepId: Long = 0,
    val code: String,
    val pathId: Long,
    val position: Int,
    val characteristicId: Long,
    val name: String,
    val nameEn: String? = null,
    val periodLabel: String,
    val periodLabelEn: String? = null,
    val description: String,
    val descriptionEn: String? = null,
    val transitionText: String? = null,
    val transitionTextEn: String? = null,
    val isActive: Boolean = true,
)

/** Short "À savoir" note under a path step. */
@Entity(
    tableName = "learning_path_facts",
    foreignKeys = [ForeignKey(LearningPathStepEntity::class, ["stepId"], ["stepId"], CASCADE)],
    indices = [Index("stepId"), Index(value = ["stepId", "position"], unique = true)],
)
data class LearningPathFactEntity(
    @PrimaryKey(autoGenerate = true) val factId: Long = 0,
    val stepId: Long,
    val position: Int,
    val title: String,
    val titleEn: String? = null,
    val body: String,
    val bodyEn: String? = null,
)

/** A key person on a path step. `directorId` is set when a director fiche exists. */
@Entity(
    tableName = "learning_path_figures",
    foreignKeys = [
        ForeignKey(LearningPathStepEntity::class, ["stepId"], ["stepId"], CASCADE),
        ForeignKey(DirectorEntity::class, ["directorId"], ["directorId"], SET_NULL),
    ],
    indices = [Index("stepId"), Index("directorId"), Index(value = ["stepId", "position"], unique = true)],
)
data class LearningPathFigureEntity(
    @PrimaryKey(autoGenerate = true) val figureId: Long = 0,
    val stepId: Long,
    val position: Int,
    val displayName: String,
    val role: String,
    val roleEn: String? = null,
    val directorId: Long? = null,
)

@Entity(
    tableName = "learning_path_movies",
    primaryKeys = ["stepId", "movieId"],
    foreignKeys = [
        ForeignKey(LearningPathStepEntity::class, ["stepId"], ["stepId"], CASCADE),
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
    ],
    indices = [Index("movieId"), Index(value = ["stepId", "position"], unique = true)],
)
data class LearningPathMovieCrossRef(val stepId: Long, val movieId: Long, val position: Int)

@Entity(
    tableName = "rankings",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["imageMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("displayOrder", unique = true), Index("imageMediaId")],
)
data class RankingEntity(
    @PrimaryKey(autoGenerate = true) val rankingId: Long = 0,
    val code: String,
    val displayOrder: Int,
    val name: String,
    val nameEn: String? = null,
    val description: String,
    val descriptionEn: String? = null,
    val longDescription: String? = null,
    val longDescriptionEn: String? = null,
    val imageMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "badges",
    foreignKeys = [ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["iconMediaId"], SET_NULL)],
    indices = [Index("code", unique = true), Index("iconMediaId")],
)
data class BadgeEntity(
    @PrimaryKey(autoGenerate = true) val badgeId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val description: String,
    val descriptionEn: String? = null,
    val difficulty: Int,
    val category: String,
    val iconMediaId: Long? = null,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(tableName = "quests", indices = [Index("code", unique = true), Index("ruleCode")])
data class QuestEntity(
    @PrimaryKey(autoGenerate = true) val questId: Long = 0,
    val code: String,
    val name: String,
    val nameEn: String? = null,
    val description: String,
    val descriptionEn: String? = null,
    val difficulty: QuestDifficulty,
    val ruleCode: String,
    val targetCount: Int,
    val isActive: Boolean = true,
    val createdAt: Instant,
    val updatedAt: Instant,
)

@Entity(
    tableName = "users",
    foreignKeys = [
        ForeignKey(CountryEntity::class, ["countryId"], ["countryId"], RESTRICT),
        ForeignKey(MediaAssetEntity::class, ["mediaAssetId"], ["avatarMediaId"], SET_NULL),
        ForeignKey(RankingEntity::class, ["rankingId"], ["rankingId"], RESTRICT),
    ],
    indices = [Index("username", unique = true), Index("countryId"), Index("avatarMediaId"), Index("rankingId")],
)
data class UserEntity(
    @PrimaryKey(autoGenerate = true) val userId: Long = 0,
    val email: String? = null,
    val username: String,
    val firstName: String? = null,
    val lastName: String? = null,
    val birthDate: LocalDate? = null,
    val countryId: Long? = null,
    val avatarMediaId: Long? = null,
    val avatarCode: String? = null,
    val rankingId: Long,
    val maxLevelReached: Int = 1,
    val unlockedTrackOrdinal: Int = -1,
    val showcaseBadgeCodes: String? = null,
    val createdAt: Instant,
)

@Entity(
    tableName = "user_movies",
    primaryKeys = ["userId", "movieId"],
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
    ],
    indices = [Index("movieId"), Index(value = ["userId", "watchedOn"])],
)
data class UserMovieCrossRef(
    val userId: Long,
    val movieId: Long,
    val watchedOn: LocalDate,
    val validatedAt: Instant,
)

@Entity(
    tableName = "user_followed_collections",
    primaryKeys = ["userId", "collectionId"],
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
        ForeignKey(CollectionEntity::class, ["collectionId"], ["collectionId"], RESTRICT),
    ],
    indices = [Index("collectionId")],
)
data class UserFollowedCollectionCrossRef(
    val userId: Long,
    val collectionId: Long,
    val followedAt: Instant,
)

@Entity(
    tableName = "user_badges",
    primaryKeys = ["userId", "badgeId"],
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
        ForeignKey(BadgeEntity::class, ["badgeId"], ["badgeId"], RESTRICT),
    ],
    indices = [Index("badgeId")],
)
data class UserBadgeCrossRef(val userId: Long, val badgeId: Long, val earnedAt: Instant)

@Entity(
    tableName = "user_quests",
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
        ForeignKey(QuestEntity::class, ["questId"], ["questId"], RESTRICT),
    ],
    indices = [
        Index("questId"),
        Index(value = ["userId", "startsAt", "expiresAt", "status"]),
        Index(value = ["userId", "questId", "startsAt"], unique = true),
    ],
)
data class UserQuestEntity(
    @PrimaryKey(autoGenerate = true) val userQuestId: Long = 0,
    val userId: Long,
    val questId: Long,
    val startsAt: Instant,
    val expiresAt: Instant,
    val progress: Int = 0,
    val targetCountSnapshot: Int,
    val xpRewardSnapshot: Int,
    val completedAt: Instant? = null,
    val status: UserQuestStatus = UserQuestStatus.ACTIVE,
)

@Entity(
    tableName = "xp_transactions",
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
        ForeignKey(UserQuestEntity::class, ["userQuestId"], ["userQuestId"], CASCADE),
        ForeignKey(MovieEntity::class, ["movieId"], ["movieId"], RESTRICT),
    ],
    indices = [
        Index("userId"),
        Index("userQuestId", unique = true),
        Index("movieId"),
        Index(value = ["userId", "movieId"], unique = true),
    ],
)
data class XpTransactionEntity(
    @PrimaryKey(autoGenerate = true) val xpTransactionId: Long = 0,
    val userId: Long,
    val userQuestId: Long? = null,
    val movieId: Long? = null,
    val source: String,
    val amount: Int,
    val earnedAt: Instant,
)

object XpSources {
    const val QUEST = "QUEST"
    const val FILM = "FILM"
}

@Entity(
    tableName = "activity_events",
    foreignKeys = [ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE)],
    indices = [Index(value = ["userId", "occurredAt"], orders = [Index.Order.ASC, Index.Order.DESC])],
)
data class ActivityEventEntity(
    @PrimaryKey(autoGenerate = true) val activityEventId: Long = 0,
    val userId: Long,
    val type: String,
    val occurredAt: Instant,
    val payloadJson: String,
)

/** One immutable editorial catalogue revision applied to the local database. */
@Entity(tableName = "catalog_versions", indices = [Index("version", unique = true)])
data class CatalogVersionEntity(
    @PrimaryKey(autoGenerate = true) val catalogVersionId: Long = 0,
    val version: Int,
    val generatedAt: Instant,
    val appliedAt: Instant,
    val movieCount: Int,
)

/** Persisted and editable coefficients used by the rank engine. */
@Entity(tableName = "rank_engine_configs", indices = [Index("code", unique = true)])
data class RankEngineConfigEntity(
    @PrimaryKey(autoGenerate = true) val rankEngineConfigId: Long = 0,
    val code: String,
    val volumeLambda: Double,
    val diversityLambda: Double,
    val depthLambda: Double,
    val attenuationExponent: Double,
    val characteristicShare: Double,
    val directorShare: Double,
    val countryShare: Double,
    val decadeShare: Double,
    val continentShare: Double,
    val eraShare: Double,
    val genreShare: Double,
    val formShare: Double,
    val isActive: Boolean,
    val createdAt: Instant,
)

/** One of the nine ordered score boundaries attached to a rank configuration. */
@Entity(
    tableName = "rank_thresholds",
    primaryKeys = ["rankEngineConfigId", "rankOrder"],
    foreignKeys = [
        ForeignKey(
            RankEngineConfigEntity::class,
            ["rankEngineConfigId"],
            ["rankEngineConfigId"],
            CASCADE,
        ),
    ],
)
data class RankThresholdEntity(
    val rankEngineConfigId: Long,
    val rankOrder: Int,
    val minimumScore: Double,
)

/**
 * Historical Q/w ratchets for one territory at one catalogue version.
 *
 * The domain recalculates current values; these rows ensure a later catalogue
 * expansion cannot dilute previously acquired diversity.
 */
@Entity(
    tableName = "catalog_dimension_stats",
    primaryKeys = ["catalogVersionId", "dimensionCode", "territoryCode"],
    foreignKeys = [
        ForeignKey(
            CatalogVersionEntity::class,
            ["catalogVersionId"],
            ["catalogVersionId"],
            RESTRICT,
        ),
    ],
    indices = [Index(value = ["dimensionCode", "territoryCode"])],
)
data class CatalogDimensionStatEntity(
    val catalogVersionId: Long,
    val dimensionCode: String,
    val territoryCode: String,
    val rarityReference: Double,
    val weightReference: Double,
)

/** Rebuildable projection of the latest calculation, never a source of truth. */
@Entity(
    tableName = "user_progress_state",
    foreignKeys = [
        ForeignKey(UserEntity::class, ["userId"], ["userId"], CASCADE),
    ],
)
data class UserProgressStateEntity(
    @PrimaryKey val userId: Long,
    val weightedVolume: Double,
    val diversity: Double,
    val depth: Double,
    val score: Double,
    val rawRankOrder: Int,
    val recalculatedAt: Instant,
)
