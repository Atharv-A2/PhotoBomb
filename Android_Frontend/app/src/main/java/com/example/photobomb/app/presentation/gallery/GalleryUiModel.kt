package com.example.photobomb.app.presentation.gallery

sealed interface GalleryUiModel {

    data class Header(
        val title: String
    ) : GalleryUiModel

    data class Media(
        val item: GalleryItemUiModel
    ) : GalleryUiModel
}