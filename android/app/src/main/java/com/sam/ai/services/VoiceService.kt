package com.sam.ai.services

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.SpeechRecognizer
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class VoiceService : Service(), RecognitionListener {

    private val TAG = "VoiceService"
    private var speechRecognizer: SpeechRecognizer? = null
    private val serviceScope = CoroutineScope(Dispatchers.Main)

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "🎤 Voice Service Created")
        initializeSpeechRecognizer()
    }

    private fun initializeSpeechRecognizer() {
        serviceScope.launch {
            try {
                speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this@VoiceService)
                speechRecognizer?.setRecognitionListener(this@VoiceService)
                Log.d(TAG, "✅ Speech Recognizer Initialized")
            } catch (e: Exception) {
                Log.e(TAG, "❌ Error: ${e.message}")
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            "START_LISTENING" -> startListening()
            "STOP_LISTENING" -> stopListening()
        }
        return START_STICKY
    }

    private fun startListening() {
        Log.d(TAG, "👂 Starting to listen")
        // Implement speech recognition
    }

    private fun stopListening() {
        Log.d(TAG, "⏹️ Stopping listener")
        speechRecognizer?.stopListening()
    }

    // RecognitionListener methods
    override fun onReadyForSpeech(params: android.os.Bundle?) {
        Log.d(TAG, "Ready for speech")
    }

    override fun onBeginningOfSpeech() {
        Log.d(TAG, "Speech started")
    }

    override fun onRmsChanged(rmsdB: Float) {}

    override fun onBufferReceived(buffer: ByteArray?) {}

    override fun onEndOfSpeech() {
        Log.d(TAG, "Speech ended")
    }

    override fun onError(error: Int) {
        Log.e(TAG, "Speech error: $error")
    }

    override fun onResults(results: android.os.Bundle?) {
        Log.d(TAG, "Speech results received")
    }

    override fun onPartialResults(partialResults: android.os.Bundle?) {}

    override fun onEvent(eventType: Int, params: android.os.Bundle?) {}

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
        Log.d(TAG, "🛑 Voice Service Destroyed")
    }
}
