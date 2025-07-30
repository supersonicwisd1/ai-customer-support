from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.post("/rebuild")
async def rebuild_knowledge_base() -> Dict[str, Any]:
    """Rebuild the entire knowledge base with enhanced scraping"""
    try:
        from app.services.enhanced_knowledge_service import EnhancedKnowledgeService
        
        async with EnhancedKnowledgeService() as service:
            result = await service.build_comprehensive_knowledge_base()
            
            return {
                "success": True,
                "message": "Knowledge base rebuilt successfully",
                "data": result
            }
            
    except Exception as e:
        logger.error(f"Failed to rebuild knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild knowledge base: {str(e)}")

@router.get("/status")
async def get_knowledge_status() -> Dict[str, Any]:
    """Get the current status of the knowledge base"""
    try:
        from app.services.pinecone_service import PineconeService
        
        pinecone_service = PineconeService()
        pinecone_service.initialize_index()
        
        # Get index stats
        index_stats = pinecone_service.index.describe_index_stats()
        
        return {
            "success": True,
            "index_name": pinecone_service.index_name,
            "total_vectors": index_stats.get("total_vector_count", 0),
            "dimension": index_stats.get("dimension", 0),
            "metric": index_stats.get("metric", "cosine")
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge status: {str(e)}") 