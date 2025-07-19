from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import List, Optional
from app.models.chat import SearchQuery, SearchResult
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/search", tags=["search"])

# Global search service instance
_search_service: Optional[SearchService] = None

def get_search_service() -> SearchService:
    """Get or create search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

@router.post("/query", response_model=List[SearchResult])
async def search_query(query: SearchQuery, search_service: SearchService = Depends(get_search_service)):
    """Perform a web search"""
    try:
        if not search_service.is_available():
            raise HTTPException(status_code=503, detail="Search service not configured")
        
        logger.info(f"Performing search: {query.query}")
        results = await search_service.search(query.query, query.max_results)
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/aven", response_model=List[SearchResult])
async def search_aven(query: SearchQuery, search_service: SearchService = Depends(get_search_service)):
    """Search specifically for Aven-related information"""
    try:
        if not search_service.is_available():
            raise HTTPException(status_code=503, detail="Search service not configured")
        
        logger.info(f"Performing Aven-specific search: {query.query}")
        results = await search_service.search_aven_specific(query.query, query.max_results)
        
        return results
        
    except Exception as e:
        logger.error(f"Aven search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Aven search failed")

@router.post("/news", response_model=List[SearchResult])
async def search_news(query: SearchQuery, search_service: SearchService = Depends(get_search_service)):
    """Search for latest news and updates"""
    try:
        if not search_service.is_available():
            raise HTTPException(status_code=503, detail="Search service not configured")
        
        logger.info(f"Performing news search: {query.query}")
        results = await search_service.search_latest_news(query.query, query.max_results)
        
        return results
        
    except Exception as e:
        logger.error(f"News search error: {str(e)}")
        raise HTTPException(status_code=500, detail="News search failed")

@router.get("/health")
async def search_health(search_service: SearchService = Depends(get_search_service)):
    """Health check for search service"""
    return {
        "status": "healthy" if search_service.is_available() else "unavailable",
        "configured": search_service.is_available(),
        "service": "search"
    } 