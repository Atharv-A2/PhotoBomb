package com.example.photobomb.app.presentation.upload

import android.content.Context
import android.text.format.Formatter
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.photobomb.app.data.local.entity.UploadStatus
import com.example.photobomb.databinding.ItemUploadQueueBinding

class UploadQueueAdapter(

    private val onRetry: (UploadQueueItem) -> Unit,

    private val onCancel: (UploadQueueItem) -> Unit

) : RecyclerView.Adapter<
        UploadQueueAdapter.ViewHolder>() {

    private val items =
        mutableListOf<UploadQueueItem>()

    fun submit(

        data: List<UploadQueueItem>

    ) {

        items.clear()

        items.addAll(data)

        notifyDataSetChanged()
    }

    inner class ViewHolder(

        private val binding:
        ItemUploadQueueBinding

    ) :

        RecyclerView.ViewHolder(
            binding.root
        ) {

        fun bind(

            item:
            UploadQueueItem

        ) {

            val uploadedBytes = item.size * item.progress / 100L
            val context = itemView.context

            val uploaded =
                Formatter.formatShortFileSize(context, uploadedBytes)

            val total =
                Formatter.formatShortFileSize(context, item.size)

            binding.fileSize.text = "$uploaded / $total"

            binding.filename.text = item.filename

            binding.progress.progress = item.progress


            binding.status.text = when (item.status) {

                UploadStatus.QUEUED ->
                    "Queued"

                UploadStatus.UPLOADING ->
                    "Uploading"

                UploadStatus.COMPLETED ->
                    "Completed"

                UploadStatus.FAILED ->
                    "Failed"

                else -> item.status.name

            }

            binding.buttonCancel.setOnClickListener {
                onCancel(item)
            }

            if (
                item.status ==
                UploadStatus.FAILED
            ) {

                binding.errorMessage.visibility = View.VISIBLE

                binding.buttonRetry.visibility = View.VISIBLE

                binding.errorMessage.text = item.errorMessage

                binding.buttonRetry.setOnClickListener {
                    onRetry(item)
                }

            } else {

                binding.errorMessage.visibility = View.GONE

                binding.buttonRetry.visibility = View.GONE
            }
        }
    }

    override fun onCreateViewHolder(

        parent: ViewGroup,

        viewType: Int

    ) =

        ViewHolder(

            ItemUploadQueueBinding.inflate(

                LayoutInflater.from(
                    parent.context
                ),

                parent,

                false
            )
        )

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