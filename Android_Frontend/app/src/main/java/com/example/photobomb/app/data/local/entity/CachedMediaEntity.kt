package com.example.photobomb.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(
    tableName = "cached_media"
)
data class CachedMediaEntity(

    @PrimaryKey
    val id: String,

    val mediaType: String,

    val thumbnailId: String?,

    val captureTime: String?,

    val width: Int?,

    val height: Int?
)