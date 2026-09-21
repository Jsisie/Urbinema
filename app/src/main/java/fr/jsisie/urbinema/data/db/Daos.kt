package fr.jsisie.urbinema.data.db

import androidx.paging.PagingSource
import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Update
import kotlinx.coroutines.flow.Flow
import java.time.Instant
import java.time.LocalDate

@Dao
interface CatalogDao {
    /** Streams active movies for compact catalogue views. */
    @Query("SELECT * FROM movies WHERE isActive = 1 ORDER BY originalTitle")
    fun observeMovies(): Flow<List<MovieEntity>>

    /** Pages active movies without loading the growing catalogue in memory. */
    @Query("SELECT * FROM movies WHERE isActive = 1 ORDER BY originalTitle")
    fun pageMovies(): PagingSource<Int, MovieEntity>

    /** Finds a stable editorial movie code. */
    @Query("SELECT * FROM movies WHERE code = :code LIMIT 1")
    suspend fun movieByCode(code: String): MovieEntity?

    /** Loads a movie and all N-N detail relations atomically. */
    @Transaction
    @Query("SELECT * FROM movies WHERE movieId = :movieId")
    suspend fun movieWithRelations(movieId: Long): MovieWithRelations?

    @Transaction
    @Query("SELECT * FROM movies WHERE isActive = 1")
    suspend fun allMoviesWithRelations(): List<MovieWithRelations>

    @Query(
        """SELECT c.code FROM countries c
           INNER JOIN movies_countries mc ON mc.countryId = c.countryId
           WHERE mc.movieId = :movieId AND mc.isPrimary = 1 LIMIT 1"""
    )
    suspend fun primaryCountryCode(movieId: Long): String?

    @Query(
        """SELECT co.code FROM continents co
           INNER JOIN countries_continents cc ON cc.continentId = co.continentId
           INNER JOIN movies_countries mc ON mc.countryId = cc.countryId
           WHERE mc.movieId = :movieId AND mc.isPrimary = 1"""
    )
    suspend fun primaryContinentCodes(movieId: Long): List<String>

    @Query(
        """SELECT DISTINCT ch.code FROM cinema_characteristics ch
           INNER JOIN directors_characteristics dc
             ON dc.characteristicId = ch.characteristicId
           INNER JOIN movies_directors md ON md.directorId = dc.directorId
           WHERE md.movieId = :movieId"""
    )
    suspend fun directorCharacteristicCodes(movieId: Long): List<String>

    @Query(
        """SELECT code FROM eras
           WHERE :releaseYear BETWEEN startYear AND endYear AND isActive = 1
           ORDER BY (endYear - startYear), startYear LIMIT 1"""
    )
    suspend fun eraCodeForYear(releaseYear: Int): String?

    /** Lists collection movies in editorial order. */
    @Query(
        """SELECT m.* FROM movies m
           INNER JOIN collections_movies cm ON cm.movieId = m.movieId
           WHERE cm.collectionId = :collectionId AND m.isActive = 1
           ORDER BY cm.displayOrder"""
    )
    fun collectionMovies(collectionId: Long): PagingSource<Int, MovieEntity>

    /** Streams published collections in editorial order. */
    @Query("SELECT * FROM collections WHERE isActive = 1 AND isPublished = 1 ORDER BY displayOrder")
    fun observeCollections(): Flow<List<CollectionEntity>>

    @Transaction
    @Query("SELECT * FROM collections WHERE isActive = 1 AND isPublished = 1 ORDER BY displayOrder")
    fun observeCollectionsWithMovies(): Flow<List<CollectionWithMovies>>

    @Query(
        """SELECT m.* FROM movies m
           INNER JOIN collections_movies cm ON cm.movieId = m.movieId
           WHERE cm.collectionId = :collectionId AND m.isActive = 1
           ORDER BY cm.displayOrder"""
    )
    suspend fun moviesForCollection(collectionId: Long): List<MovieEntity>

    /** Streams currently available quests. */
    @Query("SELECT * FROM quests WHERE isActive = 1 ORDER BY difficulty, name")
    fun observeQuests(): Flow<List<QuestEntity>>

    @Query("SELECT * FROM countries WHERE isActive = 1 ORDER BY name")
    fun observeCountries(): Flow<List<CountryEntity>>

