package com.example.photobomb.app.data.repository

import com.example.photobomb.app.core.utils.Resource
import com.example.photobomb.app.data.api.AuthApi
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.data.dto.auth.LoginRequest
import com.example.photobomb.app.data.dto.auth.RefreshRequest
import com.example.photobomb.app.domain.model.AuthResult


class AuthRepository(
    private val api: AuthApi,
    private val preferences:
    AuthPreferences,
) {

    suspend fun login(
        email: String,
        password: String,
    ): Resource<AuthResult> {

        return try {

            val response =
                api.login(
                    LoginRequest(
                        email = email,
                        password = password,
                    )
                )

            if (
                response.isSuccessful
            ) {

                val body =
                    response.body()
                        ?: return Resource.Error(
                            "Empty response"
                        )

                preferences.saveTokens(
                    body.access_token,
                    body.refresh_token,
                )

                Resource.Success(
                    AuthResult(
                        accessToken =
                            body.access_token,
                        refreshToken =
                            body.refresh_token,
                        expiresIn =
                            body.expires_in,
                    )
                )

            } else {

                Resource.Error(
                    "Login failed"
                )
            }

        } catch (
            e: Exception
        ) {

            Resource.Error(
                e.message
                    ?: "Unknown error"
            )
        }
    }

    suspend fun isLoggedIn(): Boolean {

        return preferences
            .isLoggedIn()
    }

    suspend fun logout() {
        preferences.clear()
    }

    suspend fun refreshToken():
            Boolean {

        return try {

            val refreshToken =
                preferences
                    .getRefreshToken()
                    ?: return false

            val response =
                api.refresh(
                    RefreshRequest(
                        refreshToken
                    )
                )

            if (
                response.isSuccessful
            ) {

                val body =
                    response.body()
                        ?: return false

                preferences.saveTokens(
                    body.access_token,
                    body.refresh_token
                )

                true

            } else {

                false
            }

        } catch (
            e: Exception
        ) {

            false
        }
    }

    suspend fun getAccessToken():
            String? {

        return preferences
            .getAccessToken()
    }
}