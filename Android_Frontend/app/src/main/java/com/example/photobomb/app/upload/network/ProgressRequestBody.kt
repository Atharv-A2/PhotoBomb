package com.example.photobomb.app.upload.network

import okhttp3.MediaType
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody
import okio.BufferedSink
import java.io.File

class ProgressRequestBody(

    private val file: File,

    private val contentType: String,

    private val onProgress: (Int) -> Unit

) : RequestBody() {

    companion object {
        private const val BUFFER_SIZE = 8 * 1024
    }

    override fun contentType(): MediaType? =
        contentType.toMediaTypeOrNull()

    override fun contentLength(): Long =
        file.length()

    override fun writeTo(
        sink: BufferedSink
    ) {

        val total =
            contentLength()

        var uploaded = 0L

        file.inputStream().use { input ->

            val buffer =
                ByteArray(BUFFER_SIZE)

            while (true) {

                val read =
                    input.read(buffer)

                if (read == -1)
                    break

                sink.write(
                    buffer,
                    0,
                    read
                )

                uploaded += read

                val percent =
                    ((uploaded * 100) / total)
                        .toInt()

                onProgress(percent)
            }
        }
    }
}