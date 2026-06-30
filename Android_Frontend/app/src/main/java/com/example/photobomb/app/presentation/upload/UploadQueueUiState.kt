package com.example.photobomb.app.presentation.upload

data class UploadQueueUiState(

    val uploads:

    List<UploadQueueItem> =
        emptyList(),

    val isLoading: Boolean = false,

    val error: String? = null
)