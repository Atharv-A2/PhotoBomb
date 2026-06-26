package com.example.photobomb.app.data.api

import com.example.photobomb.app.data.dto.gallery.GalleryResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface GalleryApi {

    @GET("api/v1/media")
    suspend fun getGallery(
        @Query("limit")
        limit: Int,

        @Query("offset")
        offset: Int,
    ): Response<GalleryResponse>
}