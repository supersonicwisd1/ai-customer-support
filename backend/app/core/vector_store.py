import logging
from typing import List, Dict, Any, Optional
from app.services.pinecone_service import PineconeService
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

class VectorStore:
    """Wrapper for vector database operations"""
    
    def __init__(self, pinecone_service: PineconeService, openai_service: OpenAIService):
        self.pinecone_service = pinecone_service
        self.openai_service = openai_service
    
    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database"""
        try:
            # Generate embedding for the query
            query_embedding = await self.openai_service.generate_embeddings(query)
            
            # Search in Pinecone
            results = await self.pinecone_service.search_similar(query_embedding, top_k)
            
            logger.info(f"Vector search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
    
    async def add_document(self, text: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the vector database"""
        try:
            # Generate embedding
            embedding = await self.openai_service.generate_embeddings(text)
            
            # Prepare document for Pinecone
            document = {
                "id": metadata.get("id", f"doc_{hash(text)}"),
                "embedding": embedding,
                "text": text,
                "source": metadata.get("source", "unknown"),
                "url": metadata.get("url", ""),
                "timestamp": metadata.get("timestamp", "")
            }
            
            # Store in Pinecone
            await self.pinecone_service.upsert_documents([document])
            
            logger.info(f"Document added to vector store: {metadata.get('id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False
    
    async def get_relevant_context(self, query: str, max_results: int = 3) -> str:
        """Get relevant context from vector database for a query"""
        try:
            results = await self.search_similar(query, max_results)
            
            if not results:
                return ""
            
            # Combine relevant contexts
            contexts = []
            for result in results:
                if result.get("text"):
                    contexts.append(result["text"])
            
            return "\n\n".join(contexts)
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return "" 