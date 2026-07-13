package com.example.photobomb.app.upload.repository

import android.content.Context
import android.util.Log
import com.example.photobomb.app.upload.api.UploadApi
import com.example.photobomb.app.upload.dto.ApiError
import com.example.photobomb.app.upload.dto.BulkCreateUploadSessionRequest
import com.example.photobomb.app.upload.dto.CreateUploadSessionDto
import com.example.photobomb.app.upload.dto.UploadResult
import com.example.photobomb.app.upload.dto.UploadSessionResponse
import com.example.photobomb.app.upload.model.SelectedMedia
import com.example.photobomb.app.upload.utils.MultipartUtils
import com.google.gson.Gson
import retrofit2.Response

class UploadRepository(

    private val api: UploadApi

) {

    suspend fun createUploadSessions(

        media: List<SelectedMedia>

    ): List<UploadSessionResponse> {

        val response =
            api.createBulkUploadSessions(

                BulkCreateUploadSessionRequest(

                    media.map {

                        CreateUploadSessionDto(

                            filename =
                                it.displayName
                                    ?: "Unknown",

                            file_size =
                                it.size,

                            mime_type =
                                it.mimeType
                                    ?: "application/octet-stream",
                        )
                    }
                )
            )

        if (!response.isSuccessful) {

            val errorBody = response.errorBody()?.string()

            val message = try {
                Gson()
                    .fromJson(errorBody, ApiError::class.java)
                    .detail
            } catch (_: Exception) {
                errorBody
            }

            throw RuntimeException(
                message ?: "Unable to create upload sessions."
            )
        }

        return response.body()!!.sessions
    }

    suspend fun uploadFile(

        context: Context,

        media: SelectedMedia,

        session: UploadSessionResponse,

        onProgress: (Int) -> Unit

        ): UploadResult {

        Log.d("UPLOAD", "uploadFile() started for ${media.displayName}")

        val part =
            MultipartUtils.createPart(

                context,

                media.uri,

                media.displayName
                    ?: "Unknown",

                media.size,

                media.mimeType
                    ?: "application/octet-stream",

                onProgress
            )

        val response =
            api.uploadFile(

                session.upload_session_id,

                part,
            )

        if (!response.isSuccessful) {

            val error =
                Gson().fromJson(
                    response.errorBody()
                        ?.charStream(),
                    ApiError::class.java
                )

            throw RuntimeException(
                error.detail
            )
        }

        return response.body()
            ?: throw RuntimeException(
                "Empty response"
            )
    }
}