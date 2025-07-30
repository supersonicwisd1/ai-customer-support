from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cache", tags=["cache"])

# Global cache service instance
cache_service = CacheService()

@router.get("/stats")
async def get_cache_statistics() -> Dict[str, Any]:
    """Get cache statistics"""
    try:
        stats = await cache_service.get_cache_statistics()
        return {
            "status": "success",
            "data": stats,
            "message": "Cache statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")

@router.delete("/clear")
async def clear_cache(cache_type: Optional[str] = None) -> Dict[str, Any]:
    """Clear cache entries"""
    try:
        await cache_service.clear_cache(cache_type)
        message = f"Cleared {cache_type} cache" if cache_type else "Cleared all caches"
        return {
            "status": "success",
            "message": message
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.post("/warm")
async def warm_cache(queries: List[str]) -> Dict[str, Any]:
    """Pre-warm cache with common queries"""
    try:
        await cache_service.warm_cache(queries)
        return {
            "status": "success",
            "message": f"Cache warming initiated with {len(queries)} queries"
        }
    except Exception as e:
        logger.error(f"Error warming cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to warm cache: {str(e)}")

@router.get("/health")
async def cache_health() -> Dict[str, Any]:
    """Check cache health and status"""
    try:
        stats = await cache_service.get_cache_statistics()
        
        # Check if cache directories exist and are accessible
        cache_health = {
            "status": "healthy",
            "cache_directories": {
                "responses": cache_service.response_cache_dir.exists(),
                "embeddings": cache_service.embedding_cache_dir.exists(),
                "search": cache_service.search_cache_dir.exists(),
                "vectors": cache_service.vector_cache_dir.exists()
            },
            "statistics": stats
        }
        
        return cache_health
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 