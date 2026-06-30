package com.example.photobomb.app.upload.reader

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.example.photobomb.app.upload.model.SelectedMedia

object MediaReader {

    fun read(
        context: Context,
        uri: Uri,
    ): SelectedMedia {

        val resolver = context.contentResolver

        var name: String? = null
        var size = 0L

        resolver.query(
            uri,
            null,
            null,
            null,
            null,
        )?.use { cursor ->

            val nameIndex =
                cursor.getColumnIndex(
                    OpenableColumns.DISPLAY_NAME
                )

            val sizeIndex =
                cursor.getColumnIndex(
                    OpenableColumns.SIZE
                )

            if (cursor.moveToFirst()) {

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

        return SelectedMedia(

            uri = uri,

            displayName = name,

            mimeType =
                resolver.getType(uri),

            size = size,
        )
    }
}