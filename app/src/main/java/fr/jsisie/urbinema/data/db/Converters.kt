package fr.jsisie.urbinema.data.db

import androidx.room.TypeConverter
import java.time.Instant
import java.time.LocalDate

/** Stable codes persisted instead of enum ordinals. */
enum class MovieFormat { SHORT, MEDIUM, FEATURE, EXTENDED }
enum class MediaStorageType { ASSET, FILE }
enum class QuestDifficulty { BRONZE, SILVER, GOLD }
enum class UserQuestStatus { ACTIVE, COMPLETED, EXPIRED }

/** Lossless converters for the java.time types supported by minSdk 26. */
class UrbinemaConverters {
    @TypeConverter fun instantToString(value: Instant?): String? = value?.toString()
    @TypeConverter fun stringToInstant(value: String?): Instant? = value?.let(Instant::parse)
    @TypeConverter fun localDateToString(value: LocalDate?): String? = value?.toString()
    @TypeConverter fun stringToLocalDate(value: String?): LocalDate? = value?.let(LocalDate::parse)
    @TypeConverter fun movieFormatToCode(value: MovieFormat?): String? = value?.name
    @TypeConverter fun codeToMovieFormat(value: String?): MovieFormat? = value?.let(MovieFormat::valueOf)
    @TypeConverter fun storageTypeToCode(value: MediaStorageType?): String? = value?.name
    @TypeConverter fun codeToStorageType(value: String?): MediaStorageType? = value?.let(MediaStorageType::valueOf)
    @TypeConverter fun questDifficultyToCode(value: QuestDifficulty?): String? = value?.name
    @TypeConverter fun codeToQuestDifficulty(value: String?): QuestDifficulty? = value?.let(QuestDifficulty::valueOf)
    @TypeConverter fun questStatusToCode(value: UserQuestStatus?): String? = value?.name
    @TypeConverter fun codeToQuestStatus(value: String?): UserQuestStatus? = value?.let(UserQuestStatus::valueOf)
}
