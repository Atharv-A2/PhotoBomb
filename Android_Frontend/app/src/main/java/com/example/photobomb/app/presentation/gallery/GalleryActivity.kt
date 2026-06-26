package com.example.photobomb.app.presentation.gallery

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.repository.GalleryRepository
import com.example.photobomb.app.presentation.viewer.ViewerActivity
import com.example.photobomb.databinding.ActivityGalleryBinding
import kotlinx.coroutines.launch

class GalleryActivity : AppCompatActivity() {

    private lateinit var binding: ActivityGalleryBinding

    private lateinit var adapter: GalleryAdapter

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
    }
}