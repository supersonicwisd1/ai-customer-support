import logging
import os
from typing import List, Dict, Any
from pinecone import Pinecone

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")
        
        try:
            self.pc = Pinecone(api_key=api_key)
            self.index_name = "aven-knowledge"
            self.index = None
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise
    
    def initialize_index(self):
        """Initialize or create Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                # Create index if it doesn't exist
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # text-embedding-3-small dimension
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone initialization error: {str(e)}")
            raise Exception(f"Failed to initialize Pinecone: {str(e)}")
    
    async def upsert_documents(self, documents: List[Dict[str, Any]]):
        """Upsert documents into Pinecone"""
        if not self.index:
            self.initialize_index()
            
        try:
            vectors = []
            for doc in documents:
                vectors.append({
                    "id": doc["id"],
                    "values": doc["embedding"],
                    "metadata": {
                        "text": doc["text"][:40000],  # Limit metadata size
                        "source": doc.get("source", ""),
                        "url": doc.get("url", ""),
                        "timestamp": doc.get("timestamp", "")
                    }
                })
            
            self.index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} documents to Pinecone")
            
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            raise Exception(f"Failed to upsert documents: {str(e)}")
    
    async def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.index:
            self.initialize_index()
            
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            logger.info(f"Pinecone search results: {results}")
            
            processed_results = []
            for match in results.get("matches", []):
                try:
                    metadata = match.get("metadata", {})
                    processed_result = {
                        "id": match.get("id", ""),
                        "score": match.get("score", 0.0),
                        "text": metadata.get("text", ""),
                        "source": metadata.get("source", ""),
                        "url": metadata.get("url", ""),
                        "timestamp": metadata.get("timestamp", "")
                    }
                    processed_results.append(processed_result)
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Pinecone search error: {str(e)}")
            raise Exception(f"Failed to search documents: {str(e)}")
    
    async def search_vectors(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar vectors"""
        return await self.search_similar(query_embedding, top_k)
    
    async def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """Upsert vectors into Pinecone"""
        if not self.index:
            self.initialize_index()
            
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
            
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            raise Exception(f"Failed to upsert vectors: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.index:
            self.initialize_index()
            
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "namespaces": stats.get("namespaces", {})
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"error": str(e)}
    
    def delete_vectors(self, ids: List[str]):
        """Delete vectors by IDs"""
        if not self.index:
            self.initialize_index()
            
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            raise Exception(f"Failed to delete vectors: {str(e)}")
    
    def clear_index(self):
        """Clear all vectors from the index"""
        if not self.index:
            self.initialize_index()
            
        try:
            # Get all vector IDs and delete them
            stats = self.index.describe_index_stats()
            namespaces = stats.get("namespaces", {})
            
            for namespace in namespaces:
                self.index.delete(namespace=namespace)
            
            logger.info("Cleared all vectors from Pinecone index")
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            raise Exception(f"Failed to clear index: {str(e)}")
