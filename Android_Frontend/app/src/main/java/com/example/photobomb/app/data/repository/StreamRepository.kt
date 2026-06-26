package com.example.photobomb.app.data.repository

import okhttp3.ResponseBody
import com.example.photobomb.app.data.api.StreamApi

class StreamRepository(

    private val api:
    StreamApi

) {

    suspend fun stream(
        mediaId: String
    ): ResponseBody? {

        val response =
            api.stream(
                mediaId
            )

        if (
            response.isSuccessful
        ) {

            return response.body()

        }

        return null

    }

}