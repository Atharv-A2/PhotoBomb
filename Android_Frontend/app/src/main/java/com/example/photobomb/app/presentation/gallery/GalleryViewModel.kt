package com.example.photobomb.app.presentation.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.paging.cachedIn
import com.example.photobomb.app.data.repository.GalleryRepository
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.launch

class GalleryViewModel(

    private val repository: GalleryRepository

) : ViewModel() {

    private val refreshTrigger =
        MutableSharedFlow<Unit>(replay = 1)


    val galleryPagingData =
        refreshTrigger
            .onStart { emit(Unit) }
            .flatMapLatest {
                repository.gallery()
            }
            .cachedIn(viewModelScope)

    fun refreshGallery() {
        viewModelScope.launch {
            refreshTrigger.emit(Unit)
        }
    }
}