    @Query("SELECT * FROM badges WHERE isActive = 1 ORDER BY difficulty ASC, code ASC")
    fun observeBadges(): Flow<List<BadgeEntity>>

    @Query("SELECT * FROM rankings WHERE isActive = 1 ORDER BY displayOrder")
    fun observeRankings(): Flow<List<RankingEntity>>

    @Query("SELECT * FROM rankings WHERE rankingId = :rankingId LIMIT 1")
    suspend fun rankingById(rankingId: Long): RankingEntity?

    @Transaction
    @Query("SELECT * FROM movies WHERE isActive = 1")
    fun observeMoviesWithRelations(): Flow<List<MovieWithRelations>>

    @Query("SELECT * FROM directors WHERE isActive = 1 ORDER BY displayName")
    fun observeDirectors(): Flow<List<DirectorEntity>>

    @Query("SELECT * FROM genres WHERE isActive = 1 ORDER BY name")
    fun observeGenres(): Flow<List<GenreEntity>>

    @Query("SELECT * FROM cinema_characteristics WHERE isActive = 1 ORDER BY name")
    fun observeCharacteristics(): Flow<List<CinemaCharacteristicEntity>>

    @Query("SELECT * FROM continents WHERE isActive = 1 ORDER BY name")
    fun observeContinents(): Flow<List<ContinentEntity>>

    @Query("SELECT * FROM continents WHERE isActive = 1")
    suspend fun continents(): List<ContinentEntity>

    @Query("SELECT * FROM countries_continents")
    suspend fun countryContinents(): List<CountryContinentCrossRef>

    @Query("SELECT * FROM movies_countries")
    suspend fun movieCountries(): List<MovieCountryCrossRef>

    @Query("SELECT * FROM movies_countries")
    fun observeMovieCountries(): Flow<List<MovieCountryCrossRef>>

    @Query("SELECT * FROM countries_continents")
    fun observeCountryContinents(): Flow<List<CountryContinentCrossRef>>

    @Query("SELECT * FROM collections_countries")
    fun observeCollectionCountries(): Flow<List<CollectionCountryCrossRef>>

    @Query("SELECT * FROM collections_characteristics")
    fun observeCollectionCharacteristics(): Flow<List<CollectionCharacteristicCrossRef>>
}

@Dao
interface ProgressDao {
    /** Streams the local profile. V1 expects zero or one row. */
    @Query("SELECT * FROM users ORDER BY userId LIMIT 1")
    fun observeLocalUser(): Flow<UserEntity?>

    @Query("SELECT * FROM users ORDER BY userId LIMIT 1")
    suspend fun localUser(): UserEntity?

    /** Creates a profile and returns its generated identifier. */
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertUser(user: UserEntity): Long

    /** Marks a catalogue movie as watched once. */
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertUserMovie(userMovie: UserMovieCrossRef)

    /** Removes a validation so domain progression can be recalculated. */
    @Delete
    suspend fun deleteUserMovie(userMovie: UserMovieCrossRef)

    /** Streams validations newest viewing date first. */
    @Query("SELECT * FROM user_movies WHERE userId = :userId ORDER BY watchedOn DESC")
    fun observeUserMovies(userId: Long): Flow<List<UserMovieCrossRef>>

    @Transaction
    @Query(
        """SELECT m.* FROM movies m
           INNER JOIN user_movies um ON um.movieId = m.movieId
           WHERE um.userId = :userId"""
    )
    suspend fun validatedMovies(userId: Long): List<MovieWithRelations>

    @Query("SELECT * FROM user_movies WHERE userId = :userId")
    suspend fun movieValidations(userId: Long): List<UserMovieCrossRef>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFollowedCollection(value: UserFollowedCollectionCrossRef)

    @Query("DELETE FROM user_followed_collections WHERE userId = :userId AND collectionId = :collectionId")
    suspend fun deleteFollowedCollection(userId: Long, collectionId: Long)

    @Query("SELECT collectionId FROM user_followed_collections WHERE userId = :userId")
    fun observeFollowedCollectionIds(userId: Long): Flow<List<Long>>

    @Query("DELETE FROM user_followed_collections WHERE userId = :userId")
    suspend fun clearFollowedCollections(userId: Long)

