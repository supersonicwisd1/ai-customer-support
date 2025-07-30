#!/usr/bin/env python3
"""
Cache warming script for Aven AI Assistant
Pre-warms cache with common queries to improve response times
"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.cache_service import CacheService
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.core.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Common Aven-related queries for cache warming
COMMON_QUERIES = [
    # General Aven information
    "What is Aven?",
    "How does Aven work?",
    "What services does Aven offer?",
    "Is Aven a legitimate company?",
    
    # Credit card related
    "What credit cards does Aven offer?",
    "What are the Aven credit card rates?",
    "How do I apply for an Aven credit card?",
    "What is the APR for Aven credit cards?",
    "Are there any fees with Aven credit cards?",
    
    # Loan related
    "What types of loans does Aven offer?",
    "What are the loan rates at Aven?",
    "How do I apply for a loan with Aven?",
    "What is the minimum credit score for Aven loans?",
    
    # Account management
    "How do I log into my Aven account?",
    "How do I reset my Aven password?",
    "How do I update my personal information?",
    "How do I close my Aven account?",
    
    # Customer service
    "How do I contact Aven customer service?",
    "What are Aven's customer service hours?",
    "How do I file a complaint with Aven?",
    "Does Aven have a customer support phone number?",
    
    # Security and privacy
    "Is Aven secure?",
    "How does Aven protect my personal information?",
    "What is Aven's privacy policy?",
    "Does Aven share my information with third parties?",
    
    # Fees and charges
    "What fees does Aven charge?",
    "Are there hidden fees with Aven?",
    "What is Aven's late payment fee?",
    "Does Aven charge for early payment?",
    
    # Application process
    "How long does it take to get approved by Aven?",
    "What documents do I need to apply with Aven?",
    "Can I apply for Aven if I have bad credit?",
    "What happens if Aven denies my application?",
    
    # Mobile app
    "Does Aven have a mobile app?",
    "How do I download the Aven app?",
    "What features are available in the Aven app?",
    "Is the Aven app available for Android?",
    
    # Education and resources
    "Does Aven offer financial education?",
    "Where can I learn more about credit building?",
    "Does Aven have any educational resources?",
    "How can I improve my credit score with Aven?"
]

async def warm_cache():
    """Warm the cache with common queries"""
    try:
        logger.info("Starting cache warming process...")
        
        # Initialize services
        cache_service = CacheService()
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        vector_store = VectorStore(pinecone_service, openai_service)
        
        # Initialize Pinecone
        pinecone_service.initialize_index()
        
        logger.info(f"Warming cache with {len(COMMON_QUERIES)} common queries...")
        
        # Process each query
        for i, query in enumerate(COMMON_QUERIES, 1):
            try:
                logger.info(f"Processing query {i}/{len(COMMON_QUERIES)}: {query}")
                
                # Generate embedding and cache it
                embedding = await openai_service.generate_embeddings(query)
                
                # Perform vector search and cache results
                search_results = await vector_store.search_similar(query, top_k=5)
                
                # Cache search results
                await cache_service.cache_vector_search(query, search_results, top_k=5)
                
                logger.info(f"Successfully warmed cache for: {query}")
                
                # Small delay to avoid overwhelming the APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error warming cache for query '{query}': {e}")
                continue
        
        # Get cache statistics
        stats = await cache_service.get_cache_statistics()
        logger.info("Cache warming completed!")
        logger.info(f"Final cache statistics: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        return False

async def main():
    """Main function"""
    logger.info("Starting Aven AI cache warming script...")
    
    success = await warm_cache()
    
    if success:
        logger.info("Cache warming completed successfully!")
        sys.exit(0)
    else:
        logger.error("Cache warming failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 