package com.example.photobomb.app.presentation.viewer

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.annotation.OptIn
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import androidx.lifecycle.lifecycleScope
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.ui.PlayerView
import coil.load
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.app.core.image.ImageLoaderFactory
import com.example.photobomb.app.core.media.MediaSourceFactory
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.datastore.AuthPreferences
import com.example.photobomb.app.data.dto.viewer.MediaDetailResponse
import com.example.photobomb.app.data.repository.ViewerRepository
import com.example.photobomb.databinding.ActivityViewerBinding
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

class ViewerActivity :
    AppCompatActivity() {

    companion object {

        const val EXTRA_MEDIA_ID =
            "media_id"
    }

    private var currentMedia: MediaDetailResponse? = null

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
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = android.graphics.Color.TRANSPARENT

        binding =
            ActivityViewerBinding.inflate(
                layoutInflater
            )

        setContentView(
            binding.root
        )
        ViewCompat.setOnApplyWindowInsetsListener(binding.infoBar) { view, insets ->
            val statusBarInsets = insets.getInsets(WindowInsetsCompat.Type.statusBars())

            view.updatePadding(
                top = statusBarInsets.top + 4
            )

            insets
        }


        binding.ivBack.setOnClickListener {
            onBackPressedDispatcher.onBackPressed()
        }

        binding.infoBar.post {
            binding.infoBar.translationY = 0f
            binding.infoBar.alpha = 1f
        }

        binding.imageViewer.setOnClickListener {
            toggleInfoBar()
        }

        binding.videoViewer.setControllerVisibilityListener(
            PlayerView.ControllerVisibilityListener {
                visibility -> setInfoBarVisible(visibility == View.VISIBLE)
            }
        )

        val mediaId =
            intent.getStringExtra(
                EXTRA_MEDIA_ID
            ) ?: return

        val api =
            NetworkModule.viewerApi(
                applicationContext
            )

        val authPreferences =
            AuthPreferences(
                applicationContext
            )

        val repository =
            ViewerRepository(
                api,
                applicationContext,
                authPreferences
            )

        val viewModel =
            ViewerViewModel(
                repository
            )

        binding.btnDownload.setOnClickListener {

            currentMedia?.let { media ->

                viewModel.download(
                    media
                )

                Toast.makeText(
                    this,
                    "Downloading...",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

        lifecycleScope.launch {

            viewModel.uiState.collect {

                val media =
                    it.media
                        ?: return@collect

                currentMedia = media

                val (date, time) = formatDateTime(media.capture_time.toString())

                binding.tvDate.text = date
                binding.tvTime.text = time

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

                    binding.loadingSpinner.visibility = View.VISIBLE

                    binding.imageViewer.load(
                        streamUrl,
                        ImageLoaderFactory.get(applicationContext)
                    ) {
                        listener(
                            onSuccess = { _, _ ->
                                binding.loadingSpinner.visibility = View.GONE
                            },
                            onError = { _, _ ->
                                binding.loadingSpinner.visibility = View.GONE
                            }
                        )
                    }

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

                    binding.loadingSpinner.visibility = View.VISIBLE

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

                    player?.addListener(object : Player.Listener {

                        override fun onPlaybackStateChanged(state: Int) {
                            when (state) {
                                Player.STATE_BUFFERING -> {
                                    binding.loadingSpinner.visibility = View.VISIBLE
                                }

                                Player.STATE_READY -> {
                                    binding.loadingSpinner.visibility = View.GONE
                                }

                                Player.STATE_ENDED -> {
                                    binding.loadingSpinner.visibility = View.GONE
                                }
                            }
                        }

                        override fun onPlayerError(error: PlaybackException) {
                            binding.loadingSpinner.visibility = View.GONE
                        }
                    })

                    binding.videoViewer.player =
                        player

                    player?.setMediaItem(
                        MediaItem.fromUri(streamUrl)
                    )

                    player?.prepare()

                    setInfoBarVisible(false)

                }

            }

        }

        lifecycleScope.launch {

            viewModel.downloadComplete.collect { completed ->

                when (completed) {

                    true -> {
                        Toast.makeText(
                            this@ViewerActivity,
                            "Downloaded",
                            Toast.LENGTH_SHORT
                        ).show()
                    }

                    false -> {
                        Toast.makeText(
                            this@ViewerActivity,
                            "Download failed",
                            Toast.LENGTH_SHORT
                        ).show()
                    }

                    null -> {}
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

    fun formatDateTime(input: String): Pair<String, String> {
        val instant = Instant.parse(input)
        val dateTime = instant.atZone(ZoneId.systemDefault())

        val dateFormatter = DateTimeFormatter.ofPattern("dd MMMM yyyy", Locale.ENGLISH)
        val timeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss")

        val formattedDate = dateTime.format(dateFormatter)
        val formattedTime = dateTime.format(timeFormatter)

        return Pair(formattedDate, formattedTime)
    }

    private var isInfoBarVisible = true

    private fun setInfoBarVisible(visible: Boolean) {
        if (isInfoBarVisible == visible) return

        isInfoBarVisible = visible

        binding.infoBar.animate()
            .translationY(
                if (visible) 0f else -binding.infoBar.height.toFloat()
            )
            .alpha(
                if (visible) 1f else 0f
            )
            .setDuration(250)
            .start()
    }

    private fun toggleInfoBar() {
        setInfoBarVisible(!isInfoBarVisible)
    }
}