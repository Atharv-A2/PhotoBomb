package com.example.photobomb.app.data.local.database

import android.content.Context
import androidx.room.Room

object DatabaseProvider {

    @Volatile
    private var INSTANCE:
            AppDatabase? = null

    fun getDatabase(
        context: Context
    ): AppDatabase {

        return INSTANCE ?: synchronized(
            this
        ) {

            Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "photobomb.db"
            )
                .fallbackToDestructiveMigration()
                .build()
                .also {

                    INSTANCE = it
                }
        }
    }
}