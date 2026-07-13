package com.example.photobomb.app.upload.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.local.entity.UploadStatus
import com.example.photobomb.app.data.repository.UploadQueueRepository
import com.example.photobomb.app.upload.repository.UploadRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import java.io.IOException


class UploadStatusWorker(

    context: Context,

    params: WorkerParameters

) : CoroutineWorker(

    context,

    params
) {

    companion object {

        const val KEY_MEDIA_ID =
            "media_id"

        const val KEY_URI =
            "uri"

        private const val POLL_INTERVAL =
            2_000L
    }

    private val queue =

        UploadQueueRepository(

            DatabaseProvider

                .getDatabase(
                    applicationContext
                )

                .uploadQueueDao()
        )

    private val repository =

        UploadRepository(

            NetworkModule.uploadApi(
                applicationContext
            )
        )


    override suspend fun doWork(): Result {

        val mediaId =

            inputData.getString(
                KEY_MEDIA_ID
            )

                ?: return Result.failure()

        val uri =

            inputData.getString(
                KEY_URI
            )

                ?: return Result.failure()

        val entity =

            queue.get(uri)

                ?: return Result.failure()

        while (!isStopped) {

            coroutineContext.ensureActive()

            val response = try {
                repository.getMediaStatus(mediaId)
            } catch (e: IOException) {
                delay(POLL_INTERVAL)
                continue
            }

            when (response.status) {

                "PROCESSING" -> {
                    if (entity.status != UploadStatus.PROCESSING) {
                        entity.status = UploadStatus.PROCESSING
                        queue.save(entity)
                    }
                }

                "UPLOADING_TELEGRAM" -> {
                    if (entity.status != UploadStatus.UPLOADING_TELEGRAM) {
                        entity.status = UploadStatus.UPLOADING_TELEGRAM
                        queue.save(entity)
                    }
                }

                "AVAILABLE" -> {
                    entity.status = UploadStatus.COMPLETED
                    entity.progress = 100
                    queue.save(entity)
                    return Result.success()
                }

                "FAILED" -> {
                    entity.status = UploadStatus.FAILED
                    entity.errorMessage = "Backend processing failed."
                    queue.save(entity)
                    return Result.failure()
                }
            }

            delay(
                POLL_INTERVAL
            )
        }
        return Result.success()
    }
}