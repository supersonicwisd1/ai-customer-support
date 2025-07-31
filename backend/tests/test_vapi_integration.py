#!/usr/bin/env python3
"""
Test script for voice service functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.vapi_service import VapiService

# Load environment variables
load_dotenv()

async def test_voice_service():
    """Test the voice service functionality"""
    
    print("🎤 Testing Voice Service...")
    
    # Initialize voice service
    voice_service = VapiService()
    
    # Check if service is available
    if not voice_service.is_available():
        print("⚠️  Voice service not configured (missing OPENAI_API_KEY)")
        print("   To enable voice chat, set OPENAI_API_KEY in your .env file")
        return
    
    print("✅ Voice service configured and available")
    
    # Test voice info
    print("\n🔍 Testing voice information...")
    try:
        voice_info = await voice_service.get_voices()
        print(f"✅ Voice info retrieved:")
        print(f"   Available: {voice_info['available']}")
        print(f"   Supported voices: {voice_info['supported_voices']}")
        print(f"   Features: {voice_info['features']}")
    except Exception as e:
        print(f"❌ Error getting voice info: {e}")
    
    # Test text-to-speech
    print("\n🔍 Testing text-to-speech...")
    try:
        test_text = "Hello! This is a test of the Aven AI voice service. How can I help you today?"
        audio_data = await voice_service.text_to_speech(test_text, "alloy")
        print(f"✅ Text-to-speech successful: {len(audio_data)} bytes generated")
        
        # Save test audio file
        with open("test_speech.mp3", "wb") as f:
            f.write(audio_data)
        print("   Audio saved as test_speech.mp3")
        
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
    
    # Test supported voices
    print("\n🔍 Testing supported voices...")
    try:
        voices = await voice_service.get_voices()
        print(f"✅ Supported voices: {voices}")
        
        # Test each voice
        for voice in voices[:2]:  # Test first 2 voices to avoid rate limits
            try:
                test_text = f"This is a test using the {voice} voice."
                audio_data = await voice_service.text_to_speech(test_text, voice)
                print(f"   ✅ {voice} voice working: {len(audio_data)} bytes")
            except Exception as e:
                print(f"   ❌ {voice} voice error: {e}")
                
    except Exception as e:
        print(f"❌ Error testing voices: {e}")
    
    print("\n🎉 Voice service test completed!")
    print("\n📝 Note: Audio transcription testing requires actual audio files.")
    print("   You can test transcription using the API endpoints:")

if __name__ == "__main__":
    asyncio.run(test_voice_service())                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   