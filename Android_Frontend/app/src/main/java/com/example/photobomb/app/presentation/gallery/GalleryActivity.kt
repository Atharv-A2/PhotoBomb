package com.example.photobomb.app.presentation.gallery

import android.os.Bundle
import android.util.Log
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.lifecycle.lifecycleScope
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

                NetworkModule.galleryApi(this),

                DatabaseProvider
                    .getDatabase(applicationContext)
                    .cachedMediaDao()
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

            lifecycleScope.launch {

                showUploads()
                UploadManager.enqueue(
                    this@GalleryActivity,
                    uris
                )
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
                this@GalleryActivity.adapter
        }

        binding.uploadSummaryView.root.setOnClickListener {

            UploadQueueBottomSheet()

                .show(

                    supportFragmentManager,

                    "uploads"
                )
        }

        viewModel.loadGallery()

        lifecycleScope.launch {

            viewModel.uiState.collect { state ->

                adapter.submit(

                    state.items.map {

                        GalleryItemUiModel(

                            id = it.id,

                            thumbnailId =
                                it.thumbnailId,

                            mediaType =
                                it.mediaType
                        )
                    }
                )
            }
        }

        lifecycleScope.launch {

            var lastCompletedCount = 0

            uploadViewModel.uiState.collect { state ->

                val uploading =
                    state.uploads.count {
                        it.status == UploadStatus.QUEUED || it.status == UploadStatus.UPLOADING
                    }

                val completedCount = state.uploads.count {
                    it.status == UploadStatus.COMPLETED
                }

                binding.uploadSummaryView.root.isVisible =
                    uploading > 0

                binding.uploadSummaryView.textSummary.text =
                    "Uploading $uploading items"

                if (completedCount > lastCompletedCount) {
                    lastCompletedCount = completedCount
                    viewModel.loadGallery()
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