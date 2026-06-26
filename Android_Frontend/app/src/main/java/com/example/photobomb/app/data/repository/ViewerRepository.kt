package com.example.photobomb.app.data.repository

import com.example.photobomb.app.data.api.ViewerApi

class ViewerRepository(

    private val api: ViewerApi

) {

    suspend fun getMedia(
        id: String
    ) =
        api.getMedia(id)

}