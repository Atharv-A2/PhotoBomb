package com.example.photobomb.app.presentation.gallery

import java.time.Instant

data class GalleryItemUiModel(

    val id: String,

    val thumbnailId: String?,

    val mediaType: String,

    val captureTime: Instant?
)