    @Query(
        """SELECT b.code FROM badges b
           INNER JOIN user_badges ub ON ub.badgeId = b.badgeId
           WHERE ub.userId = :userId
           ORDER BY ub.earnedAt ASC"""
    )
    suspend fun earnedBadgeCodes(userId: Long): List<String>

    @Query(
        """SELECT b.code FROM badges b
           INNER JOIN user_badges ub ON ub.badgeId = b.badgeId
           WHERE ub.userId = :userId
           ORDER BY ub.earnedAt ASC"""
    )
    fun observeEarnedBadgeCodes(userId: Long): Flow<List<String>>

    @Query("SELECT COALESCE(SUM(amount), 0) FROM xp_transactions WHERE userId = :userId")
    suspend fun totalXp(userId: Long): Long

    @Query("UPDATE users SET rankingId = :rankingId WHERE userId = :userId")
    suspend fun updateRanking(userId: Long, rankingId: Long)

    @Query("UPDATE users SET username = :username WHERE userId = :userId")
    suspend fun updateUsername(userId: Long, username: String)

    @Query("UPDATE users SET birthDate = :birthDate WHERE userId = :userId")
    suspend fun updateBirthDate(userId: Long, birthDate: LocalDate)

    @Query("UPDATE users SET avatarCode = :avatarCode WHERE userId = :userId")
    suspend fun updateAvatarCode(userId: Long, avatarCode: String)

    @Query(
        """UPDATE users SET maxLevelReached =
           CASE WHEN maxLevelReached < :candidate THEN :candidate ELSE maxLevelReached END
           WHERE userId = :userId"""
    )
    suspend fun advanceMaxLevel(userId: Long, candidate: Int)

    @Query(
        """UPDATE users SET unlockedTrackOrdinal =
           CASE WHEN unlockedTrackOrdinal < :candidate THEN :candidate ELSE unlockedTrackOrdinal END
           WHERE userId = :userId"""
    )
    suspend fun advanceUnlockedTrackOrdinal(userId: Long, candidate: Int)

    @Query("UPDATE users SET showcaseBadgeCodes = :codes WHERE userId = :userId")
    suspend fun updateShowcaseBadgeCodes(userId: Long, codes: String?)

    @Query("SELECT * FROM rankings WHERE displayOrder = :displayOrder LIMIT 1")
    suspend fun rankingByOrder(displayOrder: Int): RankingEntity?

    @Query("SELECT * FROM badges WHERE code = :code LIMIT 1")
    suspend fun badgeByCode(code: String): BadgeEntity?

    /** Persists a badge exactly once through its composite key. */
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertUserBadge(userBadge: UserBadgeCrossRef): Long

    /** Persists an assigned quest instance. */
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertUserQuest(userQuest: UserQuestEntity): Long

    @Transaction
    @Query(
        """SELECT * FROM user_quests
           WHERE userId = :userId AND startsAt = :startsAt
           ORDER BY userQuestId"""
    )
    suspend fun questAssignmentsForWeek(
        userId: Long,
        startsAt: Instant,
    ): List<UserQuestWithDefinition>

    @Transaction
    @Query(
        """SELECT * FROM user_quests
           WHERE userId = :userId AND startsAt = :startsAt
           ORDER BY userQuestId"""
    )
    fun observeQuestAssignmentsForWeek(
        userId: Long,
        startsAt: Instant,
    ): Flow<List<UserQuestWithDefinition>>

    @Query("SELECT * FROM quests WHERE isActive = 1 ORDER BY difficulty, questId")
    suspend fun activeQuestDefinitions(): List<QuestEntity>

    @Query(
        """UPDATE user_quests SET status = 'EXPIRED'
           WHERE userId = :userId AND expiresAt <= :now AND status = 'ACTIVE'"""
    )
    suspend fun expireQuests(userId: Long, now: Instant)

    @Query("UPDATE user_quests SET status = 'EXPIRED' WHERE userQuestId = :userQuestId AND status = 'ACTIVE'")
    suspend fun expireUserQuest(userQuestId: Long)

    /** Loads a quest instance so transactional writers can enforce ownership and snapshots. */
    @Query("SELECT * FROM user_quests WHERE userQuestId = :userQuestId")
    suspend fun userQuestById(userQuestId: Long): UserQuestEntity?

