package com.example.photobomb.app.upload.reader

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.example.photobomb.app.upload.model.SelectedMedia
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object MediaReader {

    fun read(
        context: Context,
        uri: Uri,
    ): SelectedMedia {

        val resolver = context.contentResolver

        var name: String? = null
        var size = 0L
        var lastModified: Long = 0

        resolver.query(
            uri,
            null,
            null,
            null,
            null,
        )?.use { cursor ->

            if (cursor.moveToFirst()) {

                val nameIndex =
                    cursor.getColumnIndex(
                        OpenableColumns.DISPLAY_NAME
                    )

                val sizeIndex =
                    cursor.getColumnIndex(
                        OpenableColumns.SIZE
                    )

                val modifiedIndex =
                    cursor.getColumnIndex("last_modified")

                if (modifiedIndex >= 0 && !cursor.isNull(modifiedIndex)) {
                    lastModified = cursor.getLong(modifiedIndex)
                }

                if (nameIndex >= 0) {
                    name =
                        cursor.getString(
                            nameIndex
                        )
                }

                if (sizeIndex >= 0) {
                    size =
                        cursor.getLong(
                            sizeIndex
                        )
                }
            }
        }

        //sending the last_modified timestamp directly from android
        val formatter =
            SimpleDateFormat(
                "yyyy-MM-dd HH:mm:ss",
                Locale.getDefault()
            )

        val formattedLastModifiedDate =
            formatter.format(Date(lastModified))

        return SelectedMedia(

            uri = uri,

            displayName = name,

            mimeType =
                resolver.getType(uri),

            size = size,

            lastModified = formattedLastModifiedDate
        )
    }
}