package com.example.photobomb.app.upload.model

import android.net.Uri

data class SelectedMedia(

    val uri: Uri,

    val displayName: String?,

    val mimeType: String?,

    val size: Long,
)