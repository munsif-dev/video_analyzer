import re
import requests
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional
import json

class VideoProcessor:
    """Handle video URL processing and metadata extraction"""
    
    def __init__(self):
        self.supported_platforms = {
            'youtube.com': self._process_youtube,
            'youtu.be': self._process_youtube,
            'vimeo.com': self._process_vimeo,
            'dailymotion.com': self._process_dailymotion,
            'twitch.tv': self._process_twitch
        }
    
    def extract_video_info(self, video_url: str) -> Dict:
        """Extract video information from URL"""
        try:
            parsed_url = urlparse(video_url)
            domain = parsed_url.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Find matching processor
            processor = None
            for platform, func in self.supported_platforms.items():
                if platform in domain:
                    processor = func
                    break
            
            if not processor:
                raise ValueError(f"Unsupported platform: {domain}")
            
            return processor(video_url, parsed_url)
            
        except Exception as e:
            return {
                'title': 'Unknown Video',
                'duration': 'Unknown',
                'platform': 'Unknown',
                'video_id': 'Unknown',
                'url': video_url,
                'error': str(e)
            }
    
    def _process_youtube(self, video_url: str, parsed_url) -> Dict:
        """Process YouTube video URL"""
        # Extract video ID
        video_id = None
        
        if 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path[1:]
        elif 'youtube.com' in parsed_url.netloc:
            if 'watch' in parsed_url.path:
                video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            elif 'embed' in parsed_url.path:
                video_id = parsed_url.path.split('/')[-1]
        
        if not video_id:
            raise ValueError("Could not extract YouTube video ID")
        
        # Try to get video info (basic implementation)
        try:
            # Use yt-dlp to get video info
            info = self._get_youtube_info_basic(video_id)
            return {
                'title': info.get('title', f'YouTube Video {video_id}'),
                'duration': info.get('duration', 'Unknown'),
                'platform': 'YouTube',
                'video_id': video_id,
                'url': video_url,
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'description': info.get('description', '')
            }
        except:
            # Fallback to basic info
            return {
                'title': f'YouTube Video {video_id}',
                'duration': 'Unknown',
                'platform': 'YouTube',
                'video_id': video_id,
                'url': video_url,
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            }
    
    def _get_youtube_info_basic(self, video_id: str) -> Dict:
        """Get basic YouTube video info"""
        # This is a simplified implementation
        # In production, you'd use YouTube Data API or yt-dlp
        
        # Try to extract from YouTube oEmbed API
        try:
            oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'duration': 'Unknown',  # oEmbed doesn't provide duration
                    'description': ''
                }
        except:
            pass
        
        return {
            'title': f'YouTube Video {video_id}',
            'duration': 'Unknown',
            'description': ''
        }
    
    def _process_vimeo(self, video_url: str, parsed_url) -> Dict:
        """Process Vimeo video URL"""
        # Extract video ID from path
        video_id = parsed_url.path.split('/')[-1]
        
        try:
            # Use Vimeo oEmbed API
            oembed_url = f'https://vimeo.com/api/oembed.json?url={video_url}'
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', f'Vimeo Video {video_id}'),
                    'duration': str(data.get('duration', 'Unknown')),
                    'platform': 'Vimeo',
                    'video_id': video_id,
                    'url': video_url,
                    'thumbnail': data.get('thumbnail_url', ''),
                    'description': data.get('description', '')
                }
        except:
            pass
        
        return {
            'title': f'Vimeo Video {video_id}',
            'duration': 'Unknown',
            'platform': 'Vimeo',
            'video_id': video_id,
            'url': video_url
        }
    
    def _process_dailymotion(self, video_url: str, parsed_url) -> Dict:
        """Process Dailymotion video URL"""
        # Extract video ID
        video_id = parsed_url.path.split('/')[-1]
        
        return {
            'title': f'Dailymotion Video {video_id}',
            'duration': 'Unknown',
            'platform': 'Dailymotion',
            'video_id': video_id,
            'url': video_url
        }
    
    def _process_twitch(self, video_url: str, parsed_url) -> Dict:
        """Process Twitch video URL"""
        # Extract video ID
        video_id = parsed_url.path.split('/')[-1]
        
        return {
            'title': f'Twitch Video {video_id}',
            'duration': 'Unknown',
            'platform': 'Twitch',
            'video_id': video_id,
            'url': video_url
        }
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is supported"""
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return False
            
            domain = parsed_url.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return any(platform in domain for platform in self.supported_platforms.keys())
            
        except:
            return False
    
    def get_video_download_url(self, video_url: str) -> Optional[str]:
        """Get direct download URL for video (if possible)"""
        try:
            video_info = self.extract_video_info(video_url)
            
            if video_info['platform'] == 'YouTube':
                # For YouTube, we'll use yt-dlp to get the audio stream
                # This is a placeholder - actual implementation would use yt-dlp
                return f"youtube:{video_info['video_id']}"
            
            return video_url
            
        except Exception as e:
            print(f"Error getting download URL: {e}")
            return None
    
    def estimate_processing_time(self, video_info: Dict) -> str:
        """Estimate processing time based on video duration"""
        duration = video_info.get('duration', 'Unknown')
        
        if duration == 'Unknown':
            return "2-5 minutes"
        
        # Simple estimation based on duration
        try:
            if isinstance(duration, str):
                # Parse duration string (e.g., "10:30" or "1:23:45")
                parts = duration.split(':')
                if len(parts) == 2:  # MM:SS
                    minutes = int(parts[0])
                elif len(parts) == 3:  # HH:MM:SS
                    minutes = int(parts[0]) * 60 + int(parts[1])
                else:
                    return "2-5 minutes"
            else:
                minutes = int(duration)
            
            if minutes <= 5:
                return "1-2 minutes"
            elif minutes <= 15:
                return "2-4 minutes"
            elif minutes <= 30:
                return "4-8 minutes"
            else:
                return "8-15 minutes"
                
        except:
            return "2-5 minutes"