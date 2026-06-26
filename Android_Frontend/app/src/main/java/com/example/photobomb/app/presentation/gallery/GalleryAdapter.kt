package com.example.photobomb.app.presentation.gallery

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import coil.load
import com.example.photobomb.app.core.constants.ApiConstants
import com.example.photobomb.databinding.ItemGalleryBinding

class GalleryAdapter(
    private val onClick: (GalleryItemUiModel) -> Unit
) :
    RecyclerView.Adapter<GalleryAdapter.ViewHolder>() {

    private val items =
        mutableListOf<GalleryItemUiModel>()

    fun submit(
        data:
        List<GalleryItemUiModel>
    ) {

        items.clear()

        items.addAll(data)
        Log.d(
            "GalleryAdapter",
            "Items = ${data.size}"
        )

        notifyDataSetChanged()
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

            binding.imageThumbnail.load(
                url
            )
            if (item.mediaType.lowercase().contains("video"))
                binding.videoSign.visibility = View.VISIBLE else View.GONE

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
        holder.bind(
            items[position]
        )
    }

    override fun getItemCount() =
        items.size
}