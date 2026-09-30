package fr.jsisie.urbinema.data.db

import androidx.room.Embedded
import androidx.room.Junction
import androidx.room.Relation

/** Complete film projection used by detail screens and rule evaluation. */
/** Director credit in billing order, used to label multi-director films. */
data class MovieDirectorBilling(
    val movieId: Long,
    val directorId: Long,
    val billingOrder: Int,
)

data class MovieWithRelations(
    @Embedded val movie: MovieEntity,
    @Relation(
        parentColumn = "movieId",
        entityColumn = "countryId",
        associateBy = Junction(MovieCountryCrossRef::class),
    )
    val countries: List<CountryEntity>,
    @Relation(
        parentColumn = "movieId",
        entityColumn = "directorId",
        associateBy = Junction(MovieDirectorCrossRef::class),
    )
    val directors: List<DirectorEntity>,
    @Relation(
        parentColumn = "movieId",
        entityColumn = "genreId",
        associateBy = Junction(MovieGenreCrossRef::class),
    )
    val genres: List<GenreEntity>,
    @Relation(
        parentColumn = "movieId",
        entityColumn = "characteristicId",
        associateBy = Junction(MovieCharacteristicCrossRef::class),
    )
    val characteristics: List<CinemaCharacteristicEntity>,
)

data class CollectionProgressRow(
    val collectionId: Long,
    val totalCount: Int,
    val watchedCount: Int,
)

data class CountryProgressRow(
    val countryId: Long,
    val totalCount: Int,
    val watchedCount: Int,
)

data class UserQuestWithDefinition(
    @Embedded val assignment: UserQuestEntity,
    @Relation(parentColumn = "questId", entityColumn = "questId")
    val definition: QuestEntity,
)

/** Ordered collection projection. Movie ordering is queried explicitly by the DAO. */
data class CollectionWithMovies(
    @Embedded val collection: CollectionEntity,
    @Relation(
        parentColumn = "collectionId",
        entityColumn = "movieId",
        associateBy = Junction(CollectionMovieCrossRef::class),
    )
    val movies: List<MovieEntity>,
)
