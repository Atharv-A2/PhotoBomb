package com.example.photobomb.app.presentation.gallery

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.paging.PagingDataAdapter
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import coil.load
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.databinding.ItemGalleryBinding

class GalleryAdapter(

    private val onClick:
        (GalleryItemUiModel) -> Unit

) : PagingDataAdapter<GalleryItemUiModel, GalleryAdapter.ViewHolder>(DIFF) {

    companion object {

        val DIFF =

            object :
                DiffUtil.ItemCallback<
                        GalleryItemUiModel>() {

                override fun areItemsTheSame(

                    oldItem: GalleryItemUiModel,

                    newItem: GalleryItemUiModel

                ) =
                    oldItem.id == newItem.id

                override fun areContentsTheSame(

                    oldItem: GalleryItemUiModel,

                    newItem: GalleryItemUiModel

                ) =
                    oldItem == newItem
            }
    }

    inner class ViewHolder(
        private val binding:
        ItemGalleryBinding
    ) : RecyclerView.ViewHolder(
        binding.root
    ) {

        fun bind(
            item:
            GalleryItemUiModel
        ) {

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
    ): ViewHolder {

        return ViewHolder(
            ItemGalleryBinding.inflate(
                LayoutInflater.from(
                    parent.context
                ),
                parent,
                false
            )
        )
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int
    ) {
        getItem(position)?.let {
            holder.bind(it)
        }
    }

}