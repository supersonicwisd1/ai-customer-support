from openai import OpenAI
import logging
import os
from typing import Optional
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        try:
            self.client = OpenAI(api_key=api_key)
            self.cache_service = CacheService()
            logger.info("OpenAI client initialized successfully with caching")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def generate_response(self, message: str, context: str = "") -> str:
        """Generate a response using OpenAI's GPT model"""
        try:
            prompt = f"""
            You are a helpful customer support agent for Aven, a financial technology company.
            
            Context: {context}
            
            User question: {message}
            
            Please provide a helpful, accurate response based on the context provided.
            If you don't have enough information, say so politely.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using more cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful customer support agent for Aven."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_embeddings(self, text: str) -> list:
        """Generate embeddings for text using OpenAI's embedding model with caching"""
        try:
            # Check cache first
            cached_embedding = await self.cache_service.get_cached_embedding(text)
            if cached_embedding:
                logger.debug(f"Cache hit for embedding: {text[:50]}...")
                return cached_embedding
            
            # Generate new embedding
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache the embedding
            await self.cache_service.cache_embedding(text, embedding)
            
            return embedding
        
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")