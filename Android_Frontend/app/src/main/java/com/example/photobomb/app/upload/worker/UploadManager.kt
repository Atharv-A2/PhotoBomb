package com.example.photobomb.app.upload.worker

import android.content.Context
import android.net.Uri
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.Data
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.local.entity.UploadQueueEntity
import com.example.photobomb.app.data.local.entity.UploadStatus
import com.example.photobomb.app.data.repository.UploadQueueRepository
import com.example.photobomb.app.upload.reader.MediaReader
import kotlinx.coroutines.flow.first
import java.util.concurrent.TimeUnit
import androidx.core.net.toUri

object UploadManager {

    private const val KEY_URIS =
        MediaUploadWorker.KEY_URIS

    private fun enqueueWork(
        context: Context,
        uris: List<Uri>
    ) {
        for (uri in uris) {
            val request =
                OneTimeWorkRequestBuilder<MediaUploadWorker>()
                    .setConstraints(
                        Constraints.Builder()
                            .setRequiredNetworkType(
                                NetworkType.CONNECTED
                            )
                            .build()
                    )

                    .setInputData(
                        Data.Builder()
                            .putStringArray(
                                KEY_URIS,
                                arrayOf(uri.toString())
                            )
                            .build()
                    )
                    .setBackoffCriteria(
                        BackoffPolicy.EXPONENTIAL,
                        10,
                        TimeUnit.SECONDS
                    )
                    .build()

            WorkManager
                .getInstance(context)
                .enqueueUniqueWork(
                    "media_upload_${uri}",
                    ExistingWorkPolicy.REPLACE,
                    request
                )
        }
    }

    suspend fun enqueue(

        context: Context,

        uris: List<Uri>

    ) {

        val queueRepository =
            UploadQueueRepository(

                DatabaseProvider
                    .getDatabase(context)
                    .uploadQueueDao()
            )

        val media =
            uris.map {
                MediaReader.read(
                    context,
                    it
                )
            }

        queueRepository.enqueue(
            media.map {

                UploadQueueEntity(

                    uri = it.uri.toString(),

                    filename =
                        it.displayName ?: "Unknown",

                    mimeType =
                        it.mimeType ?: "",

                    size = it.size,

                    status = UploadStatus.QUEUED,

                    progress = 0,

                    retryCount = 0,

                    uploadSessionId = null,

                    mediaId = null
                )
            }
        )
        enqueueWork(context, uris)
    }

    suspend fun retry(

        context: Context,

        entity: UploadQueueEntity

    ) {

        val queueRepository =
            UploadQueueRepository(
                DatabaseProvider
                    .getDatabase(context)
                    .uploadQueueDao()
            )

        entity.status =
            UploadStatus.QUEUED

        entity.progress = 0

        entity.errorMessage = null

        entity.retryCount++

        queueRepository.save(entity)

        enqueueWork(
            context,
            listOf( entity.uri.toUri() )
        )
    }

    suspend fun cancel(
        context: Context,
        entity: UploadQueueEntity
    ) {
        WorkManager.getInstance(context)
            .cancelUniqueWork("media_upload_${entity.uri}")
    }
}