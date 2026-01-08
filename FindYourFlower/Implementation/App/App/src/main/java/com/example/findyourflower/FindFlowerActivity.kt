package com.example.findyourflower

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.content.res.AssetManager
import android.graphics.Bitmap
import android.os.Bundle
import android.provider.MediaStore
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.toDrawable
import com.bumptech.glide.Glide
import com.example.findyourflower.databinding.ActivityFindFlowerBinding
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel


class FindFlowerActivity : AppCompatActivity() {


    private lateinit var binding: ActivityFindFlowerBinding
    var imageBitmap: Bitmap?=null

    private lateinit var MODEL_PATH:String
    private val IMAGE_SIZE = 224
    private val NUM_CLASSES = 102

    private val REQUEST_IMAGE_CAPTURE = 1
    private val REQUEST_IMAGE_GALLERY = 2
    private val REQUEST_CAMERA_PERMISSION = 1001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFindFlowerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        MODEL_PATH = intent.getStringExtra("ModelPath")?:"mobilenet.tflite"
        val title = intent.getStringExtra("Title")
        binding.btnOpenCamera.setOnClickListener {
            openCamera()
        }

        binding.btnOpenGallery.setOnClickListener {
            openGallery()
        }

        binding.btnPredict.setOnClickListener{
            val (resultIndexArray,resultMaxArray) = predict()
            if(resultMaxArray[0]<20)
                showTryAgainAlert()
            else {
                val intent = Intent(this, ShowResultActivity::class.java)
                intent.putExtra("resultIndexArray", resultIndexArray)
                intent.putExtra("resultMaxArray", resultMaxArray)
                intent.putExtra("Title",title)
                startActivity(intent)
            }
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

    private fun showTryAgainAlert() {
        val builder = AlertDialog.Builder(this)
        builder.setTitle("Invalid Prediction")
        builder.setMessage("Sorry I couldn't recognize your image Please try again...! ")
        builder.setPositiveButton("OK") { dialog, _ ->
            dialog.dismiss()
        }

        // Create and show the dialog
        val dialog = builder.create()
        dialog.show()
    }

    private fun predict():Pair<ArrayList<Int>,ArrayList<Int>> {
        val assetManager = assets
        var predictedClassIndexArray = arrayListOf<Int>()
        var predictedClassMaxArray = arrayListOf<Int>()
        if (imageBitmap != null) {
            val resizedBitmap = Bitmap.createScaledBitmap(imageBitmap!!, 224, 224, true)
            val inputValues = preprocessImage(resizedBitmap)
            val tflite = Interpreter(loadModelFileFromAsset(assetManager,MODEL_PATH))
            val output = Array(1) { FloatArray(NUM_CLASSES) }
            tflite.run(inputValues, output)
            val result = argmax((output[0]))
            predictedClassIndexArray = result.first
            predictedClassMaxArray = result.second
        } else {
            Toast.makeText(this,"Invalid image",Toast.LENGTH_SHORT).show()
        }
        return Pair(predictedClassIndexArray,predictedClassMaxArray)
    }

    private fun preprocessImage(bitmap: Bitmap): ByteBuffer {
        val inputSize = 224
        val output = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3).apply {
            order(ByteOrder.nativeOrder())
        }

        val pixels = IntArray(inputSize * inputSize)
        bitmap.getPixels(pixels, 0, inputSize, 0, 0, inputSize, inputSize)

        for (pixel in pixels) {
            val r = (pixel shr 16 and 0xFF) / 255.0f
            val g = (pixel shr 8 and 0xFF) / 255.0f
            val b = (pixel and 0xFF) / 255.0f

            output.putFloat(r)
            output.putFloat(g)
            output.putFloat(b)
        }

        return output
    }

    private fun loadModelFileFromAsset(assetManager: AssetManager, modelFilename: String): ByteBuffer {
        val fileDescriptor = assetManager.openFd(modelFilename)
        val inputStream = fileDescriptor.createInputStream()
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength

        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    fun argmax(arr: FloatArray): Pair<ArrayList<Int>,ArrayList<Int>> {
        var firstMax = Float.NEGATIVE_INFINITY
        var secondMax = Float.NEGATIVE_INFINITY
        var thirdMax = Float.NEGATIVE_INFINITY

        var firstIndex = -1
        var secondIndex = -1
        var thirdIndex = -1

        for ((index, num) in arr.withIndex()) {
            if (num > firstMax) {
                thirdMax = secondMax
                thirdIndex = secondIndex
                secondMax = firstMax
                secondIndex = firstIndex
                firstMax = num
                firstIndex = index
            } else if (num > secondMax) {
                thirdMax = secondMax
                thirdIndex = secondIndex
                secondMax = num
                secondIndex = index
            } else if (num > thirdMax) {
                thirdMax = num
                thirdIndex = index
            }
        }
        val indexArray = arrayListOf<Int>(firstIndex,secondIndex,thirdIndex)
        val maxArray = arrayListOf<Int>((firstMax*100).toInt(),(secondMax*100).toInt(),(thirdMax*100).toInt())
        return Pair(indexArray,maxArray)
    }


    private fun openCamera() {
        if (ContextCompat.checkSelfPermission(
                this,android.Manifest.permission.CAMERA
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(android.Manifest.permission.CAMERA),
                REQUEST_CAMERA_PERMISSION
            )
        } else {
            startCamera()
        }
    }

    private fun startCamera() {
        val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        if (takePictureIntent.resolveActivity(packageManager) != null) {
            startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
        }
    }
    private fun openGallery() {
        val galleryIntent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        startActivityForResult(galleryIntent, REQUEST_IMAGE_GALLERY)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (resultCode == Activity.RESULT_OK) {
            when (requestCode) {
                REQUEST_IMAGE_CAPTURE -> {
                    imageBitmap = data?.extras?.get("data") as Bitmap
                    displayImage(imageBitmap!!)
                }
                REQUEST_IMAGE_GALLERY -> {
                    val imageUri = data?.data
                    imageUri?.let {
                        imageBitmap = MediaStore.Images.Media.getBitmap(this.contentResolver, it)
                        displayImage(imageBitmap!!)
                    }
                }
            }
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            REQUEST_CAMERA_PERMISSION -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    startCamera()
                }
            }
        }
    }

    private fun displayImage(bitmap: Bitmap) {
        Glide.with(this)
            .load(bitmap)
            .into(binding.imageView)
    }
}