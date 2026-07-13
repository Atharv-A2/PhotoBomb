package com.example.photobomb.app.data.repository

import com.example.photobomb.app.data.local.dao.UploadQueueDao
import com.example.photobomb.app.data.local.entity.UploadQueueEntity
import com.example.photobomb.app.data.local.entity.UploadStatus

class UploadQueueRepository(

    private val dao:
    UploadQueueDao

) {

    suspend fun enqueue(

        items:
        List<UploadQueueEntity>

    ) {

        dao.insertAll(items)
    }

    suspend fun get(
        uri: String
    )=
        dao.get(uri)

    suspend fun save(
        entity: UploadQueueEntity
    ){

        dao.update(entity)
    }

    suspend fun retry(

        uri: String

    ) {
        val item =
            dao.get(uri)
                ?: return

        item.status =
            UploadStatus.QUEUED

        item.progress = 0

        item.errorMessage = null

        dao.update(item)
    }

    fun observeUploads() =

        dao.observe()


    suspend fun deleteUpload(
        uri: String
    ) {
        dao.delete(uri)
    }


    suspend fun deleteCompleted() {

        dao.deleteCompleted()
    }
}