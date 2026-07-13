package com.example.photobomb.app.data.paging

import android.util.Log
import androidx.paging.PagingSource
import androidx.paging.PagingState
import com.example.photobomb.app.data.api.GalleryApi
import com.example.photobomb.app.presentation.gallery.GalleryItemUiModel

class GalleryPagingSource(

    private val api: GalleryApi

) : PagingSource<Int, GalleryItemUiModel>() {

    companion object {

        const val PAGE_SIZE = 15
    }

    override suspend fun load(
        params: LoadParams<Int>
    ): LoadResult<Int, GalleryItemUiModel> {

        return try {

            val offset =
                params.key ?: 0

            Log.d("Paging", "Loading offset=${params.key ?: 0}")

            val response =
                api.getGallery(

                    limit = PAGE_SIZE,

                    offset = offset
                )

            if (!response.isSuccessful) {

                return LoadResult.Error(

                    RuntimeException(
                        "Unable to load gallery"
                    )
                )
            }

            val body =
                response.body()!!

            val items =
                body.items.map {

                    GalleryItemUiModel(

                        id = it.id,

                        thumbnailId =
                            it.thumbnail_id,

                        mediaType =
                            it.media_type
                    )
                }

            LoadResult.Page(

                data = items,

                prevKey =

                    if (offset == 0)
                        null
                    else
                        offset - PAGE_SIZE,

                nextKey =

                    if (items.isEmpty())
                        null
                    else
                        offset + PAGE_SIZE
            )

        } catch (
            e: Exception
        ) {

            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(
        state: PagingState<Int, GalleryItemUiModel>
    ): Int? {

        val anchor = state.anchorPosition
            ?: return null

        val page =
            state.closestPageToPosition(anchor)

        return page?.prevKey?.plus(PAGE_SIZE)
            ?: page?.nextKey?.minus(PAGE_SIZE)
    }
}