package com.example.photobomb.app.presentation.gallery

import com.example.photobomb.app.data.local.entity.CachedMediaEntity

data class GalleryUiState(

    val isLoading: Boolean = false,

    val items: List<CachedMediaEntity> = emptyList(),

    val error: String? = null
)