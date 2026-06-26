package com.example.photobomb.app.presentation.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.photobomb.app.data.repository.GalleryRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class GalleryViewModel(

    private val repository:
    GalleryRepository
) : ViewModel() {

    private val _uiState =
        MutableStateFlow(
            GalleryUiState()
        )

    val uiState:
            StateFlow<GalleryUiState> =
        _uiState.asStateFlow()

    fun loadGallery() {

        viewModelScope.launch {

            try {

                _uiState.value =
                    GalleryUiState(
                        isLoading = true
                    )

                repository.refreshGallery()

                val items =
                    repository
                        .getCachedGallery()

                _uiState.value =
                    GalleryUiState(
                        items = items
                    )

            } catch (
                e: Exception
            ) {

                _uiState.value =
                    GalleryUiState(
                        error =
                            e.message
                    )
            }
        }
    }
}