#!/usr/bin/env python3
"""
Demo script to test the Video Content Analyzer without full UI
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from services.video_processor import VideoProcessor
from services.transcription_service import TranscriptionService
from services.notes_generator import NotesGenerator
from services.rag_system import RAGSystem

def demo_video_processing():
    """Demo video processing workflow"""
    print("🎥 Video Content Analyzer Demo")
    print("=" * 50)
    
    # Initialize services
    print("1. Initializing services...")
    video_processor = VideoProcessor()
    transcription_service = TranscriptionService()
    
    # Test video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"2. Processing video: {test_url}")
    
    # Extract video info
    video_info = video_processor.extract_video_info(test_url)
    print(f"   Title: {video_info.get('title', 'Unknown')}")
    print(f"   Platform: {video_info.get('platform', 'Unknown')}")
    print(f"   Duration: {video_info.get('duration', 'Unknown')}")
    
    # Get transcript (will use mock for demo)
    print("3. Generating transcript...")
    transcript = transcription_service.transcribe_video(test_url)
    print(f"   Transcript length: {len(transcript['full_text'])} characters")
    print(f"   Segments: {len(transcript['segments'])}")
    print(f"   Source: {transcript['source']}")
    
    # Show first segment
    if transcript['segments']:
        first_segment = transcript['segments'][0]
        print(f"   First segment: {first_segment['text'][:100]}...")
    
    print("\n✓ Demo completed successfully!")
    print("\nTo run the full application:")
    print("1. Copy .env.example to .env")
    print("2. Add your free Groq API key from console.groq.com")
    print("3. Run: uv run streamlit run app.py")
    print("\nNote: All services are now FREE!")
    print("- Groq API: Free LLM inference")
    print("- Embeddings: Local sentence-transformers")
    print("- Transcription: YouTube Transcript API")

def demo_notes_generation():
    """Demo notes generation with mock data"""
    print("\n4. Testing notes generation...")
    
    # Mock transcript data
    mock_transcript = {
        'full_text': "This is a sample video about artificial intelligence and machine learning. We'll cover the basics of neural networks, deep learning, and practical applications.",
        'segments': [
            {
                'start': '00:00',
                'end': '00:30',
                'text': "Welcome to this tutorial on artificial intelligence and machine learning."
            },
            {
                'start': '00:30', 
                'end': '01:00',
                'text': "Today we'll explore neural networks and their applications."
            }
        ],
        'source': 'Mock'
    }
    
    mock_video_info = {
        'title': 'AI and Machine Learning Tutorial',
        'platform': 'YouTube',
        'duration': '10:00'
    }
    
    # Test without API key (will use fallback)
    notes_generator = NotesGenerator(api_key="mock_key")
    
    try:
        # This will fail gracefully and create fallback notes
        notes = notes_generator._create_fallback_notes(
            mock_transcript['full_text'], 
            mock_video_info
        )
        
        print(f"   Generated {len(notes['sections'])} sections")
        print(f"   Main theme: {notes['main_theme']}")
        print(f"   Topics: {notes['topics']}")
        
    except Exception as e:
        print(f"   Notes generation test: {e}")

def demo_supported_platforms():
    """Demo supported platforms"""
    print("\n5. Supported platforms:")
    
    video_processor = VideoProcessor()
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ", 
        "https://vimeo.com/123456789",
        "https://www.dailymotion.com/video/x123456",
        "https://www.twitch.tv/videos/123456789"
    ]
    
    for url in test_urls:
        is_valid = video_processor.validate_url(url)
        print(f"   {url}: {'✓' if is_valid else '✗'}")

def main():
    """Main demo function"""
    try:
        demo_video_processing()
        demo_notes_generation()
        demo_supported_platforms()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()