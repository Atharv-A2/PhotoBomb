package com.example.photobomb.app.ui.splash

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.photobomb.MainActivity
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.ui.auth.LoginActivity
import kotlinx.coroutines.launch

class SplashActivity :
    AppCompatActivity() {

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(
            savedInstanceState
        )

        lifecycleScope.launch {

            val prefs =
                AuthPreferences(
                    applicationContext
                )

            if (
                prefs.isLoggedIn()
            ) {

                startActivity(
                    Intent(
                        this@SplashActivity,
                        MainActivity::class.java
                    )
                )

            } else {

                startActivity(
                    Intent(
                        this@SplashActivity,
                        LoginActivity::class.java
                    )
                )
            }

            finish()
        }
    }
}