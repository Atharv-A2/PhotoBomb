package com.example.photobomb.app.upload.utils

import android.content.Context
import android.net.Uri
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

object MultipartUtils {

    fun createPart(

        context: Context,

        uri: Uri,

        filename: String,

        mimeType: String,

        ): MultipartBody.Part {

        val cacheFile = File(
            context.cacheDir,
            filename
        )

        context.contentResolver
            .openInputStream(uri)
            ?.use { input ->

                cacheFile.outputStream().use {

                    input.copyTo(it)
                }
            }

        val requestBody =
            cacheFile.asRequestBody(
                mimeType.toMediaTypeOrNull()
            )

        return MultipartBody.Part.createFormData(

            "file",

            filename,

            requestBody
        )
    }
}