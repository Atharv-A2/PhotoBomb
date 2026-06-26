package com.example.photobomb.app.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.photobomb.app.core.utils.Resource
import com.example.photobomb.app.data.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AuthViewModel(
    private val repository:
    AuthRepository,
) : ViewModel() {

    private val _uiState =
        MutableStateFlow(
            AuthUiState()
        )

    val uiState:
            StateFlow<AuthUiState>
            = _uiState

    fun login(
        email: String,
        password: String,
    ) {

        viewModelScope.launch {

            _uiState.value =
                AuthUiState(
                    isLoading = true
                )

            val result =
                repository.login(
                    email,
                    password
                )

            when(result) {

                is Resource.Success -> {

                    _uiState.value =
                        AuthUiState(
                            isLoggedIn = true
                        )
                }

                is Resource.Error -> {

                    _uiState.value =
                        AuthUiState(
                            error = result.message
                        )
                }

                else -> Unit
            }
        }
    }

    fun isLoggedIn(
        callback: (Boolean) -> Unit
    ) {
        viewModelScope.launch {

            callback(
                repository.isLoggedIn()
            )
        }
    }
}