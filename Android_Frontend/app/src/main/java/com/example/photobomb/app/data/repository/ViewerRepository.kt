package com.example.photobomb.app.data.repository

import android.content.ContentValues
import android.content.Context
import android.os.Environment
import android.provider.MediaStore
import com.example.photobomb.app.data.api.ViewerApi
import com.example.photobomb.app.presentation.viewer.DownloadState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import java.io.IOException

class ViewerRepository(

    private val api: ViewerApi,
    private val context: Context

) {

    suspend fun getMedia(
        id: String
    ) =
        api.getMedia(id)


    fun downloadFile(
        mediaId: String
    ): Flow<DownloadState> = flow {

        val response = api.downloadMedia(mediaId)

        if (!response.isSuccessful) {
            throw IOException("Download failed")
        }

        val body = response.body() ?: throw IOException("Empty body")

        val mimeType = response.body()?.contentType()?.toString()
            ?: response.headers()["Content-Type"]
            ?: "application/octet-stream"

        val total =
            response.headers()["Content-Length"]?.toLongOrNull()
                ?: body.contentLength()

        val contentDisposition = response.headers()["Content-Disposition"]

        val displayName =
            extractFileName(contentDisposition)
                ?: "download"

        val resolver = context.contentResolver

        val isVideo = mimeType.startsWith("video")

        val relativePath =
            if (isVideo) {
                Environment.DIRECTORY_MOVIES + "/PhotoBomb"
            } else {
                Environment.DIRECTORY_PICTURES + "/PhotoBomb"
            }

        val values = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, displayName)
            put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
            put(MediaStore.MediaColumns.RELATIVE_PATH, relativePath)
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        }

        val collection =
            if (mimeType.startsWith("video")) {
                MediaStore.Video.Media.EXTERNAL_CONTENT_URI
            } else {
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }

        val uri = resolver.insert(collection, values)
            ?: throw IOException("Unable to create MediaStore entry")

        resolver.openOutputStream(uri)?.use { output ->

            body.byteStream().use { input ->

                val buffer = ByteArray(8192)

                var downloaded = 0L

                while (true) {
                    val read = input.read(buffer)
                    if (read == -1) break

                    output.write(buffer, 0, read)

                    downloaded += read

                    emit(
                        DownloadState.Progress(
                            downloaded,
                            total,
                            ((downloaded * 100) / total).toInt()
                        )
                    )
                }
            }
        }

        values.clear()
        values.put(MediaStore.MediaColumns.IS_PENDING, 0)
        resolver.update(uri, values, null, null)

        emit(DownloadState.Success(uri))
    }
        .flowOn(Dispatchers.IO)

    private fun extractFileName(header: String?): String? {
        if (header == null) return null

        val regex = Regex("""filename="?([^"]+)"?""")
        return regex.find(header)
            ?.groupValues
            ?.getOrNull(1)
    }
}