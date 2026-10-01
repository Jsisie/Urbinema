package fr.jsisie.urbinema.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

/** Single local source of truth for editorial content and user progression. */
@Database(
    entities = [
        MediaAssetEntity::class, MovieEntity::class, CountryEntity::class,
        ContinentEntity::class, CountryContinentCrossRef::class, MovieCountryCrossRef::class,
        DirectorEntity::class, MovieDirectorCrossRef::class, CharacteristicTypeEntity::class,
        CinemaCharacteristicEntity::class, DirectorCharacteristicCrossRef::class,
        MovieCharacteristicCrossRef::class, GenreEntity::class, MovieGenreCrossRef::class,
        EraEntity::class, CollectionEntity::class, CollectionMovieCrossRef::class,
        CollectionCharacteristicCrossRef::class, CollectionCountryCrossRef::class,
        CollectionContinentCrossRef::class, CollectionEraCrossRef::class,
        LearningPathEntity::class, LearningPathStepEntity::class, LearningPathFactEntity::class,
        LearningPathFigureEntity::class, LearningPathMovieCrossRef::class, RankingEntity::class,
        BadgeEntity::class, QuestEntity::class, UserEntity::class, UserMovieCrossRef::class,
        UserFollowedCollectionCrossRef::class, UserBadgeCrossRef::class, UserQuestEntity::class,
        XpTransactionEntity::class,
        ActivityEventEntity::class, CatalogVersionEntity::class,
        RankEngineConfigEntity::class, RankThresholdEntity::class,
        CatalogDimensionStatEntity::class, UserProgressStateEntity::class,
    ],
    version = 11,
    exportSchema = true,
)
@TypeConverters(UrbinemaConverters::class)
abstract class UrbinemaDatabase : RoomDatabase() {
    abstract fun catalogDao(): CatalogDao
    abstract fun progressDao(): ProgressDao
    abstract fun catalogImportDao(): CatalogImportDao
    abstract fun rankConfigDao(): RankConfigDao

