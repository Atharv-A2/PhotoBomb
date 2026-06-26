package com.example.photobomb.app.data.dto.gallery

data class GalleryItemDto(
    val id: String,
    val media_type: String,
    val thumbnail_id: String?,
    val capture_time: String?,
    val width: Int?,
    val height: Int?
)