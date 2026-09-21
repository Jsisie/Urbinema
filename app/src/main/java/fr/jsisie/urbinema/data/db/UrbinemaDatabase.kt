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
        CollectionContinentCrossRef::class, CollectionEraCrossRef::class, RankingEntity::class,
        BadgeEntity::class, QuestEntity::class, UserEntity::class, UserMovieCrossRef::class,
        UserFollowedCollectionCrossRef::class, UserBadgeCrossRef::class, UserQuestEntity::class,
        XpTransactionEntity::class,
        ActivityEventEntity::class, CatalogVersionEntity::class,
        RankEngineConfigEntity::class, RankThresholdEntity::class,
        CatalogDimensionStatEntity::class, UserProgressStateEntity::class,
    ],
    version = 7,
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
                    MIGRATION_6_7,
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
