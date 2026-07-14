package com.example.photobomb.app.presentation.upload

import android.content.Context
import android.text.format.Formatter
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.photobomb.R
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

                    context.getString(
                        R.string.upload_status_queued
                    )

                UploadStatus.UPLOADING ->

                    context.getString(
                        R.string.upload_status_uploading
                    )

                UploadStatus.PROCESSING ->

                    context.getString(
                        R.string.upload_status_processing
                    )

                UploadStatus.UPLOADING_TELEGRAM ->

                    context.getString(
                        R.string.upload_status_uploading_telegram
                    )

                UploadStatus.COMPLETED ->

                    context.getString(
                        R.string.upload_status_completed
                    )

                UploadStatus.FAILED ->

                    context.getString(
                        R.string.upload_status_failed
                    )
            }

            when (item.status) {

                UploadStatus.UPLOADING -> {

                    binding.progress.isIndeterminate = false

                    binding.progress.progress =
                        item.progress

                    val uploadedBytes =
                        item.size * item.progress / 100L

                    val uploaded =
                        Formatter.formatShortFileSize(
                            context,
                            uploadedBytes
                        )

                    val total =
                        Formatter.formatShortFileSize(
                            context,
                            item.size
                        )

                    binding.fileSize.text =
                        "$uploaded / $total"
                }

                UploadStatus.PROCESSING,

                UploadStatus.UPLOADING_TELEGRAM -> {

                    binding.progress.isIndeterminate = true

                    binding.fileSize.text =
                        context.getString(
                            R.string.upload_backend_processing
                        )
                }

                UploadStatus.COMPLETED -> {

                    binding.progress.isIndeterminate = false

                    binding.progress.progress = 100

                    binding.fileSize.text =
                        Formatter.formatShortFileSize(
                            context,
                            item.size
                        )
                }

                UploadStatus.QUEUED -> {

                    binding.progress.isIndeterminate = false

                    binding.progress.progress = 0

                    binding.fileSize.text =
                        Formatter.formatShortFileSize(
                            context,
                            item.size
                        )
                }

                UploadStatus.FAILED -> {

                    binding.progress.isIndeterminate = false

                    binding.progress.progress = 0

                    binding.fileSize.text =
                        Formatter.formatShortFileSize(
                            context,
                            item.size
                        )
                }
            }

            //For the Cancel Button Visibility
            val canCancel = item.status == UploadStatus.QUEUED ||
                    item.status == UploadStatus.UPLOADING ||
                    item.status == UploadStatus.FAILED

            binding.buttonCancel.visibility =
                if (canCancel) View.VISIBLE else View.GONE

            binding.buttonCancel.setOnClickListener(
                if (canCancel) {
                    View.OnClickListener { onCancel(item) }
                } else null
            )

            //For the Retry Button Visibility
            val hasFailed = item.status == UploadStatus.FAILED

            binding.errorMessage.visibility =
                if (hasFailed) View.VISIBLE else View.GONE

            binding.buttonRetry.visibility =
                if (hasFailed) View.VISIBLE else View.GONE

            binding.errorMessage.text = item.errorMessage

            binding.buttonRetry.setOnClickListener(
                if (hasFailed) {
                    View.OnClickListener { onRetry(item) }
                } else null
            )
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