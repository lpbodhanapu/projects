package com.example.findyourflower

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import com.example.findyourflower.databinding.ActivityModelSelectionBinding

class ModelSelectionActivity : AppCompatActivity() {
    lateinit var binding: ActivityModelSelectionBinding
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityModelSelectionBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.mobilenet.setOnClickListener{
            val intent = Intent(this,FindFlowerActivity::class.java)
            intent.putExtra("ModelPath","mobilenet.tflite")
            intent.putExtra("Title", "Mobilenet")
            startActivity(intent)
        }
        binding.vgg.setOnClickListener{
            val intent = Intent(this,FindFlowerActivity::class.java)
            intent.putExtra("ModelPath","VGGModel.tflite")
            intent.putExtra("Title","VGG")
            startActivity(intent)
        }

    }
    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.about, menu)
        return true
    }
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_about -> {
                startActivity(Intent(this,AboutActivity::class.java))
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }
}