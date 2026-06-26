package com.example.photobomb.app.data.api

import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Streaming

interface StreamApi {

    @Streaming
    @GET(
        "api/v1/media/{id}/stream"
    )
    suspend fun stream(

        @Path("id")
        mediaId: String

    ): Response<ResponseBody>

}