package com.example.photobomb.app.upload.picker

import android.content.Context
import android.net.Uri
import com.example.photobomb.app.upload.model.SelectedMedia
import com.example.photobomb.app.upload.reader.MediaReader

object MediaPicker {

    fun buildSelection(

        context: Context,

        uris: List<Uri>,
    ): List<SelectedMedia> {

        return uris.map { uri ->

            MediaReader.read(

                context = context,

                uri = uri,
            )
        }
    }
}