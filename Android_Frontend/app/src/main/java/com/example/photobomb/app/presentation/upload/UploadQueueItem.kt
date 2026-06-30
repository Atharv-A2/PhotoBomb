package com.example.photobomb.app.presentation.upload

import com.example.photobomb.app.data.local.entity.UploadStatus

data class UploadQueueItem(

    val uri: String,

    val filename: String,

    val progress: Int,

    val size: Long,

    val status: UploadStatus,

    val errorMessage: String?
)