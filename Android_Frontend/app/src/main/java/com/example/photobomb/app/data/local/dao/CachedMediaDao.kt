package com.example.photobomb.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.photobomb.app.data.local.entity.CachedMediaEntity

@Dao
interface CachedMediaDao {

    @Insert(
        onConflict =
            OnConflictStrategy.REPLACE
    )
    suspend fun insertAll(
        items: List<CachedMediaEntity>
    )

    @Query(
        "SELECT * FROM cached_media ORDER BY captureTime DESC"
    )
    suspend fun getAll():
            List<CachedMediaEntity>

    @Query(
        "DELETE FROM cached_media"
    )
    suspend fun clear()
}