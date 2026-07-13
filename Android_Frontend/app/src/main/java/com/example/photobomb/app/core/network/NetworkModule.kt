package com.example.photobomb.app.core.network

import AuthInterceptor
import android.content.Context
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.app.data.api.AuthApi
import com.example.photobomb.app.data.api.GalleryApi
import com.example.photobomb.app.data.api.StreamApi
import com.example.photobomb.app.data.api.ViewerApi
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.data.repository.AuthRepository
import com.example.photobomb.app.upload.api.UploadApi
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object NetworkModule {

    fun authApi(
        context: Context
    ): AuthApi {
        return NetworkClient
            .getRetrofit(context)
            .create(AuthApi::class.java)
    }

    fun galleryApi(
        context: Context
    ): GalleryApi {
        return NetworkClient
            .getRetrofit(context)
            .create(GalleryApi::class.java)
    }

    fun viewerApi(
        context: Context
    ): ViewerApi {
        return NetworkClient
            .getRetrofit(context)
            .create(ViewerApi::class.java)
    }

    fun streamApi(
        context: Context
    ): StreamApi {
        return NetworkClient
            .getRetrofit(context)
            .create(StreamApi::class.java)
    }

    fun uploadApi(
        context: Context
    ): UploadApi {
        return NetworkClient
            .getRetrofit(context)
            .create(UploadApi::class.java)
    }


    internal fun authApiWithoutAuth(): AuthApi {

        val logging =
            HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.HEADERS
            }

        val client =
            OkHttpClient.Builder()
                .addInterceptor(logging)
                .build()

        return Retrofit.Builder()
            .baseUrl(ApiConstants.BASE_URL)
            .client(client)
            .addConverterFactory(
                GsonConverterFactory.create()
            )
            .build()
            .create(AuthApi::class.java)
    }
}