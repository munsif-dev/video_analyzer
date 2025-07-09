import os
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import pickle

class CacheManager:
    """Simple file-based cache for video processing results"""
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache settings
        self.default_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
        self.max_cache_size = 1000  # Maximum number of cached items
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.cache")
    
    def _get_metadata_path(self, cache_key: str) -> str:
        """Get metadata file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.meta")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        try:
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_metadata_path(cache_key)
            
            # Check if cache files exist
            if not os.path.exists(cache_path) or not os.path.exists(meta_path):
                return None
            
            # Load metadata
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            # Check if cache is expired
            created_at = datetime.fromisoformat(metadata['created_at'])
            ttl = metadata.get('ttl', self.default_ttl)
            
            if datetime.now() > created_at + timedelta(seconds=ttl):
                self.delete(key)
                return None
            
            # Load cached data
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Error reading from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set item in cache"""
        try:
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_metadata_path(cache_key)
            
            # Save data
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Save metadata
            metadata = {
                'key': key,
                'cache_key': cache_key,
                'created_at': datetime.now().isoformat(),
                'ttl': ttl or self.default_ttl,
                'size': os.path.getsize(cache_path)
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)
            
            # Clean up old cache if needed
            self._cleanup_old_cache()
            
            return True
            
        except Exception as e:
            print(f"Error writing to cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        try:
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_metadata_path(cache_key)
            
            if os.path.exists(cache_path):
                os.remove(cache_path)
            
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache') or filename.endswith('.meta'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def _cleanup_old_cache(self):
        """Clean up old cache items"""
        try:
            # Get all cache files
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    meta_path = os.path.join(self.cache_dir, filename)
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                    cache_files.append((meta_path, metadata))
            
            # Sort by creation time
            cache_files.sort(key=lambda x: x[1]['created_at'])
            
            # Remove oldest files if exceeding max cache size
            while len(cache_files) > self.max_cache_size:
                meta_path, metadata = cache_files.pop(0)
                self.delete(metadata['key'])
                
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            stats = {
                'total_items': 0,
                'total_size': 0,
                'expired_items': 0,
                'cache_dir': self.cache_dir
            }
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    meta_path = os.path.join(self.cache_dir, filename)
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                    
                    stats['total_items'] += 1
                    stats['total_size'] += metadata.get('size', 0)
                    
                    # Check if expired
                    created_at = datetime.fromisoformat(metadata['created_at'])
                    ttl = metadata.get('ttl', self.default_ttl)
                    
                    if datetime.now() > created_at + timedelta(seconds=ttl):
                        stats['expired_items'] += 1
            
            return stats
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'error': str(e)}

# Global cache instance
cache = CacheManager()

def cached_transcription(video_url: str, max_duration: int = 30):
    """Cache decorator for transcription results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"transcript_{video_url}_{max_duration}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=7*24*60*60)  # Cache for 7 days
            
            return result
        return wrapper
    return decorator

def cached_notes(transcript_hash: str, options: Dict):
    """Cache decorator for notes generation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            options_str = json.dumps(sorted(options.items()))
            cache_key = f"notes_{transcript_hash}_{hashlib.md5(options_str.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=7*24*60*60)  # Cache for 7 days
            
            return result
        return wrapper
    return decorator

def cached_embeddings(text_hash: str):
    """Cache decorator for embeddings"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"embeddings_{text_hash}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=30*24*60*60)  # Cache for 30 days
            
            return result
        return wrapper
    return decorator

def get_text_hash(text: str) -> str:
    """Get hash of text for caching"""
    return hashlib.md5(text.encode()).hexdigest()

def cleanup_expired_cache():
    """Clean up expired cache items"""
    try:
        for filename in os.listdir(cache.cache_dir):
            if filename.endswith('.meta'):
                meta_path = os.path.join(cache.cache_dir, filename)
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                
                # Check if expired
                created_at = datetime.fromisoformat(metadata['created_at'])
                ttl = metadata.get('ttl', cache.default_ttl)
                
                if datetime.now() > created_at + timedelta(seconds=ttl):
                    cache.delete(metadata['key'])
                    
    except Exception as e:
        print(f"Error cleaning expired cache: {e}")

# Performance monitoring
class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'transcription_times': [],
            'notes_generation_times': [],
            'embedding_times': [],
            'qa_response_times': []
        }
    
    def record_time(self, operation: str, duration: float):
        """Record operation time"""
        if operation in self.metrics:
            self.metrics[operation].append(duration)
    
    def get_avg_time(self, operation: str) -> float:
        """Get average time for operation"""
        times = self.metrics.get(operation, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        stats = {}
        for operation, times in self.metrics.items():
            if times:
                stats[operation] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
            else:
                stats[operation] = {
                    'avg': 0, 'min': 0, 'max': 0, 'count': 0
                }
        return stats

# Global performance monitor
performance_monitor = PerformanceMonitor()