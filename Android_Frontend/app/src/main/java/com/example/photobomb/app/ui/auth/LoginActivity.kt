package com.example.photobomb.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.photobomb.MainActivity
import com.example.photobomb.R
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.data.repository.AuthRepository
import kotlinx.coroutines.launch

class LoginActivity :
    AppCompatActivity() {

    private lateinit var viewModel:
            AuthViewModel

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(
            savedInstanceState
        )

        setContentView(
            R.layout.activity_login
        )

        val prefs =
            AuthPreferences(
                applicationContext
            )

        val repository =
            AuthRepository(
                NetworkModule.authApi(
                    applicationContext
                ),
                prefs
            )

        viewModel =
            AuthViewModel(
                repository
            )

        val email =
            findViewById<EditText>(
                R.id.etEmail
            )

        val password =
            findViewById<EditText>(
                R.id.etPassword
            )

        val button =
            findViewById<Button>(
                R.id.btnLogin
            )

        val progress =
            findViewById<ProgressBar>(
                R.id.progressBar
            )

        lifecycleScope.launch {

            viewModel.uiState.collect {

                progress.visibility =
                    if (
                        it.isLoading
                    )
                        View.VISIBLE
                    else
                        View.GONE

                if (
                    it.error != null
                ) {

                    Toast.makeText(
                        this@LoginActivity,
                        it.error,
                        Toast.LENGTH_LONG
                    ).show()
                }

                if (
                    it.isLoggedIn
                ) {

                    startActivity(
                        Intent(
                            this@LoginActivity,
                            MainActivity::class.java
                        )
                    )

                    finish()
                }
            }
        }

        button.setOnClickListener {

            viewModel.login(
                email.text.toString()
                    .trim(),
                password.text.toString()
            )
        }
    }
}