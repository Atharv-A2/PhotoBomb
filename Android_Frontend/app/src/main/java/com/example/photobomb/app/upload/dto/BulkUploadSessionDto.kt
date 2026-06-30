package com.example.photobomb.app.upload.dto

data class BulkCreateUploadSessionRequest(

    val files: List<
            CreateUploadSessionDto
            >
)

data class BulkUploadSessionResponse(

    val sessions:
    List<UploadSessionResponse>
)