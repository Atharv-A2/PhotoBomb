package com.example.photobomb.app.presentation.viewer

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.photobomb.app.data.dto.viewer.MediaDetailResponse
import com.example.photobomb.app.data.repository.ViewerRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ViewerViewModel(

    private val repository: ViewerRepository

) : ViewModel() {

    private val _uiState =
        MutableStateFlow(
            ViewerUiState()
        )

    val uiState:
            StateFlow<ViewerUiState> =
        _uiState.asStateFlow()

    private val _downloadComplete =
        MutableStateFlow<Boolean?>(null)

    val downloadComplete =
        _downloadComplete.asStateFlow()

    fun load(
        mediaId: String
    ) {

        viewModelScope.launch {

            _uiState.value =
                ViewerUiState(
                    loading = true
                )

            try {

                val response =
                    repository.getMedia(
                        mediaId
                    )

                if (
                    response.isSuccessful
                ) {

                    _uiState.value =
                        ViewerUiState(
                            media =
                                response.body()
                        )

                } else {

                    _uiState.value =
                        ViewerUiState(
                            error =
                                response.message()
                        )

                }

            } catch (
                e: Exception
            ) {

                _uiState.value =
                    ViewerUiState(
                        error =
                            e.message
                    )

            }

        }

    }

    fun download(
        media: MediaDetailResponse
    ) {

        viewModelScope.launch {

            try {

                val downloadId =
                    repository.downloadFile(
                        media.id,
                        media.original_filename,
                        media.mime_type
                    )


                val success =
                    repository.waitForDownloadCompletion(
                        downloadId
                    )


                _downloadComplete.value = success


            } catch (e: Exception) {

                _downloadComplete.value = false
            }
        }
    }
}