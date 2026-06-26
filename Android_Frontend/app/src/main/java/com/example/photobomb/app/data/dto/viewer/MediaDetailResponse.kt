package com.example.photobomb.app.data.dto.viewer

data class MediaDetailResponse(

    val id: String,

    val media_type: String,

    val original_filename: String,

    val file_size: Long,

    val width: Int?,

    val height: Int?,

    val duration: Double?,

    val capture_time: String?

)