package com.example.photobomb

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.photobomb.app.core.network.NetworkModule
import com.example.photobomb.app.data.local.database.AppDatabase
import com.example.photobomb.app.data.local.database.DatabaseProvider
import com.example.photobomb.app.data.repository.GalleryRepository
import com.example.photobomb.app.presentation.gallery.GalleryActivity
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        startActivity(
            Intent(
                this,
                GalleryActivity::class.java
            )
        )
        finish()

    }
}