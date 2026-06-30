package com.example.photobomb.app.presentation.upload

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.photobomb.app.data.repository.UploadQueueRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class UploadQueueViewModel(

    private val repository:
    UploadQueueRepository

) : ViewModel() {

    private val _uiState =

        MutableStateFlow(
            UploadQueueUiState()
        )

    val uiState:
            StateFlow<UploadQueueUiState> =
        _uiState.asStateFlow()

    init {

        observeUploads()
    }

    private fun observeUploads() {

        viewModelScope.launch {

            repository
                .observeUploads()

                .collectLatest { rows ->

                    _uiState.value =
                        UploadQueueUiState(

                            uploads =

                                rows.map {

                                    UploadQueueItem(

                                        uri = it.uri,

                                        filename = it.filename,

                                        progress = it.progress,

                                        size = it.size,

                                        status = it.status,

                                        errorMessage = it.errorMessage
                                    )
                                }
                        )
                }
        }
    }
}