    /** Updates bounded quest progress and completion state. */
    @Query(
        """UPDATE user_quests
           SET progress = :progress, status = :status, completedAt = :completedAt
           WHERE userQuestId = :userQuestId"""
    )
    suspend fun updateQuestProgress(
        userQuestId: Long,
        progress: Int,
        status: UserQuestStatus,
        completedAt: Instant?,
    )

    /** Awards XP once per quest; the unique index rejects duplicate rewards. */
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertXpTransaction(transaction: XpTransactionEntity): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertXpTransactionIgnore(transaction: XpTransactionEntity): Long

    @Query("SELECT movieId FROM xp_transactions WHERE userId = :userId AND source = 'FILM' AND movieId IS NOT NULL")
    suspend fun filmXpMovieIds(userId: Long): List<Long>

    @Query("DELETE FROM xp_transactions WHERE userId = :userId AND source = :source")
    suspend fun deleteXpBySource(userId: Long, source: String): Int

    @Query(
        """UPDATE xp_transactions SET amount = :amount
           WHERE userId = :userId AND source = :source AND amount != :amount""",
    )
    suspend fun updateXpAmountBySource(userId: Long, source: String, amount: Int): Int

    @Query("UPDATE users SET maxLevelReached = :level WHERE userId = :userId")
    suspend fun setMaxLevelReached(userId: Long, level: Int)

    /** Returns the XP ledger sum, never a denormalized cache. */
    @Query("SELECT COALESCE(SUM(amount), 0) FROM xp_transactions WHERE userId = :userId")
    fun observeTotalXp(userId: Long): Flow<Long>

    /** Appends a versioned display event to the local history. */
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertActivityEvent(event: ActivityEventEntity): Long

    /** Streams recent history using the required descending time index. */
    @Query(
        "SELECT * FROM activity_events WHERE userId = :userId ORDER BY occurredAt DESC LIMIT :limit"
    )
    fun observeActivity(userId: Long, limit: Int = 2000): Flow<List<ActivityEventEntity>>

    @Query("SELECT badgeId FROM user_badges WHERE userId = :userId")
    fun observeEarnedBadgeIds(userId: Long): Flow<List<Long>>

    /** Counts validations in a date interval for temporal quest rules. */
    @Query(
        """SELECT COUNT(*) FROM user_movies
           WHERE userId = :userId AND watchedOn BETWEEN :from AND :through"""
    )
    suspend fun watchedCount(userId: Long, from: LocalDate, through: LocalDate): Int

    @Query(
        """SELECT c.collectionId AS collectionId,
                  COUNT(DISTINCT cm.movieId) AS totalCount,
                  COUNT(DISTINCT um.movieId) AS watchedCount
           FROM collections c
           LEFT JOIN collections_movies cm ON cm.collectionId = c.collectionId
           LEFT JOIN user_movies um ON um.movieId = cm.movieId AND um.userId = :userId
           WHERE c.isActive = 1 AND c.isPublished = 1
           GROUP BY c.collectionId"""
    )
    fun observeCollectionProgress(userId: Long): Flow<List<CollectionProgressRow>>

    @Query(
        """SELECT c.countryId AS countryId,
                  COUNT(DISTINCT mc.movieId) AS totalCount,
                  COUNT(DISTINCT um.movieId) AS watchedCount
           FROM countries c
           LEFT JOIN movies_countries mc
             ON mc.countryId = c.countryId AND mc.isPrimary = 1
           LEFT JOIN user_movies um ON um.movieId = mc.movieId AND um.userId = :userId
           WHERE c.isActive = 1
           GROUP BY c.countryId"""
    )
    fun observeCountryProgress(userId: Long): Flow<List<CountryProgressRow>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertProgressState(state: UserProgressStateEntity)

    @Query("DELETE FROM user_movies WHERE userId = :userId")
    suspend fun clearUserMovies(userId: Long)

    @Query("DELETE FROM user_badges WHERE userId = :userId")
    suspend fun clearUserBadges(userId: Long)

    @Query("DELETE FROM user_quests WHERE userId = :userId")
    suspend fun clearUserQuests(userId: Long)

    @Query("DELETE FROM xp_transactions WHERE userId = :userId")
    suspend fun clearXpTransactions(userId: Long)

    @Query("DELETE FROM activity_events WHERE userId = :userId")
    suspend fun clearActivityEvents(userId: Long)

    @Query("DELETE FROM user_progress_state WHERE userId = :userId")
    suspend fun clearProgressState(userId: Long)

