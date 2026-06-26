package com.example.photobomb.app.core.network

import com.example.photobomb.app.data.repository.AuthRepository
import kotlinx.coroutines.runBlocking
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

class TokenAuthenticator(
    private val repository:
    AuthRepository
) : Authenticator {

    override fun authenticate(
        route: Route?,
        response: Response
    ): Request? {

        val refreshed =
            runBlocking {

                repository.refreshToken()
            }

        if (responseCount(response) >= 2) {
            return null
        }

        if (!refreshed) {

            return null
        }

        val token =
            runBlocking {

                repository
                    .getAccessToken()
            }

        return response.request
            .newBuilder()
            .header(
                "Authorization",
                "Bearer $token"
            )
            .build()
    }

    private fun responseCount(
        response: Response
    ): Int {

        var result = 1

        var current =
            response.priorResponse

        while (current != null) {

            result++

            current =
                current.priorResponse
        }

        return result
    }
}