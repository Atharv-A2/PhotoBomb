package com.example.photobomb.app.core.network

import AuthInterceptor
import android.content.Context
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.data.repository.AuthRepository
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object NetworkClient {

    @Volatile
    private var retrofit: Retrofit? = null

    @Volatile
    private var okHttpClient: OkHttpClient? = null

    fun getClient(
        context: Context
    ): OkHttpClient {

        okHttpClient?.let {
            return it
        }

        synchronized(this) {

            okHttpClient?.let {
                return it
            }

            val prefs =
                AuthPreferences(context)

            val repository =
                AuthRepository(
                    NetworkModule.authApiWithoutAuth(),
                    prefs
                )

            val logging =
                HttpLoggingInterceptor().apply {
                    level =
                        HttpLoggingInterceptor.Level.BODY
                }

            okHttpClient =
                OkHttpClient.Builder()
                    .addInterceptor(
                        AuthInterceptor(prefs)
                    )
                    .authenticator(
                        TokenAuthenticator(repository)
                    )
                    .addInterceptor(logging)
                    .build()

            return okHttpClient!!

        }

    }

    fun getRetrofit(
        context: Context
    ): Retrofit {

        retrofit?.let {
            return it
        }

        synchronized(this) {

            retrofit?.let {
                return it
            }

            retrofit =
                Retrofit.Builder()
                    .baseUrl(ApiConstants.BASE_URL)
                    .client(
                        getClient(context)
                    )
                    .addConverterFactory(
                        GsonConverterFactory.create()
                    )
                    .build()

            return retrofit!!

        }

    }

}