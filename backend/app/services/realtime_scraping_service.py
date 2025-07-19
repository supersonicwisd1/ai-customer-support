import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.scraping_service import ScrapingService
from app.models.chat import SearchResult

logger = logging.getLogger(__name__)

class RealtimeScrapingService:
    """Service for real-time web scraping of Aven's website"""
    
    def __init__(self):
        self.scraping_service = ScrapingService()
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
    
    async def get_aven_current_info(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Get current information from Aven's website based on query"""
        try:
            # Check cache first
            cache_key = f"aven_{query.lower().replace(' ', '_')}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.utcnow() - cached_data['timestamp'] < self.cache_duration:
                    logger.info(f"Returning cached data for: {query}")
                    return cached_data['results']
            
            # Scrape Aven's website
            logger.info(f"Scraping Aven website for: {query}")
            
            # Define Aven URLs to scrape
            aven_urls = [
                "https://aven.com",
                "https://www.aven.com"
            ]
            
            all_results = []
            
            for url in aven_urls:
                try:
                    # Scrape the page
                    scraped_data = await self.scraping_service.scrape_page(url)
                    
                    if scraped_data and scraped_data.get('content'):
                        # Extract relevant information based on query
                        relevant_info = self._extract_relevant_info(scraped_data['content'], query)
                        
                        if relevant_info:
                            result = SearchResult(
                                title=f"Aven Website - {query.title()}",
                                content=relevant_info,
                                url=url,
                                source="aven_website_scraped",
                                relevance_score=self._calculate_relevance(query, relevant_info),
                                timestamp=datetime.utcnow()
                            )
                            all_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue
            
            # Cache the results
            self.cache[cache_key] = {
                'results': all_results[:max_results],
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"Scraping completed: {len(all_results)} results found")
            return all_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error in real-time scraping: {str(e)}")
            return []
    
    def _extract_relevant_info(self, text: str, query: str) -> str:
        """Extract relevant information from scraped text based on query"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Define search patterns for different query types
        patterns = {
            "rates": ["apr", "rate", "interest", "7.49", "14.99", "percentage"],
            "latest": ["new", "update", "latest", "recent", "announcement"],
            "features": ["feature", "benefit", "offer", "include", "provide"],
            "news": ["news", "announcement", "update", "release"],
            "pricing": ["price", "cost", "fee", "charge", "rate"],
            "cash back": ["cash back", "cashback", "reward", "12%"],
            "credit limit": ["credit limit", "limit", "250,000", "250000"]
        }
        
        # Find relevant patterns
        relevant_patterns = []
        for category, pattern_list in patterns.items():
            if any(word in query_lower for word in category.split()):
                relevant_patterns.extend(pattern_list)
        
        # If no specific patterns, look for general Aven information
        if not relevant_patterns:
            relevant_patterns = ["aven", "credit", "card", "home equity", "heloc"]
        
        # Extract sentences containing relevant patterns
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(pattern in sentence_lower for pattern in relevant_patterns):
                # Clean up the sentence
                cleaned_sentence = sentence.strip()
                if len(cleaned_sentence) > 20:  # Only include substantial sentences
                    relevant_sentences.append(cleaned_sentence)
        
        # Combine relevant sentences
        if relevant_sentences:
            return '. '.join(relevant_sentences[:5])  # Limit to 5 sentences
        
        # Fallback: return first 200 characters if no specific matches
        return text[:200] + "..." if len(text) > 200 else text
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score for scraped content"""
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        score = 0.5  # Base score
        
        # Boost score for query term matches
        for term in query_terms:
            if term in content_lower:
                score += 0.2
        
        # Boost score for Aven-specific terms
        aven_terms = ["aven", "credit card", "home equity", "heloc", "apr", "cash back"]
        for term in aven_terms:
            if term in content_lower:
                score += 0.1
        
        # Boost score for recent content (if timestamp is recent)
        if "2025" in content or "2024" in content:
            score += 0.1
        
        return min(score, 1.0)
    
    async def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_keys": list(self.cache.keys()),
            "oldest_entry": min([data['timestamp'] for data in self.cache.values()]) if self.cache else None,
            "newest_entry": max([data['timestamp'] for data in self.cache.values()]) if self.cache else None
        } 