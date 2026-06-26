package com.example.photobomb.app.domain.model

data class AuthResult(
    val accessToken: String,
    val refreshToken: String,
    val expiresIn: Int
)