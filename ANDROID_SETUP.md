# Android Setup Guide for SAM

## Prerequisites
- Android Studio (Latest)
- Android SDK 24+
- Java 11+
- Gradle 8.0+

## Installation Steps

### 1. Open Android Studio
```bash
# Clone repository
git clone https://github.com/cchinonso313-gif/SAM-AI-Assistant.git
cd SAM-AI-Assistant/android
```

### 2. Open Project
- Launch Android Studio
- Select "Open" → Navigate to `SAM-AI-Assistant/android`
- Wait for Gradle sync to complete

### 3. Configure API Keys
Create `local.properties`:
```properties
gemini_api_key=YOUR_GEMINI_API_KEY
groq_api_key=YOUR_GROQ_API_KEY
```

### 4. Build Project
```bash
# In Android Studio terminal
./gradlew build
```

### 5. Run on Device/Emulator
- Connect Android device or start emulator
- Click "Run" or press Shift+F10

## Project Structure
```
android/
├── app/
│   ├── build.gradle
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/com/sam/ai/
│   │   │   ├── MainActivity.kt
│   │   │   ├── services/
│   │   │   │   ├── AIService.kt
│   │   │   │   └── VoiceService.kt
│   │   │   └── models/
│   │   └── res/
│   │       ├── layout/
│   │       ├── values/
│   │       └── drawable/
│   └── build.gradle
└── build.gradle
```

## Permissions Requested
- INTERNET - API communication
- RECORD_AUDIO - Voice input
- CAMERA - Optional for future features
- READ/WRITE_EXTERNAL_STORAGE - File operations

## Testing on Emulator
1. Create AVD (Android Virtual Device)
2. Select API Level 24+
3. Start emulator
4. Build and run app

## Troubleshooting

### Gradle Sync Issues
```bash
./gradlew clean
./gradlew build
```

### API Key Errors
- Verify keys in local.properties
- Check internet connection
- Ensure API quotas not exceeded

### Voice Recognition Not Working
- Check microphone permissions
- Verify device has Google Play Services
- Test on actual device (not emulator)

## Features
- Voice input/output
- Real-time AI responses
- Conversation history
- System integration

## Next Steps
- Customize UI in `res/layout/activity_main.xml`
- Add custom AI tasks in AIService
- Build production APK: `./gradlew assembleRelease`
