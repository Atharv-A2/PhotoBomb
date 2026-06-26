package com.example.photobomb.app.presentation.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.photobomb.app.data.repository.GalleryRepository

class GalleryViewModelFactory(
    private val repository:
    GalleryRepository
) : ViewModelProvider.Factory {

    override fun <T : ViewModel>
            create(
        modelClass: Class<T>
    ): T {

        return GalleryViewModel(
            repository
        ) as T
    }
}