package com.example.photobomb.app.presentation.gallery

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.paging.PagingDataAdapter
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import coil.load
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.databinding.ItemGalleryBinding
import com.example.photobomb.databinding.ItemMonthHeaderBinding

class GalleryAdapter(

    private val onClick:
        (GalleryItemUiModel) -> Unit

) : PagingDataAdapter<GalleryUiModel, RecyclerView.ViewHolder>(DIFF) {

    companion object {

        val DIFF =

            object : DiffUtil.ItemCallback<GalleryUiModel>() {

                override fun areItemsTheSame(
                    oldItem: GalleryUiModel,
                    newItem: GalleryUiModel
                ): Boolean {

                    return when {

                        oldItem is GalleryUiModel.Media &&
                                newItem is GalleryUiModel.Media ->
                            oldItem.item.id == newItem.item.id

                        oldItem is GalleryUiModel.Header &&
                                newItem is GalleryUiModel.Header ->
                            oldItem.title == newItem.title

                        else -> false
                    }
                }

                override fun areContentsTheSame(
                    oldItem: GalleryUiModel,
                    newItem: GalleryUiModel
                ) = oldItem == newItem
            }
        private const val TYPE_HEADER = 0
        private const val TYPE_MEDIA = 1
    }


    override fun getItemViewType(position: Int): Int {

        return when (getItem(position)) {

            is GalleryUiModel.Header -> TYPE_HEADER

            is GalleryUiModel.Media -> TYPE_MEDIA

            else -> TYPE_MEDIA
        }
    }


    class HeaderViewHolder(
        private val binding: ItemMonthHeaderBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(header: GalleryUiModel.Header) {

            binding.textMonth.text = header.title
        }
    }


    class MediaViewHolder(
        private val binding: ItemGalleryBinding,
        private val onClick: (GalleryItemUiModel) -> Unit
    ) : RecyclerView.ViewHolder(
        binding.root
    ) {

        fun bind(
            media:
            GalleryUiModel.Media
        ) {
            val item = media.item

            val url =
                "${ApiConstants.BASE_URL}" +
                        "api/v1/thumbnails/" +
                        item.thumbnailId

            binding.imageThumbnail.load(url) {

                crossfade(true)

                placeholder(
                    android.R.color.darker_gray
                )

                error(
                    android.R.color.darker_gray
                )
            }

            binding.videoSign.isVisible =
                item.mediaType.contains("video", ignoreCase = true)

            binding.root.setOnClickListener {
                onClick(
                    item
                )
            }
        }
    }

    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): RecyclerView.ViewHolder {

        return when (viewType) {

            TYPE_HEADER -> HeaderViewHolder(
                ItemMonthHeaderBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
            )

            else -> MediaViewHolder(
                ItemGalleryBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                ),
                onClick
            )
        }
    }
    override fun onBindViewHolder(
        holder: RecyclerView.ViewHolder,
        position: Int
    ) {

        when (val item = getItem(position)) {

            is GalleryUiModel.Header ->
                (holder as HeaderViewHolder).bind(item)

            is GalleryUiModel.Media ->
                (holder as MediaViewHolder).bind(item)

            null -> Unit
        }
    }

}