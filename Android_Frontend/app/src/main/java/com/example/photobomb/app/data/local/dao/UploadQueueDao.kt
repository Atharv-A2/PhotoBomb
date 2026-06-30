package com.example.photobomb.app.data.local.dao

import androidx.room.*
import com.example.photobomb.app.data.local.entity.UploadQueueEntity
import com.example.photobomb.app.data.local.entity.UploadStatus
import kotlinx.coroutines.flow.Flow

@Dao
interface UploadQueueDao {

    @Insert(
        onConflict =
            OnConflictStrategy.REPLACE
    )
    suspend fun insert(
        item: UploadQueueEntity
    )

    @Insert(
        onConflict =
            OnConflictStrategy.REPLACE
    )
    suspend fun insertAll(
        items: List<UploadQueueEntity>
    )

    @Update
    suspend fun update(
        entity: UploadQueueEntity
    )

    @Query(
        """
    SELECT *
    FROM upload_queue
    WHERE uri=:uri
    """
    )
    suspend fun get(
        uri: String
    ): UploadQueueEntity?


    @Query(
        "SELECT * FROM upload_queue ORDER BY filename"
    )
    fun observe(): Flow<List<UploadQueueEntity>>

    @Query(
        """
        DELETE

        FROM upload_queue

        WHERE uri=:uri
        """
    )
    suspend fun delete(

        uri: String
    )

}