    @Query(
        "UPDATE users SET rankingId = :firstRankingId, maxLevelReached = 1, unlockedTrackOrdinal = -1, showcaseBadgeCodes = NULL WHERE userId = :userId"
    )
    suspend fun resetUserRatchets(userId: Long, firstRankingId: Long)
}

@Dao
interface RankConfigDao {
    @Insert
    suspend fun insertCatalogVersion(version: CatalogVersionEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDimensionStats(stats: List<CatalogDimensionStatEntity>)

    @Query(
        """SELECT cds.* FROM catalog_dimension_stats cds
           INNER JOIN catalog_versions cv
             ON cv.catalogVersionId = cds.catalogVersionId
           WHERE cv.version = (SELECT MAX(version) FROM catalog_versions)"""
    )
    suspend fun latestDimensionStats(): List<CatalogDimensionStatEntity>

    @Query("SELECT COUNT(*) FROM catalog_dimension_stats WHERE catalogVersionId = :versionId")
    suspend fun dimensionStatCount(versionId: Long): Int

    @Query("SELECT * FROM catalog_versions ORDER BY version DESC LIMIT 1")
    suspend fun latestCatalogVersion(): CatalogVersionEntity?

    @Insert
    suspend fun insertRankConfig(config: RankEngineConfigEntity): Long

    @Insert
    suspend fun insertRankThresholds(thresholds: List<RankThresholdEntity>)

    @Query("SELECT * FROM rank_engine_configs WHERE isActive = 1 ORDER BY rankEngineConfigId DESC LIMIT 1")
    suspend fun activeRankConfig(): RankEngineConfigEntity?

    @Query(
        """SELECT * FROM rank_thresholds
           WHERE rankEngineConfigId = :configId ORDER BY rankOrder"""
    )
    suspend fun thresholds(configId: Long): List<RankThresholdEntity>
}

/** Write-only DAO used by the validated catalogue importer. */
@Dao
interface CatalogImportDao {
    @Insert suspend fun insertMedia(value: MediaAssetEntity): Long
    @Insert suspend fun insertCountry(value: CountryEntity): Long
    @Insert suspend fun insertContinent(value: ContinentEntity): Long
    @Insert suspend fun insertDirector(value: DirectorEntity): Long
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCharacteristicType(value: CharacteristicTypeEntity)
    @Insert suspend fun insertCharacteristic(value: CinemaCharacteristicEntity): Long
    @Insert suspend fun insertGenre(value: GenreEntity): Long
    @Insert suspend fun insertEra(value: EraEntity): Long
    @Insert suspend fun insertMovie(value: MovieEntity): Long
    @Insert suspend fun insertCollection(value: CollectionEntity): Long
    @Insert suspend fun insertRanking(value: RankingEntity): Long
    @Insert suspend fun insertBadge(value: BadgeEntity): Long
    @Insert suspend fun insertQuest(value: QuestEntity): Long
    @Insert suspend fun insertCatalogVersion(value: CatalogVersionEntity): Long

    @Update suspend fun updateMedia(value: MediaAssetEntity)
    @Update suspend fun updateCountry(value: CountryEntity)
    @Update suspend fun updateContinent(value: ContinentEntity)
    @Update suspend fun updateDirector(value: DirectorEntity)
    @Update suspend fun updateCharacteristic(value: CinemaCharacteristicEntity)
    @Update suspend fun updateGenre(value: GenreEntity)
    @Update suspend fun updateEra(value: EraEntity)
    @Update suspend fun updateMovie(value: MovieEntity)
    @Update suspend fun updateCollection(value: CollectionEntity)
    @Update suspend fun updateRanking(value: RankingEntity)
    @Update suspend fun updateBadge(value: BadgeEntity)
    @Update suspend fun updateQuest(value: QuestEntity)

