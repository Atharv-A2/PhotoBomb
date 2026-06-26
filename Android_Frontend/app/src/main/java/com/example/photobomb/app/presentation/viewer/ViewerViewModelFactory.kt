package com.example.photobomb.app.presentation.viewer

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.photobomb.app.data.repository.ViewerRepository

class ViewerViewModelFactory(

    private val repository:
    ViewerRepository

) : ViewModelProvider.Factory {

    override fun <T : ViewModel> create(

        modelClass: Class<T>

    ): T {

        return ViewerViewModel(
            repository
        ) as T

    }

}