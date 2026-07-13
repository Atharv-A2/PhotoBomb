package com.example.photobomb.app.upload.utils

import android.content.Context
import android.net.Uri
import android.util.Log
import com.example.photobomb.app.upload.network.ProgressRequestBody
import okhttp3.MediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import okio.BufferedSink
import java.io.File
import java.io.IOException

object MultipartUtils {

    fun createPart(
        context: Context,
        uri: Uri,
        filename: String,
        totalSize: Long,
        mimeType: String,
        onProgress: (Int) -> Unit
    ): MultipartBody.Part {

        val requestBody = object : RequestBody() {

            override fun contentType(): MediaType? =
                mimeType.toMediaTypeOrNull()

            override fun writeTo(sink: BufferedSink) {
                Log.d("UPLOAD", "writeTo() called")
                val inputStream =
                    context.contentResolver.openInputStream(uri)
                        ?: throw IOException("Cannot open input stream")

                inputStream.use { input ->
                    val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                    var uploaded = 0L

                    var read: Int

                    while (input.read(buffer).also { read = it } != -1) {
                        sink.write(buffer, 0, read)
                        uploaded += read

                        val progress =
                            ((uploaded * 100) / totalSize).toInt()

                        onProgress(progress)
                    }
                }
            }
        }

        return MultipartBody.Part.createFormData(
            name = "file",
            filename = filename,
            body = requestBody
        )
    }
}