    @Query("SELECT * FROM media_assets WHERE code = :code LIMIT 1")
    suspend fun mediaByCode(code: String): MediaAssetEntity?
    @Query("SELECT * FROM countries WHERE code = :code LIMIT 1")
    suspend fun countryByCode(code: String): CountryEntity?
    @Query("SELECT * FROM continents WHERE code = :code LIMIT 1")
    suspend fun continentByCode(code: String): ContinentEntity?
    @Query("SELECT * FROM directors WHERE code = :code LIMIT 1")
    suspend fun directorByCode(code: String): DirectorEntity?
    @Query("SELECT * FROM cinema_characteristics WHERE code = :code LIMIT 1")
    suspend fun characteristicByCode(code: String): CinemaCharacteristicEntity?
    @Query("SELECT * FROM genres WHERE code = :code LIMIT 1")
    suspend fun genreByCode(code: String): GenreEntity?
    @Query("SELECT * FROM eras WHERE code = :code LIMIT 1")
    suspend fun eraByCode(code: String): EraEntity?
    @Query("SELECT * FROM movies WHERE code = :code LIMIT 1")
    suspend fun movieByCode(code: String): MovieEntity?
    @Query("SELECT * FROM collections WHERE code = :code LIMIT 1")
    suspend fun collectionByCode(code: String): CollectionEntity?
    @Query("SELECT * FROM rankings WHERE code = :code LIMIT 1")
    suspend fun rankingByCode(code: String): RankingEntity?
    @Query("SELECT * FROM badges WHERE code = :code LIMIT 1")
    suspend fun badgeByCode(code: String): BadgeEntity?
    @Query("SELECT * FROM quests WHERE code = :code LIMIT 1")
    suspend fun questByCode(code: String): QuestEntity?

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCountriesContinents(values: List<CountryContinentCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertMoviesCountries(values: List<MovieCountryCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertMoviesDirectors(values: List<MovieDirectorCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertDirectorsCharacteristics(values: List<DirectorCharacteristicCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertMoviesGenres(values: List<MovieGenreCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertMoviesCharacteristics(values: List<MovieCharacteristicCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCollectionsMovies(values: List<CollectionMovieCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCollectionsCharacteristics(values: List<CollectionCharacteristicCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCollectionsCountries(values: List<CollectionCountryCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCollectionsContinents(values: List<CollectionContinentCrossRef>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertCollectionsEras(values: List<CollectionEraCrossRef>)

    @Query("DELETE FROM movies_countries")
    suspend fun clearMoviesCountries()
    @Query("DELETE FROM movies_directors")
    suspend fun clearMoviesDirectors()
    @Query("DELETE FROM movies_genres")
    suspend fun clearMoviesGenres()
    @Query("DELETE FROM movies_characteristics")
    suspend fun clearMoviesCharacteristics()
    @Query("DELETE FROM directors_characteristics")
    suspend fun clearDirectorsCharacteristics()
    @Query("DELETE FROM collections_movies")
    suspend fun clearCollectionsMovies()
    @Query("DELETE FROM collections_characteristics")
    suspend fun clearCollectionsCharacteristics()
    @Query("DELETE FROM collections_countries")
    suspend fun clearCollectionsCountries()
    @Query("DELETE FROM collections_continents")
    suspend fun clearCollectionsContinents()
    @Query("DELETE FROM collections_eras")
    suspend fun clearCollectionsEras()
    @Query("DELETE FROM countries_continents")
    suspend fun clearCountriesContinents()
    @Query("UPDATE movies SET isActive = 0")
    suspend fun deactivateAllMovies()
    @Query("UPDATE collections SET isPublished = 0, isActive = 0")
    suspend fun deactivateAllCollections()
    @Query("UPDATE collections SET displayOrder = -(collectionId + 100000)")
    suspend fun parkCollectionDisplayOrders()
    @Query("UPDATE rankings SET displayOrder = -(rankingId + 100000)")
    suspend fun parkRankingDisplayOrders()
    @Query("UPDATE movies SET isActive = 0 WHERE code NOT IN (:codes)")
    suspend fun deactivateMoviesNotIn(codes: List<String>)
    @Query("UPDATE collections SET isActive = 0, isPublished = 0 WHERE code NOT IN (:codes)")
    suspend fun deactivateCollectionsNotIn(codes: List<String>)

    /** Import is intentionally limited to an empty catalogue artifact. */
    @Query(
        """SELECT
           (SELECT COUNT(*) FROM movies) +
           (SELECT COUNT(*) FROM media_assets) +
           (SELECT COUNT(*) FROM countries) +
           (SELECT COUNT(*) FROM rankings) +
           (SELECT COUNT(*) FROM catalog_versions)"""
    )
    suspend fun catalogRowCount(): Int
}
