package com.example.photobomb.app.presentation.upload

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.repository.UploadQueueRepository
import com.example.photobomb.app.upload.worker.UploadManager
import com.example.photobomb.databinding.FragmentUploadQueueBinding
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import kotlinx.coroutines.launch
import kotlin.getValue

class UploadQueueBottomSheet :
    BottomSheetDialogFragment() {

    private var _binding:
            FragmentUploadQueueBinding? = null

    private val binding
        get() = _binding!!

    private lateinit var adapter:
            UploadQueueAdapter

    private val viewModel: UploadQueueViewModel by activityViewModels {
        UploadQueueViewModelFactory(
            UploadQueueRepository(
                DatabaseProvider
                    .getDatabase(requireContext())
                    .uploadQueueDao()
            )
        )
    }

    override fun onCreateView(

        inflater: LayoutInflater,

        container: ViewGroup?,

        savedInstanceState: Bundle?

    ): View {

        _binding =
            FragmentUploadQueueBinding.inflate(
                inflater,
                container,
                false
            )

        return binding.root
    }

    override fun onViewCreated(

        view: View,

        savedInstanceState: Bundle?

    ) {

        adapter =
            UploadQueueAdapter {
                lifecycleScope.launch {

                    val repository =
                        UploadQueueRepository(
                            DatabaseProvider
                                .getDatabase(requireContext())
                                .uploadQueueDao()
                        )

                    val entity =
                        repository.get(
                            it.uri
                        ) ?: return@launch

                    UploadManager.retry(
                        requireContext(),
                        entity
                    )
                }
            }

        binding.recyclerUploads.apply {

            layoutManager =
                LinearLayoutManager(
                    requireContext()
                )

            adapter =
                this@UploadQueueBottomSheet.adapter
        }

        viewLifecycleOwner.lifecycleScope.launch {

            viewModel.uiState.collect {
                adapter.submit(
                    it.uploads
                )
            }
        }
    }

    override fun onDestroyView() {

        _binding = null

        super.onDestroyView()
    }
}