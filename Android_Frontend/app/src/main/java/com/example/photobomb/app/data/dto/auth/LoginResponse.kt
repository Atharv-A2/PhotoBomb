package com.example.photobomb.app.data.dto.auth

data class LoginResponse(
    val access_token: String,
    val refresh_token: String,
    val expires_in: Int
)