package com.example.photobomb.app.core.media

import android.content.Context
import androidx.media3.datasource.okhttp.OkHttpDataSource
import com.example.photobomb.app.core.network.NetworkClient
import okhttp3.OkHttpClient

object MediaSourceFactory {

    fun create(
        context: Context
    ): OkHttpDataSource.Factory {

        val client: OkHttpClient =
            NetworkClient.getClient(
                context
            )

        return OkHttpDataSource.Factory(
            client
        )
    }
}