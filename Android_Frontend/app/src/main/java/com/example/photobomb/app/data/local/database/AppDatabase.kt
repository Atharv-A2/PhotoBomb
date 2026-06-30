package com.example.photobomb.app.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.example.photobomb.app.data.local.dao.CachedMediaDao
import com.example.photobomb.app.data.local.dao.UploadQueueDao
import com.example.photobomb.app.data.local.entity.CachedMediaEntity
import com.example.photobomb.app.data.local.entity.UploadQueueEntity

@Database(
    entities = [
        CachedMediaEntity::class,
        UploadQueueEntity::class
    ],
    version = 4,
    exportSchema = false
)
abstract class AppDatabase :
    RoomDatabase() {

    abstract fun cachedMediaDao():
            CachedMediaDao

    abstract fun uploadQueueDao():
            UploadQueueDao
}