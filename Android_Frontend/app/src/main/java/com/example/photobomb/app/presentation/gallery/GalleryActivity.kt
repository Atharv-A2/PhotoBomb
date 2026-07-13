package com.example.photobomb.app.presentation.gallery

import android.os.Bundle
import android.util.Log
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.paging.LoadState
import androidx.recyclerview.widget.GridLayoutManager
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.local.entity.UploadStatus
import com.example.photobomb.app.data.repository.GalleryRepository
import com.example.photobomb.app.data.repository.UploadQueueRepository
import com.example.photobomb.app.presentation.upload.UploadQueueBottomSheet
import com.example.photobomb.app.presentation.upload.UploadQueueViewModel
import com.example.photobomb.app.presentation.upload.UploadQueueViewModelFactory
import com.example.photobomb.app.presentation.viewer.ViewerActivity
import com.example.photobomb.app.upload.worker.UploadManager
import com.example.photobomb.databinding.ActivityGalleryBinding
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class GalleryActivity : AppCompatActivity() {
    private lateinit var binding: ActivityGalleryBinding

    private lateinit var adapter: GalleryAdapter

    private val uploadViewModel:

            UploadQueueViewModel

            by viewModels {

                UploadQueueViewModelFactory(
                    UploadQueueRepository(
                        DatabaseProvider
                            .getDatabase(applicationContext)
                            .uploadQueueDao()
                    )
                )
            }

    private val viewModel: GalleryViewModel by viewModels {

        GalleryViewModelFactory(

            GalleryRepository(

                NetworkModule.galleryApi(this)
            )
        )
    }

    private val picker =
        registerForActivityResult(

            ActivityResultContracts
                .PickMultipleVisualMedia(
                    100
                )

        ) { uris ->

            if (uris.isEmpty()) {
                return@registerForActivityResult
            }

            lifecycleScope.launch {
                UploadManager.enqueue(
                    this@GalleryActivity,
                    uris
                )

                showUploads()
            }
        }

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        binding =
            ActivityGalleryBinding.inflate(
                layoutInflater
            )

        setContentView(binding.root)

        adapter =
            GalleryAdapter {
                val intent =
                    android.content.Intent(
                        this,
                        ViewerActivity::class.java
                    )

                intent.putExtra(
                    ViewerActivity.EXTRA_MEDIA_ID,
                    it.id
                )

                startActivity(
                    intent
                )
            }

        binding.recyclerGallery.apply {

            layoutManager =
                GridLayoutManager(
                    this@GalleryActivity,
                    3
                )

            adapter =
                this@GalleryActivity.adapter.withLoadStateFooter(
                    footer =
                        GalleryLoadStateAdapter {
                            this@GalleryActivity.adapter.retry()
                        }
                )
        }

        binding.uploadSummaryView.root.setOnClickListener {

            UploadQueueBottomSheet()

                .show(

                    supportFragmentManager,

                    "uploads"
                )
        }

        binding.swipeRefresh.setOnRefreshListener {
            adapter.refresh()
        }

        lifecycleScope.launch {

            adapter.loadStateFlow.collectLatest { loadState ->

                val isRefreshing = loadState.refresh is LoadState.Loading

                binding.galleryLoading.isVisible =
                    isRefreshing && adapter.itemCount == 0

                binding.swipeRefresh.isRefreshing =
                    isRefreshing && adapter.itemCount > 0

                if (loadState.refresh is LoadState.Error) {
                    binding.swipeRefresh.isRefreshing = false

                    android.widget.Toast.makeText(
                        this@GalleryActivity,
                        (
                                loadState.refresh
                                        as LoadState.Error
                                ).error.message,

                        android.widget.Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }

        lifecycleScope.launch {
            repeatOnLifecycle(
                Lifecycle.State.STARTED
            ) {
                viewModel.galleryPagingData.collectLatest {
                    adapter.submitData(it)
                }
            }
        }

        lifecycleScope.launch {

            uploadViewModel.uiState.collect { state ->

                val activeUploads =
                    state.uploads.count {

                        when (it.status) {
                            UploadStatus.QUEUED,
                            UploadStatus.UPLOADING,
                            UploadStatus.PROCESSING,
                            UploadStatus.UPLOADING_TELEGRAM -> true
                            UploadStatus.COMPLETED,
                            UploadStatus.FAILED -> false
                        }
                    }

                binding.uploadSummaryView.root.isVisible =
                    activeUploads > 0

                val uploading =
                    state.uploads.count {
                        it.status == UploadStatus.UPLOADING
                    }

                val processing =
                    state.uploads.count {
                        it.status == UploadStatus.PROCESSING
                    }

                val telegram =
                    state.uploads.count {
                        it.status == UploadStatus.UPLOADING_TELEGRAM
                    }

                val queued =
                    state.uploads.count {
                        it.status == UploadStatus.QUEUED
                    }

                binding.uploadSummaryView.textSummary.text =
                    when {
                        uploading > 0 -> "Uploading $uploading item(s)"
                        processing > 0 -> "Processing $processing item(s)"
                        telegram > 0 -> "Uploading to Telegram $telegram item(s)"
                        queued > 0 -> "Queued $queued item(s)"
                        else -> "Uploading"
                    }

                val completed = state.uploads.count {
                        it.status == UploadStatus.COMPLETED
                    }

                if (activeUploads == 0 && completed > 0) {
                    lifecycleScope.launch {
                        delay(500)
                        adapter.refresh()
                    }
                }
            }

        }

        binding.fabUpload.setOnClickListener {

            picker.launch(

                PickVisualMediaRequest(

                    ActivityResultContracts
                        .PickVisualMedia
                        .ImageAndVideo

                )
            )
        }
    }

    private fun showUploads() {

        val tag = "uploads"

        if (supportFragmentManager.findFragmentByTag(tag) == null) {

            UploadQueueBottomSheet()
                .show(
                    supportFragmentManager,
                    tag
                )
        }
    }
}