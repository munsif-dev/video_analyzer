import requests
import time
from typing import Dict, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

class TranscriptionService:
    """Handle video transcription using YouTube Transcript API"""
    
    def __init__(self, api_key: str = None):
        # No API key needed for YouTube Transcript API
        pass
    
    def transcribe_video(self, video_url: str, max_duration: int = 30) -> Dict:
        """Main transcription method using YouTube Transcript API"""
        
        # Try YouTube transcript first (fastest and free)
        youtube_transcript = self._try_youtube_transcript(video_url)
        if youtube_transcript:
            return self._process_youtube_transcript(youtube_transcript, max_duration)
        
        # Return mock transcript for development/testing
        return self._create_mock_transcript(video_url)
    
    def _try_youtube_transcript(self, video_url: str) -> Optional[List]:
        """Try to get YouTube transcript directly"""
        try:
            # Extract video ID from URL
            video_id = self._extract_youtube_id(video_url)
            if not video_id:
                return None
            
            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
            
        except Exception as e:
            print(f"YouTube transcript failed: {e}")
            return None
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        try:
            if 'youtu.be' in url:
                return url.split('youtu.be/')[-1].split('?')[0]
            elif 'youtube.com' in url:
                if 'watch?v=' in url:
                    return url.split('watch?v=')[-1].split('&')[0]
                elif 'embed/' in url:
                    return url.split('embed/')[-1].split('?')[0]
            return None
        except:
            return None
    
    def _process_youtube_transcript(self, transcript: List, max_duration: int) -> Dict:
        """Process YouTube transcript data"""
        # Filter by duration
        filtered_transcript = []
        max_seconds = max_duration * 60
        
        for entry in transcript:
            if entry['start'] <= max_seconds:
                filtered_transcript.append(entry)
            else:
                break
        
        # Format transcript
        full_text = ' '.join([entry['text'] for entry in filtered_transcript])
        
        # Create timestamped segments
        segments = []
        current_segment = {'start': 0, 'end': 0, 'text': ''}
        
        for entry in filtered_transcript:
            if not current_segment['text']:
                current_segment['start'] = entry['start']
            
            current_segment['text'] += ' ' + entry['text']
            current_segment['end'] = entry['start'] + entry['duration']
            
            # Create new segment every ~30 seconds or ~200 words
            if (current_segment['end'] - current_segment['start'] > 30 or 
                len(current_segment['text'].split()) > 200):
                
                segments.append({
                    'start': self._format_timestamp(current_segment['start']),
                    'end': self._format_timestamp(current_segment['end']),
                    'text': current_segment['text'].strip()
                })
                
                current_segment = {'start': entry['start'], 'end': 0, 'text': ''}
        
        # Add final segment
        if current_segment['text']:
            segments.append({
                'start': self._format_timestamp(current_segment['start']),
                'end': self._format_timestamp(current_segment['end']),
                'text': current_segment['text'].strip()
            })
        
        return {
            'full_text': full_text,
            'segments': segments,
            'duration': self._format_timestamp(max_seconds if filtered_transcript else 0),
            'word_count': len(full_text.split()),
            'source': 'YouTube Transcript API'
        }
    
    
    def _create_mock_transcript(self, video_url: str) -> Dict:
        """Create a mock transcript for development/testing"""
        mock_text = """
        Welcome to this video! Today we'll be discussing the main topic which is very important 
        for understanding the concepts we'll cover. Let me start by explaining the background 
        and context of what we're about to learn.
        
        First, let's look at the fundamental principles. These are crucial because they form 
        the foundation of everything else we'll discuss. Without understanding these basics, 
        it would be difficult to grasp the more advanced concepts later.
        
        Now, let's move on to the practical applications. This is where things get interesting 
        because we can see how the theory actually works in real-world scenarios. I'll show 
        you several examples to illustrate these points.
        
        In conclusion, what we've learned today provides a solid foundation for further study. 
        The key takeaways are the main principles we discussed and how they apply to 
        practical situations. Thank you for watching!
        """
        
        segments = [
            {
                'start': '00:00',
                'end': '01:30',
                'text': 'Welcome to this video! Today we\'ll be discussing the main topic which is very important for understanding the concepts we\'ll cover. Let me start by explaining the background and context of what we\'re about to learn.'
            },
            {
                'start': '01:30',
                'end': '03:00',
                'text': 'First, let\'s look at the fundamental principles. These are crucial because they form the foundation of everything else we\'ll discuss. Without understanding these basics, it would be difficult to grasp the more advanced concepts later.'
            },
            {
                'start': '03:00',
                'end': '04:30',
                'text': 'Now, let\'s move on to the practical applications. This is where things get interesting because we can see how the theory actually works in real-world scenarios. I\'ll show you several examples to illustrate these points.'
            },
            {
                'start': '04:30',
                'end': '06:00',
                'text': 'In conclusion, what we\'ve learned today provides a solid foundation for further study. The key takeaways are the main principles we discussed and how they apply to practical situations. Thank you for watching!'
            }
        ]
        
        return {
            'full_text': mock_text.strip(),
            'segments': segments,
            'duration': '06:00',
            'word_count': len(mock_text.split()),
            'source': 'Mock Transcript (Development)'
        }
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to MM:SS or HH:MM:SS format"""
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return [
            'YouTube (youtube.com, youtu.be) - Free transcript via YouTube API',
            'Other platforms - Mock transcript for development'
        ]
    
    def estimate_transcription_time(self, video_duration: str) -> str:
        """Estimate transcription time based on video duration"""
        try:
            # Parse duration
            parts = video_duration.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
            elif len(parts) == 3:
                minutes = int(parts[0]) * 60 + int(parts[1])
            else:
                return "2-5 minutes"
            
            # Estimate based on duration
            if minutes <= 5:
                return "30 seconds - 1 minute"
            elif minutes <= 15:
                return "1-3 minutes"
            elif minutes <= 30:
                return "3-8 minutes"
            else:
                return "8-15 minutes"
                
        except:
            return "2-5 minutes"