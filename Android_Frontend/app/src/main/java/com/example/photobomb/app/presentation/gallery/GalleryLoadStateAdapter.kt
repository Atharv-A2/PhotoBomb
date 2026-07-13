package com.example.photobomb.app.presentation.gallery

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.paging.LoadState
import androidx.paging.LoadStateAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.photobomb.databinding.ItemLoadStateBinding

class GalleryLoadStateAdapter(

    private val retry: () -> Unit

) : LoadStateAdapter<
        GalleryLoadStateAdapter.ViewHolder>() {

    inner class ViewHolder(

        private val binding:
        ItemLoadStateBinding

    ) : RecyclerView.ViewHolder(
        binding.root
    ) {

        fun bind(
            state: LoadState
        ) {

            binding.progress.isVisible =
                state is LoadState.Loading

            binding.buttonRetry.isVisible =
                state is LoadState.Error

            binding.textError.isVisible =
                state is LoadState.Error

            if (
                state is LoadState.Error
            ) {

                binding.textError.text =
                    state.error.message
            }

            binding.buttonRetry.setOnClickListener {

                retry()
            }
        }
    }

    override fun onBindViewHolder(

        holder: ViewHolder,

        loadState: LoadState

    ) {

        holder.bind(loadState)
    }

    override fun onCreateViewHolder(

        parent: ViewGroup,

        loadState: LoadState

    ): ViewHolder {

        return ViewHolder(

            ItemLoadStateBinding.inflate(

                LayoutInflater.from(
                    parent.context
                ),

                parent,

                false
            )
        )
    }
}