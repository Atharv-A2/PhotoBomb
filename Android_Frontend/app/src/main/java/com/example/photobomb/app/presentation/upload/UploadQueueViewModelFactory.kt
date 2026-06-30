package com.example.photobomb.app.presentation.upload

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.photobomb.app.data.repository.UploadQueueRepository

class UploadQueueViewModelFactory(
    private val repository:
    UploadQueueRepository
) : ViewModelProvider.Factory {

    override fun <T : ViewModel>

            create(

        modelClass: Class<T>

    ): T {

        return UploadQueueViewModel(
            repository
        ) as T
    }
}