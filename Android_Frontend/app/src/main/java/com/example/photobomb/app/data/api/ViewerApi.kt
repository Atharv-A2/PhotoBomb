package com.example.photobomb.app.data.api

import com.example.photobomb.app.data.dto.viewer.MediaDetailResponse
import com.example.photobomb.app.data.dto.viewer.ViewerResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

interface ViewerApi {

    @GET(
        "api/v1/media/{id}"
    )
    suspend fun getMedia(

        @Path("id")
        mediaId: String

    ): Response<MediaDetailResponse>

}