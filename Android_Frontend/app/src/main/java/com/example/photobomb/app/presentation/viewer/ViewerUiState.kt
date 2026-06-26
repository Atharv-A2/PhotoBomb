package com.example.photobomb.app.presentation.viewer

import com.example.photobomb.app.data.dto.viewer.MediaDetailResponse

data class ViewerUiState(

    val loading: Boolean = false,

    val media: MediaDetailResponse? = null,

    val viewerUrl: String? = null,

    val error: String? = null

)