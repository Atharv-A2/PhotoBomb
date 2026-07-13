package com.example.photobomb.app.data.repository

import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import com.example.photobomb.app.data.api.GalleryApi
import com.example.photobomb.app.data.paging.GalleryPagingSource
import com.example.photobomb.app.presentation.gallery.GalleryItemUiModel
import kotlinx.coroutines.flow.Flow

class GalleryRepository(

    private val api: GalleryApi

) {

    private companion object {

        const val PAGE_SIZE = 15
    }

    fun gallery():

            Flow<PagingData<GalleryItemUiModel>> {

        return Pager(

            PagingConfig(

                pageSize = PAGE_SIZE,
                initialLoadSize = PAGE_SIZE*2,
                prefetchDistance = PAGE_SIZE,
                enablePlaceholders = false
            )

        ) {

            GalleryPagingSource(api)

        }.flow
    }
}