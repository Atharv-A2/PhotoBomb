package com.example.photobomb.app.data.repository

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.app.data.api.ViewerApi
import com.example.photobomb.app.data.datastore.AuthPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext

class ViewerRepository(

    private val api: ViewerApi,
    private val context: Context,
    private val authPreferences: AuthPreferences,

) {

    suspend fun getMedia(
        id: String
    ) =
        api.getMedia(id)

    suspend fun downloadFile(
        mediaId: String,
        fileName: String,
        mimeType: String
    ): Long {

        val url =
            "${ApiConstants.BASE_URL}" +
                    "api/v1/media/" +
                    mediaId +
                    "/download"

        val token = getAccessToken()
            ?: throw IllegalStateException("No access token")

        val request =
            DownloadManager.Request(
                Uri.parse(url)
            )
                .setTitle(fileName)
                .setDescription("Downloading media")
                .setMimeType(mimeType)
                .setNotificationVisibility(
                    DownloadManager.Request
                        .VISIBILITY_VISIBLE_NOTIFY_COMPLETED
                )
                .setDestinationInExternalPublicDir(
                    Environment.DIRECTORY_DOWNLOADS,
                    "PhotoBomb/$fileName"
                )

        request.addRequestHeader(
            "Authorization",
            "Bearer $token"
        )

        val manager =
            context.getSystemService(
                Context.DOWNLOAD_SERVICE
            ) as DownloadManager


        return manager.enqueue(request)
    }

    suspend fun getAccessToken():
            String? {

        return authPreferences
            .getAccessToken()
    }

    suspend fun waitForDownloadCompletion(
        downloadId: Long
    ): Boolean = withContext(Dispatchers.IO) {

        val manager =
            context.getSystemService(
                Context.DOWNLOAD_SERVICE
            ) as DownloadManager

        while (isActive) {

            val status =
                manager.query(
                    DownloadManager.Query()
                        .setFilterById(downloadId)
                ).use { cursor ->

                    if (cursor.moveToFirst()) {

                        cursor.getInt(
                            cursor.getColumnIndexOrThrow(
                                DownloadManager.COLUMN_STATUS
                            )
                        )

                    } else {
                        null
                    }
                }

            when (status) {

                DownloadManager.STATUS_SUCCESSFUL ->
                    return@withContext true

                DownloadManager.STATUS_FAILED ->
                    return@withContext false
            }

            delay(500)
        }

        false
    }
}