package com.example.photobomb.app.data.datastore

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first

private val Context.dataStore by preferencesDataStore(
    name = "auth_preferences"
)

class AuthPreferences(
    private val context: Context
) {

    companion object {

        private val ACCESS_TOKEN =
            stringPreferencesKey(
                "access_token"
            )

        private val REFRESH_TOKEN =
            stringPreferencesKey(
                "refresh_token"
            )
    }

    suspend fun saveTokens(
        accessToken: String,
        refreshToken: String
    ) {
        context.dataStore.edit { prefs ->

            prefs[ACCESS_TOKEN] =
                accessToken

            prefs[REFRESH_TOKEN] =
                refreshToken
        }
    }

    suspend fun getAccessToken(): String? {

        val prefs =
            context.dataStore.data.first()

        return prefs[ACCESS_TOKEN]
    }

    suspend fun getRefreshToken(): String? {

        val prefs =
            context.dataStore.data.first()

        return prefs[REFRESH_TOKEN]
    }

    suspend fun saveAccessToken(
        token: String
    ) {

        context.dataStore.edit {

            it[ACCESS_TOKEN] =
                token
        }
    }

    suspend fun clear() {

        context.dataStore.edit {
            it.clear()
        }
    }

    suspend fun isLoggedIn(): Boolean {

        return !getAccessToken()
            .isNullOrBlank()
    }
}