package com.example.photobomb.app.upload.api

import com.example.photobomb.app.upload.dto.BulkCreateUploadSessionRequest
import com.example.photobomb.app.upload.dto.BulkUploadSessionResponse
import com.example.photobomb.app.upload.dto.UploadResult
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path

interface UploadApi {

    @POST("api/v1/media/upload-sessions/bulk")
    suspend fun createBulkUploadSessions(
        @Body
        request:
        BulkCreateUploadSessionRequest

    ): Response<BulkUploadSessionResponse>

    @Multipart
    @POST("api/v1/media/upload-sessions/{sessionId}/file")
    suspend fun uploadFile(

        @Path("sessionId")
        sessionId: String,

        @Part
        file: MultipartBody.Part,

        ): Response<UploadResult>
}