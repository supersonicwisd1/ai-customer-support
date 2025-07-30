import logging
import os
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec

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
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
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
                        "url": metadata.get("url", "")
                    }
                    processed_results.append(processed_result)
                except Exception as e:
                    logger.warning(f"Error processing Pinecone match: {e}, match: {match}")
                    continue
            
            logger.info(f"Processed {len(processed_results)} results from Pinecone")
            return processed_results
            
        except Exception as e:
            logger.error(f"Pinecone search error: {str(e)}")
            # Return empty results instead of raising exception
            return []
    
    async def search_vectors(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Alias for search_similar - for compatibility with existing code"""
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
