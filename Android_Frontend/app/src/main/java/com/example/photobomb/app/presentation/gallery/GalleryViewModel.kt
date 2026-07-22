package com.example.photobomb.app.presentation.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.paging.cachedIn
import androidx.paging.insertSeparators
import androidx.paging.map
import com.example.photobomb.app.data.repository.GalleryRepository
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

class GalleryViewModel(

    private val repository: GalleryRepository

) : ViewModel() {

    private val DATE_FORMATTER =
        DateTimeFormatter.ofPattern(
            "EEE, d MMM, yyyy",
            Locale.ENGLISH
        )

    private fun LocalDate.toRelativeLabel(): String {

        val today = LocalDate.now()

        return when (ChronoUnit.DAYS.between(this, today)) {

            0L -> "Today"

            1L -> "Yesterday"

            in 2L..6L -> dayOfWeek.getDisplayName(
                java.time.format.TextStyle.FULL,
                Locale.ENGLISH
            )

            else -> format(DATE_FORMATTER)
        }
    }

    private val refreshTrigger =
        MutableSharedFlow<Unit>(replay = 1)


    val galleryPagingData =
        refreshTrigger
            .onStart { emit(Unit) }
            .flatMapLatest {

                repository.gallery()
                    .map { pagingData ->

                        pagingData
                            .map {
                                GalleryUiModel.Media(it)
                            }
                            .insertSeparators { before, after ->

                                if (after == null)
                                    return@insertSeparators null

                                val afterDate =
                                    after.item.captureTime
                                        ?.atZone(ZoneId.systemDefault())
                                        ?.toLocalDate()

                                val beforeDate =
                                    before?.item?.captureTime
                                        ?.atZone(ZoneId.systemDefault())
                                        ?.toLocalDate()

                                if (beforeDate != afterDate) {

                                    GalleryUiModel.Header(
                                        afterDate?.toRelativeLabel() ?: "Historical"
                                    )

                                } else {
                                    null
                                }
                            }
                    }
            }
            .cachedIn(viewModelScope)

    fun refreshGallery() {
        viewModelScope.launch {
            refreshTrigger.emit(Unit)
        }
    }
}