package com.example.photobomb.app.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.example.photobomb.app.data.local.dao.CachedMediaDao
import com.example.photobomb.app.data.local.entity.CachedMediaEntity

@Database(
    entities = [
        CachedMediaEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase :
    RoomDatabase() {

    abstract fun cachedMediaDao():
            CachedMediaDao
}