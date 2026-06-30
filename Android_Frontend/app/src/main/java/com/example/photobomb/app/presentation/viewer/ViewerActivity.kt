package com.example.photobomb.app.presentation.viewer

import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.annotation.OptIn
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.repository.ViewerRepository
import com.example.photobomb.databinding.ActivityViewerBinding
import kotlinx.coroutines.launch
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import coil.load
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.app.core.image.ImageLoaderFactory
import com.example.photobomb.app.core.media.MediaSourceFactory
import com.example.photobomb.app.data.repository.StreamRepository

class ViewerActivity :
    AppCompatActivity() {

    companion object {

        const val EXTRA_MEDIA_ID =
            "media_id"
    }

    private lateinit var binding:
            ActivityViewerBinding

    private var player:
            ExoPlayer? = null

    @OptIn(UnstableApi::class)
    override fun onCreate(
        savedInstanceState: Bundle?
    ) {

        super.onCreate(
            savedInstanceState
        )

        binding =
            ActivityViewerBinding.inflate(
                layoutInflater
            )

        setContentView(
            binding.root
        )

        val mediaId =
            intent.getStringExtra(
                EXTRA_MEDIA_ID
            ) ?: return

        val api =
            NetworkModule.viewerApi(
                applicationContext
            )

        val repository =
            ViewerRepository(
                api
            )

        val viewModel =
            ViewerViewModel(
                repository
            )

        val streamRepo =
            StreamRepository(
                NetworkModule.streamApi(
                    applicationContext
                )
            )

//        lifecycleScope.launch {
//
//            val body =
//                streamRepo.stream(
//                    mediaId
//                )
//
//            Log.d(
//                "STREAM_TEST",
//                body?.contentLength()
//                    .toString()
//            )
//
//        }

        lifecycleScope.launch {

            viewModel.uiState.collect {

                val media =
                    it.media
                        ?: return@collect

                val streamUrl =
                    "${ApiConstants.BASE_URL}" +
                            "api/v1/media/" +
                            media.id +
                            "/stream"

                if (media.media_type == "IMAGE") {

                    binding.videoViewer.visibility =
                        View.GONE

                    binding.imageViewer.visibility =
                        View.VISIBLE

                    binding.imageViewer.load(
                        streamUrl,
                        ImageLoaderFactory.get(
                            applicationContext
                        )
                    )

                } else {

                    binding.imageViewer.visibility =
                        View.GONE

                    binding.videoViewer.visibility =
                        View.VISIBLE

                    player?.release()

                    val dataSourceFactory =
                        MediaSourceFactory.create(
                            applicationContext
                        )

                    player =
                        ExoPlayer.Builder(
                            this@ViewerActivity
                        )
                            .setMediaSourceFactory(
                                DefaultMediaSourceFactory(
                                    dataSourceFactory
                                )
                            )
                            .build()

                    binding.videoViewer.player =
                        player

                    player?.setMediaItem(
                        MediaItem.fromUri(streamUrl)
                    )

                    player?.prepare()

                }

            }

        }

        viewModel.load(
            mediaId
        )
    }


    override fun onDestroy() {

        player?.release()

        player = null

        super.onDestroy()

    }
}