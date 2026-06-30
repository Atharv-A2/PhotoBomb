package com.example.photobomb.app.upload.dto

data class CreateUploadSessionDto(

    val filename: String,

    val file_size: Long,

    val mime_type: String,
)

data class UploadSessionResponse(

    val upload_session_id: String,

    val status: String,
)