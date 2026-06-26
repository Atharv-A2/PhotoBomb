package com.example.photobomb.app.data.repository

import com.example.photobomb.app.data.api.GalleryApi
import com.example.photobomb.app.data.local.dao.CachedMediaDao
import com.example.photobomb.app.data.local.entity.CachedMediaEntity

class GalleryRepository(

    private val api: GalleryApi,

    private val dao: CachedMediaDao,
) {

    suspend fun refreshGallery() {

        val response =
            api.getGallery(
                limit = 100,
                offset = 0
            )

        if (
            response.isSuccessful
        ) {

            val body =
                response.body()
                    ?: return

            dao.clear()

            dao.insertAll(

                body.items.map {

                    CachedMediaEntity(
                        id = it.id,
                        mediaType =
                            it.media_type,
                        thumbnailId =
                            it.thumbnail_id,
                        captureTime =
                            it.capture_time,
                        width =
                            it.width,
                        height =
                            it.height
                    )
                }
            )
        }
    }

    suspend fun getCachedGallery() =
        dao.getAll()
}