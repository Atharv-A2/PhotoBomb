package com.example.photobomb.app.presentation.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.paging.cachedIn
import com.example.photobomb.app.data.repository.GalleryRepository

class GalleryViewModel(

    repository: GalleryRepository

) : ViewModel() {

    val galleryPagingData =

        repository.gallery()

            .cachedIn(viewModelScope)
}