package com.example.photobomb.app.core.image

import android.content.Context
import coil.ImageLoader
import coil.util.DebugLogger
import coil.disk.DiskCache
import com.example.photobomb.app.core.network.NetworkClient
import okhttp3.OkHttpClient
import coil.request.CachePolicy
//import coil.network.okhttp.OkHttpNetworkFetcherFactory

object ImageLoaderFactory {

    @Volatile
    private var loader:
            ImageLoader? = null

    fun get(
        context: Context
    ): ImageLoader {

        loader?.let {
            return it
        }

        synchronized(this) {

            loader?.let {
                return it
            }

            val client: OkHttpClient =
                NetworkClient.getClient(
                    context
                )

            loader =
                ImageLoader.Builder(context)
                    .okHttpClient(client)
                    .diskCachePolicy(
                        CachePolicy.ENABLED
                    )
                    .memoryCachePolicy(
                        CachePolicy.ENABLED
                    )
                    .logger(
                        DebugLogger()
                    )
                    .build()

            return loader!!

        }

    }

}