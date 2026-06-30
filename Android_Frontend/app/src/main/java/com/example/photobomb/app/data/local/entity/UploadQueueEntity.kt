package com.example.photobomb.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(
    tableName = "upload_queue"
)
data class UploadQueueEntity(

    @PrimaryKey
    val uri: String,

    val filename: String,

    val mimeType: String,

    val size: Long,

    var uploadSessionId: String? = null,

    var mediaId: String? = null,

    var status: UploadStatus,

    var progress: Int,

    var retryCount: Int,

    var errorMessage: String? = null
)