    companion object {
        const val DATABASE_NAME = "urbinema.db"
        const val PRIMARY_COUNTRY_INDEX = "index_movies_countries_one_primary"

        /**
         * Creates the database. The custom callback owns the partial index Room annotations
         * cannot express and recreates it defensively after every open.
         */
        fun build(context: Context): UrbinemaDatabase =
            Room.databaseBuilder(context, UrbinemaDatabase::class.java, DATABASE_NAME)
                .addMigrations(
                    MIGRATION_1_2, MIGRATION_2_3, MIGRATION_3_4, MIGRATION_4_5, MIGRATION_5_6,
                    MIGRATION_6_7, MIGRATION_7_8, MIGRATION_8_9, MIGRATION_9_10,
                    MIGRATION_10_11,
                )
                .fallbackToDestructiveMigration(true)
                .addCallback(SchemaCallback)
                .build()

        val MIGRATION_1_2 = Migration(1, 2) { database ->
            database.execSQL("ALTER TABLE collections ADD COLUMN longDescription TEXT")
        }

        val MIGRATION_2_3 = Migration(2, 3) { database ->
            database.execSQL("ALTER TABLE rankings ADD COLUMN longDescription TEXT")
        }

        val MIGRATION_3_4 = Migration(3, 4) { database ->
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `user_followed_collections` (
                   `userId` INTEGER NOT NULL,
                   `collectionId` INTEGER NOT NULL,
                   `followedAt` TEXT NOT NULL,
                   PRIMARY KEY(`userId`, `collectionId`),
                   FOREIGN KEY(`userId`) REFERENCES `users`(`userId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                   FOREIGN KEY(`collectionId`) REFERENCES `collections`(`collectionId`) ON UPDATE NO ACTION ON DELETE RESTRICT
                )"""
            )
            database.execSQL(
                "CREATE INDEX IF NOT EXISTS `index_user_followed_collections_collectionId` ON `user_followed_collections` (`collectionId`)"
            )
        }

        val MIGRATION_4_5 = Migration(4, 5) { database ->
            database.execSQL(
                "ALTER TABLE collections ADD COLUMN track TEXT NOT NULL DEFAULT 'JOURNEY'"
            )
        }

        val MIGRATION_5_6 = Migration(5, 6) { database ->
            database.execSQL(
                "ALTER TABLE users ADD COLUMN unlockedTrackOrdinal INTEGER NOT NULL DEFAULT -1"
            )
            database.execSQL("ALTER TABLE users ADD COLUMN showcaseBadgeCodes TEXT")
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `xp_transactions_new` (
                   `xpTransactionId` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   `userId` INTEGER NOT NULL,
                   `userQuestId` INTEGER,
                   `movieId` INTEGER,
                   `source` TEXT NOT NULL,
                   `amount` INTEGER NOT NULL,
                   `earnedAt` TEXT NOT NULL,
                   FOREIGN KEY(`userId`) REFERENCES `users`(`userId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                   FOREIGN KEY(`userQuestId`) REFERENCES `user_quests`(`userQuestId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                   FOREIGN KEY(`movieId`) REFERENCES `movies`(`movieId`) ON UPDATE NO ACTION ON DELETE RESTRICT
                )"""
            )
            database.execSQL(
                """INSERT INTO `xp_transactions_new`
                   (`xpTransactionId`, `userId`, `userQuestId`, `movieId`, `source`, `amount`, `earnedAt`)
                   SELECT `xpTransactionId`, `userId`, `userQuestId`, NULL, 'QUEST', `amount`, `earnedAt`
                   FROM `xp_transactions`"""
            )
            database.execSQL("DROP TABLE `xp_transactions`")
            database.execSQL("ALTER TABLE `xp_transactions_new` RENAME TO `xp_transactions`")
            database.execSQL(
                "CREATE INDEX IF NOT EXISTS `index_xp_transactions_userId` ON `xp_transactions` (`userId`)"
            )
            database.execSQL(
                "CREATE UNIQUE INDEX IF NOT EXISTS `index_xp_transactions_userQuestId` ON `xp_transactions` (`userQuestId`)"
            )
            database.execSQL(
                "CREATE INDEX IF NOT EXISTS `index_xp_transactions_movieId` ON `xp_transactions` (`movieId`)"
            )
            database.execSQL(
                "CREATE UNIQUE INDEX IF NOT EXISTS `index_xp_transactions_userId_movieId` ON `xp_transactions` (`userId`, `movieId`)"
            )
        }

        val MIGRATION_6_7 = Migration(6, 7) { database ->
            database.execSQL("ALTER TABLE users ADD COLUMN avatarCode TEXT")
        }

        val MIGRATION_7_8 = Migration(7, 8) { database ->
            // Room compare le schéma juste après la migration. Cet index partiel
            // n'est pas dans les annotations : onOpen l'a déjà créé sur la base v7.
            // On le retire pour le contrôle, onOpen le recrée ensuite.
            dropPartialCountryIndex(database)
            if (!hasColumn(database, "directors", "biography")) {
                database.execSQL("ALTER TABLE directors ADD COLUMN biography TEXT")
            }
        }

        val MIGRATION_8_9 = Migration(8, 9) { database ->
            dropPartialCountryIndex(database)
            if (!hasColumn(database, "directors", "biographyEn")) {
                database.execSQL("ALTER TABLE directors ADD COLUMN biographyEn TEXT")
            }
        }

        val MIGRATION_9_10 = Migration(9, 10) { database ->
            dropPartialCountryIndex(database)
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `learning_paths` (
                    `pathId` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    `code` TEXT NOT NULL,
                    `displayOrder` INTEGER NOT NULL,
                    `name` TEXT NOT NULL,
                    `summary` TEXT NOT NULL,
                    `description` TEXT NOT NULL,
                    `periodLabel` TEXT NOT NULL,
                    `isActive` INTEGER NOT NULL,
                    `createdAt` TEXT NOT NULL,
                    `updatedAt` TEXT NOT NULL
                )"""
            )
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_paths_code` ON `learning_paths` (`code`)")
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_paths_displayOrder` ON `learning_paths` (`displayOrder`)")
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `learning_path_steps` (
                    `stepId` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    `code` TEXT NOT NULL,
                    `pathId` INTEGER NOT NULL,
                    `position` INTEGER NOT NULL,
                    `characteristicId` INTEGER NOT NULL,
                    `name` TEXT NOT NULL,
                    `periodLabel` TEXT NOT NULL,
                    `description` TEXT NOT NULL,
                    `transitionText` TEXT,
                    `isActive` INTEGER NOT NULL,
                    FOREIGN KEY(`pathId`) REFERENCES `learning_paths`(`pathId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                    FOREIGN KEY(`characteristicId`) REFERENCES `cinema_characteristics`(`characteristicId`) ON UPDATE NO ACTION ON DELETE RESTRICT
                )"""
            )
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_path_steps_code` ON `learning_path_steps` (`code`)")
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_steps_pathId` ON `learning_path_steps` (`pathId`)")
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_steps_characteristicId` ON `learning_path_steps` (`characteristicId`)")
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_path_steps_pathId_position` ON `learning_path_steps` (`pathId`, `position`)")
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `learning_path_facts` (
                    `factId` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    `stepId` INTEGER NOT NULL,
                    `position` INTEGER NOT NULL,
                    `title` TEXT NOT NULL,
                    `body` TEXT NOT NULL,
                    FOREIGN KEY(`stepId`) REFERENCES `learning_path_steps`(`stepId`) ON UPDATE NO ACTION ON DELETE CASCADE
                )"""
            )
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_facts_stepId` ON `learning_path_facts` (`stepId`)")
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_path_facts_stepId_position` ON `learning_path_facts` (`stepId`, `position`)")
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `learning_path_figures` (
                    `figureId` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    `stepId` INTEGER NOT NULL,
                    `position` INTEGER NOT NULL,
                    `displayName` TEXT NOT NULL,
                    `role` TEXT NOT NULL,
                    `directorId` INTEGER,
                    FOREIGN KEY(`stepId`) REFERENCES `learning_path_steps`(`stepId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                    FOREIGN KEY(`directorId`) REFERENCES `directors`(`directorId`) ON UPDATE NO ACTION ON DELETE SET NULL
                )"""
            )
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_figures_stepId` ON `learning_path_figures` (`stepId`)")
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_figures_directorId` ON `learning_path_figures` (`directorId`)")
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_path_figures_stepId_position` ON `learning_path_figures` (`stepId`, `position`)")
            database.execSQL(
                """CREATE TABLE IF NOT EXISTS `learning_path_movies` (
                    `stepId` INTEGER NOT NULL,
                    `movieId` INTEGER NOT NULL,
                    `position` INTEGER NOT NULL,
                    PRIMARY KEY(`stepId`, `movieId`),
                    FOREIGN KEY(`stepId`) REFERENCES `learning_path_steps`(`stepId`) ON UPDATE NO ACTION ON DELETE CASCADE,
                    FOREIGN KEY(`movieId`) REFERENCES `movies`(`movieId`) ON UPDATE NO ACTION ON DELETE RESTRICT
                )"""
            )
            database.execSQL("CREATE INDEX IF NOT EXISTS `index_learning_path_movies_movieId` ON `learning_path_movies` (`movieId`)")
            database.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS `index_learning_path_movies_stepId_position` ON `learning_path_movies` (`stepId`, `position`)")
        }

        val MIGRATION_10_11 = Migration(10, 11) { database ->
            dropPartialCountryIndex(database)
            val columns = listOf(
                "countries" to "nameEn",
                "continents" to "nameEn",
                "cinema_characteristics" to "nameEn",
                "cinema_characteristics" to "descriptionEn",
                "genres" to "nameEn",
                "eras" to "nameEn",
                "collections" to "nameEn",
                "collections" to "descriptionEn",
                "collections" to "longDescriptionEn",
                "learning_paths" to "nameEn",
                "learning_paths" to "summaryEn",
                "learning_paths" to "descriptionEn",
                "learning_paths" to "periodLabelEn",
                "learning_path_steps" to "nameEn",
                "learning_path_steps" to "periodLabelEn",
                "learning_path_steps" to "descriptionEn",
                "learning_path_steps" to "transitionTextEn",
                "learning_path_facts" to "titleEn",
                "learning_path_facts" to "bodyEn",
                "learning_path_figures" to "roleEn",
                "rankings" to "nameEn",
                "rankings" to "descriptionEn",
                "rankings" to "longDescriptionEn",
                "badges" to "nameEn",
                "badges" to "descriptionEn",
                "quests" to "nameEn",
                "quests" to "descriptionEn",
            )
            for ((table, column) in columns) {
                if (!hasColumn(database, table, column)) {
                    database.execSQL("ALTER TABLE `$table` ADD COLUMN `$column` TEXT")
                }
            }
        }

        private fun dropPartialCountryIndex(database: SupportSQLiteDatabase) {
            database.execSQL("DROP INDEX IF EXISTS `$PRIMARY_COUNTRY_INDEX`")
        }

        private fun hasColumn(database: SupportSQLiteDatabase, table: String, column: String): Boolean {
            database.query("PRAGMA table_info(`$table`)").use { cursor ->
                val name = cursor.getColumnIndex("name")
                while (cursor.moveToNext()) {
                    if (cursor.getString(name) == column) return true
                }
            }
            return false
        }

        /** Callback shared by production and tests that require the complete physical schema. */
        val SchemaCallback: Callback = object : Callback() {
            override fun onCreate(db: SupportSQLiteDatabase) {
                super.onCreate(db)
                createCustomSchema(db)
            }

            override fun onOpen(db: SupportSQLiteDatabase) {
                super.onOpen(db)
                db.execSQL("PRAGMA foreign_keys = ON")
                createCustomSchema(db)
            }

            private fun createCustomSchema(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """CREATE UNIQUE INDEX IF NOT EXISTS $PRIMARY_COUNTRY_INDEX
                       ON movies_countries(movieId) WHERE isPrimary = 1"""
                )
            }
        }
    }
}
