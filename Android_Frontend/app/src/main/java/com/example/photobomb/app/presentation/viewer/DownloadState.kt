package com.example.photobomb.app.presentation.viewer

import android.net.Uri

sealed interface DownloadState {

    data object Idle : DownloadState

    data class Progress(
        val downloaded: Long,
        val total: Long,
        val percent: Int
    ) : DownloadState

    data class Success(
        val uri: Uri
    ) : DownloadState

    data class Error(
        val message: String
    ) : DownloadState
}