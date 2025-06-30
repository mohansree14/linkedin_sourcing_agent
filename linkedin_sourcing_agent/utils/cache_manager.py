"""
Simple cache manager for LinkedIn sourcing agent.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple file-based cache manager for storing temporary data.
    """
    
    def __init__(self, cache_dir: str = "cache", ttl_seconds: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache entry has expired
            if time.time() - cache_data['timestamp'] > self.ttl_seconds:
                # Remove expired cache file
                os.remove(cache_file)
                return None
            
            return cache_data['value']
            
        except Exception as e:
            logger.warning(f"Failed to read cache for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            cache_data = {
                'value': value,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to write cache for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to delete cache for key {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to clear cache: {str(e)}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries cleaned up
        """
        cleaned_up = 0
        try:
            current_time = time.time()
            
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                cache_file = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if current_time - cache_data['timestamp'] > self.ttl_seconds:
                        os.remove(cache_file)
                        cleaned_up += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to process cache file {filename}: {str(e)}")
                    # Remove corrupted cache files
                    try:
                        os.remove(cache_file)
                        cleaned_up += 1
                    except:
                        pass
            
            if cleaned_up > 0:
                logger.info(f"Cleaned up {cleaned_up} expired cache entries")
            
            return cleaned_up
            
        except Exception as e:
            logger.warning(f"Failed to cleanup expired cache entries: {str(e)}")
            return 0
