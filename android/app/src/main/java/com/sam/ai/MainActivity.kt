package com.sam.ai

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.sam.ai.services.AIService
import com.sam.ai.services.VoiceService
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var responseText: TextView
    private lateinit var voiceButton: Button
    private lateinit var stopButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize views
        statusText = findViewById(R.id.status_text)
        responseText = findViewById(R.id.response_text)
        voiceButton = findViewById(R.id.voice_button)
        stopButton = findViewById(R.id.stop_button)

        // Setup listeners
        voiceButton.setOnClickListener {
            startListening()
        }

        stopButton.setOnClickListener {
            stopListening()
        }

        // Start AI Service
        startAIService()
    }

    private fun startAIService() {
        lifecycleScope.launch {
            val intent = Intent(this@MainActivity, AIService::class.java)
            startService(intent)
            updateStatus("🤖 SAM Ready")
        }
    }

    private fun startListening() {
        lifecycleScope.launch {
            val intent = Intent(this@MainActivity, VoiceService::class.java)
            intent.action = "START_LISTENING"
            startService(intent)
            updateStatus("🎤 Listening...")
        }
    }

    private fun stopListening() {
        lifecycleScope.launch {
            val intent = Intent(this@MainActivity, VoiceService::class.java)
            intent.action = "STOP_LISTENING"
            startService(intent)
            updateStatus("⏹️ Stopped")
        }
    }

    private fun updateStatus(status: String) {
        runOnUiThread {
            statusText.text = status
        }
    }

    private fun updateResponse(response: String) {
        runOnUiThread {
            responseText.text = response
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        stopListening()
    }
}
