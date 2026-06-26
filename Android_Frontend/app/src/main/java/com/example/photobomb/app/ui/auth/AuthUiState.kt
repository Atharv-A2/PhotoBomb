package com.example.photobomb.app.ui.auth

data class AuthUiState(

    val isLoading: Boolean =
        false,

    val isLoggedIn: Boolean =
        false,

    val error: String? =
        null,
)