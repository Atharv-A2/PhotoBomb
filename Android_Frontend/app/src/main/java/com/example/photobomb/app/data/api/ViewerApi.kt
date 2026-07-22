package com.example.photobomb.app.data.api

import com.example.photobomb.app.data.dto.viewer.MediaDetailResponse
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Streaming

interface ViewerApi {

    @GET(
        "api/v1/media/{id}"
    )
    suspend fun getMedia(

        @Path("id")
        mediaId: String

    ): Response<MediaDetailResponse>


    @Streaming
    @GET("api/v1/media/{id}/download")
    suspend fun downloadMedia(

        @Path("id") mediaId: String
    ): Response<ResponseBody>

}