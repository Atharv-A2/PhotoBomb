package com.example.photobomb.app.upload.worker

import android.content.Context
import android.net.Uri
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.upload.model.SelectedMedia
import com.example.photobomb.app.upload.reader.MediaReader
import com.example.photobomb.app.upload.repository.UploadRepository
import java.io.IOException
import androidx.core.net.toUri
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.local.entity.UploadStatus
import com.example.photobomb.app.data.repository.UploadQueueRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.launch

class MediaUploadWorker(

    context: Context,

    params: WorkerParameters

) : CoroutineWorker(
    context,
    params
) {

    companion object {

        const val KEY_URIS = "uris"
    }

    private val queue =
        UploadQueueRepository(

            DatabaseProvider
                .getDatabase(
                    applicationContext
                )
                .uploadQueueDao()
        )

    var hasFailures = false

    var lastProgress = -1

    override suspend fun doWork(): Result {

        return try {

            val uriStrings =
                inputData.getStringArray(
                    KEY_URIS
                ) ?: return Result.failure()

            val media =
                uriStrings.map {
                    MediaReader.read(
                        context = applicationContext,
                        uri = it.toUri(),
                    )
                }

            val repository =
                UploadRepository(
                    NetworkModule.uploadApi(
                        applicationContext
                    )
                )

            val sessions = try {

                repository.createUploadSessions(
                    media
                )

            } catch (e: Exception) {

                media.forEach { mediaItem ->

                    queue.get(
                        mediaItem.uri.toString()
                    )?.let { entity ->

                        entity.status =
                            UploadStatus.FAILED

                        entity.progress = 0

                        entity.retryCount =
                            runAttemptCount

                        entity.errorMessage =
                            e.message

                        queue.save(entity)
                    }
                }

                return Result.success()
            }

            for ((mediaItem, session) in media.zip(sessions)) {

                coroutineContext.ensureActive()

                val entity =
                    queue.get(
                        mediaItem.uri.toString()
                    )!!

                try {

                    entity.uploadSessionId =
                        session.upload_session_id

                    entity.status =
                        UploadStatus.UPLOADING

                    queue.save(entity)

                    val result = repository.uploadFile(

                        applicationContext,

                        mediaItem,

                        session,
                    ) { progress ->

                        if (progress != lastProgress) {

                            lastProgress = progress
                            entity.progress =
                                progress

                            CoroutineScope(Dispatchers.IO).launch {
                                queue.save(entity)
                            }
                        }
                    }

                    entity.mediaId =
                        result.media_id

                    entity.status =
                        UploadStatus.COMPLETED

                    entity.progress =
                        100

                    queue.save(entity)

                } catch(e: Exception){

                    entity.status =
                        UploadStatus.FAILED

                    entity.progress = 0

                    entity.retryCount =
                        runAttemptCount

                    entity.errorMessage =
                        e.message

                    queue.save(entity)

                    hasFailures = true

                    break
                }
            }

            Result.success()

        } catch (e: IOException) {
            hasFailures = true
            Result.retry()
        } catch (e: Exception) {
            hasFailures = true
            Result.failure()
        }
    }

}