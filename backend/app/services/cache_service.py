import json
import logging
import os
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheService:
    """Comprehensive caching service for AI responses, embeddings, and search results"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache subdirectories
        self.response_cache_dir = self.cache_dir / "responses"
        self.embedding_cache_dir = self.cache_dir / "embeddings"
        self.search_cache_dir = self.cache_dir / "search"
        self.vector_cache_dir = self.cache_dir / "vectors"
        
        # Create cache directories
        for cache_subdir in [self.response_cache_dir, self.embedding_cache_dir, 
                        self.search_cache_dir, self.vector_cache_dir]:
            cache_subdir.mkdir(exist_ok=True)
        
        # Cache configuration
        self.cache_config = {
            "responses": {
                "ttl_hours": 24,  # Cache AI responses for 24 hours
                "max_size_mb": 100  # Max 100MB for response cache
            },
            "embeddings": {
                "ttl_hours": 168,  # Cache embeddings for 1 week
                "max_size_mb": 500  # Max 500MB for embedding cache
            },
            "search": {
                "ttl_hours": 6,    # Cache search results for 6 hours
                "max_size_mb": 50   # Max 50MB for search cache
            },
            "vectors": {
                "ttl_hours": 168,  # Cache vector search results for 1 week
                "max_size_mb": 200  # Max 200MB for vector cache
            }
        }
        
        logger.info(f"Cache service initialized with directory: {self.cache_dir}")
    
    def _generate_cache_key(self, data: str, prefix: str = "") -> str:
        """Generate a cache key from data"""
        # Create a hash of the data
        hash_object = hashlib.md5(data.encode('utf-8'))
        cache_key = hash_object.hexdigest()
        
        if prefix:
            cache_key = f"{prefix}_{cache_key}"
        
        return cache_key
    
    def _get_cache_file_path(self, cache_key: str, cache_type: str) -> Path:
        """Get the file path for a cache entry"""
        if cache_type == "response_cache_dir":
            cache_dir = self.response_cache_dir
        elif cache_type == "embedding_cache_dir":
            cache_dir = self.embedding_cache_dir
        elif cache_type == "search_cache_dir":
            cache_dir = self.search_cache_dir
        elif cache_type == "vector_cache_dir":
            cache_dir = self.vector_cache_dir
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
        return cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_data: Dict[str, Any], cache_type: str) -> bool:
        """Check if cache entry is still valid based on TTL"""
        if "timestamp" not in cache_data:
            return False
        
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        ttl_hours = self.cache_config[cache_type]["ttl_hours"]
        expiry_time = cache_time + timedelta(hours=ttl_hours)
        
        return datetime.utcnow() < expiry_time
    
    def _get_cache_size_mb(self, cache_dir: Path) -> float:
        """Get the size of cache directory in MB"""
        total_size = 0
        for file_path in cache_dir.rglob("*.json"):
            total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _cleanup_cache(self, cache_type: str):
        """Clean up expired cache entries and enforce size limits"""
        if cache_type == "responses":
            cache_dir = self.response_cache_dir
        elif cache_type == "embeddings":
            cache_dir = self.embedding_cache_dir
        elif cache_type == "search":
            cache_dir = self.search_cache_dir
        elif cache_type == "vectors":
            cache_dir = self.vector_cache_dir
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
            
        max_size_mb = self.cache_config[cache_type]["max_size_mb"]
        ttl_hours = self.cache_config[cache_type]["ttl_hours"]
        
        current_time = datetime.utcnow()
        expired_files = []
        file_times = []
        
        # Find expired files and collect file times
        for file_path in cache_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)
                
                if "timestamp" in cache_data:
                    cache_time = datetime.fromisoformat(cache_data["timestamp"])
                    expiry_time = cache_time + timedelta(hours=ttl_hours)
                    
                    if current_time > expiry_time:
                        expired_files.append(file_path)
                    else:
                        file_times.append((file_path, cache_time))
            except Exception as e:
                logger.warning(f"Error reading cache file {file_path}: {e}")
                expired_files.append(file_path)
        
        # Remove expired files
        for file_path in expired_files:
            try:
                file_path.unlink()
                logger.debug(f"Removed expired cache file: {file_path}")
            except Exception as e:
                logger.warning(f"Error removing expired cache file {file_path}: {e}")
        
        # Check size limit and remove oldest files if needed
        current_size_mb = self._get_cache_size_mb(cache_dir)
        if current_size_mb > max_size_mb:
            # Sort files by timestamp (oldest first)
            file_times.sort(key=lambda x: x[1])
            
            # Remove oldest files until under size limit
            for file_path, _ in file_times:
                try:
                    file_path.unlink()
                    logger.debug(f"Removed old cache file due to size limit: {file_path}")
                    
                    current_size_mb = self._get_cache_size_mb(cache_dir)
                    if current_size_mb <= max_size_mb:
                        break
                except Exception as e:
                    logger.warning(f"Error removing cache file {file_path}: {e}")
    
    async def get_cached_response(self, query: str, context: str = "") -> Optional[Dict[str, Any]]:
        """Get cached AI response for a query"""
        try:
            # Generate cache key from query and context
            cache_data = f"query:{query}|context:{context}"
            cache_key = self._generate_cache_key(cache_data, "response")
            cache_file = self._get_cache_file_path(cache_key, "response_cache_dir")
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            if not self._is_cache_valid(cached_data, "responses"):
                cache_file.unlink()  # Remove expired cache
                return None
            
            logger.debug(f"Cache hit for response: {query[:50]}...")
            return cached_data["data"]
            
        except Exception as e:
            logger.warning(f"Error reading response cache: {e}")
            return None
    
    async def cache_response(self, query: str, response: Dict[str, Any], context: str = ""):
        """Cache AI response"""
        try:
            # Cleanup before adding new cache
            self._cleanup_cache("responses")
            
            # Generate cache key
            cache_key_data = f"query:{query}|context:{context}"
            cache_key = self._generate_cache_key(cache_key_data, "response")
            cache_file = self._get_cache_file_path(cache_key, "response_cache_dir")
            
            # Prepare cache data
            cache_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "context": context,
                "data": response,
                "cache_type": "response"
            }
            
            # Write to cache
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached response for: {query[:50]}...")
            
        except Exception as e:
            logger.warning(f"Error caching response: {e}")
    
    async def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        try:
            cache_key = self._generate_cache_key(text, "embedding")
            cache_file = self._get_cache_file_path(cache_key, "embedding_cache_dir")
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            if not self._is_cache_valid(cached_data, "embeddings"):
                cache_file.unlink()
                return None
            
            logger.debug(f"Cache hit for embedding: {text[:50]}...")
            return cached_data["data"]
            
        except Exception as e:
            logger.warning(f"Error reading embedding cache: {e}")
            return None
    
    async def cache_embedding(self, text: str, embedding: List[float]):
        """Cache text embedding"""
        try:
            self._cleanup_cache("embeddings")
            
            cache_key = self._generate_cache_key(text, "embedding")
            cache_file = self._get_cache_file_path(cache_key, "embedding_cache_dir")
            
            cache_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "text": text,
                "data": embedding,
                "cache_type": "embedding"
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached embedding for: {text[:50]}...")
            
        except Exception as e:
            logger.warning(f"Error caching embedding: {e}")
    
    async def get_cached_search(self, query: str, search_type: str = "general") -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        try:
            cache_key_data = f"query:{query}|type:{search_type}"
            cache_key = self._generate_cache_key(cache_key_data, "search")
            cache_file = self._get_cache_file_path(cache_key, "search_cache_dir")
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            if not self._is_cache_valid(cached_data, "search"):
                cache_file.unlink()
                return None
            
            logger.debug(f"Cache hit for search: {query[:50]}...")
            return cached_data["data"]
            
        except Exception as e:
            logger.warning(f"Error reading search cache: {e}")
            return None
    
    async def cache_search(self, query: str, results: List[Dict[str, Any]], search_type: str = "general"):
        """Cache search results"""
        try:
            self._cleanup_cache("search")
            
            cache_key_data = f"query:{query}|type:{search_type}"
            cache_key = self._generate_cache_key(cache_key_data, "search")
            cache_file = self._get_cache_file_path(cache_key, "search_cache_dir")
            
            cache_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "search_type": search_type,
                "data": results,
                "cache_type": "search"
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached search results for: {query[:50]}...")
            
        except Exception as e:
            logger.warning(f"Error caching search results: {e}")
    
    async def get_cached_vector_search(self, query: str, top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Get cached vector search results"""
        try:
            cache_data = f"query:{query}|top_k:{top_k}"
            cache_key = self._generate_cache_key(cache_data, "vector")
            cache_file = self._get_cache_file_path(cache_key, "vector_cache_dir")
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            if not self._is_cache_valid(cached_data, "vectors"):
                cache_file.unlink()
                return None
            
            logger.debug(f"Cache hit for vector search: {query[:50]}...")
            return cached_data["data"]
            
        except Exception as e:
            logger.warning(f"Error reading vector search cache: {e}")
            return None
    
    async def cache_vector_search(self, query: str, results: List[Dict[str, Any]], top_k: int = 5):
        """Cache vector search results"""
        try:
            self._cleanup_cache("vectors")
            
            cache_key_data = f"query:{query}|top_k:{top_k}"
            cache_key = self._generate_cache_key(cache_key_data, "vector")
            cache_file = self._get_cache_file_path(cache_key, "vector_cache_dir")
            
            cache_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "top_k": top_k,
                "data": results,
                "cache_type": "vector_search"
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cached vector search results for: {query[:50]}...")
            
        except Exception as e:
            logger.warning(f"Error caching vector search results: {e}")
    
    async def clear_cache(self, cache_type: Optional[str] = None):
        """Clear cache entries"""
        try:
            if cache_type:
                if cache_type == "responses":
                    cache_dir = self.response_cache_dir
                elif cache_type == "embeddings":
                    cache_dir = self.embedding_cache_dir
                elif cache_type == "search":
                    cache_dir = self.search_cache_dir
                elif cache_type == "vectors":
                    cache_dir = self.vector_cache_dir
                else:
                    raise ValueError(f"Unknown cache type: {cache_type}")
                    
                for file_path in cache_dir.glob("*.json"):
                    file_path.unlink()
                logger.info(f"Cleared {cache_type} cache")
            else:
                # Clear all caches
                for cache_dir in [self.response_cache_dir, self.embedding_cache_dir, 
                                self.search_cache_dir, self.vector_cache_dir]:
                    for file_path in cache_dir.glob("*.json"):
                        file_path.unlink()
                logger.info("Cleared all caches")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = {}
            
            for cache_type in self.cache_config.keys():
                if cache_type == "responses":
                    cache_dir = self.response_cache_dir
                elif cache_type == "embeddings":
                    cache_dir = self.embedding_cache_dir
                elif cache_type == "search":
                    cache_dir = self.search_cache_dir
                elif cache_type == "vectors":
                    cache_dir = self.vector_cache_dir
                else:
                    continue
                
                # Count files
                file_count = len(list(cache_dir.glob("*.json")))
                
                # Calculate size
                size_mb = self._get_cache_size_mb(cache_dir)
                
                # Get max size
                max_size_mb = self.cache_config[cache_type]["max_size_mb"]
                
                stats[cache_type] = {
                    "file_count": file_count,
                    "size_mb": round(size_mb, 2),
                    "max_size_mb": max_size_mb,
                    "usage_percent": round((size_mb / max_size_mb) * 100, 2) if max_size_mb > 0 else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}
    
    async def warm_cache(self, common_queries: List[str]):
        """Pre-warm cache with common queries"""
        logger.info(f"Warming cache with {len(common_queries)} common queries")
        
        # This would be called during startup to pre-cache common queries
        # Implementation depends on the specific queries you want to cache
        pass 