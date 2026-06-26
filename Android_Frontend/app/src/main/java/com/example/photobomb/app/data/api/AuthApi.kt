package com.example.photobomb.app.data.api

import com.example.photobomb.app.data.dto.auth.LoginRequest
import com.example.photobomb.app.data.dto.auth.LoginResponse
import com.example.photobomb.app.data.dto.auth.RefreshRequest
import com.example.photobomb.app.data.dto.auth.RegisterRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {

    @POST(
        "api/v1/auth/register"
    )
    suspend fun register(
        @Body request:
        RegisterRequest
    ): Response<Unit>

    @POST(
        "api/v1/auth/login"
    )
    suspend fun login(
        @Body request:
        LoginRequest
    ): Response<LoginResponse>

    @POST(
        "api/v1/auth/refresh"
    )
    suspend fun refresh(
        @Body request:
        RefreshRequest
    ): Response<LoginResponse>
}