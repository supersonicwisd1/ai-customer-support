#!/usr/bin/env python3
"""
Comprehensive Aven Site Crawler Script

This script uses the ComprehensiveCrawler to crawl the entire Aven website
and build a complete knowledge base with proper source attribution.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.crawler_service import CrawlerService
from app.services.pinecone_service import PineconeService
from app.services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawl_aven_site.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def crawl_and_store():
    """Crawl Aven site and store in vector database"""
    
    # Check environment variables
    required_env_vars = ['FIRECRAWL_API_KEY', 'OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your .env file")
        return False
    
    try:
        logger.info("Starting comprehensive Aven site crawl")
        
        # Initialize services
        crawler = CrawlerService()
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Initialize Pinecone
        pinecone_service.initialize_index()
        
        # Start comprehensive crawling
        logger.info("Beginning comprehensive site crawl...")
        scraped_data = await crawler.crawl_and_scrape_sitemaps()
        
        if not scraped_data:
            logger.error("No data was scraped")
            return False
        
        # Get crawl statistics
        stats = await crawler.get_crawl_statistics()
        logger.info(f"Crawl statistics: {json.dumps(stats, indent=2)}")
        
        # Save raw scraped data
        output_file = f"aven_site_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw scraped data saved to: {output_file}")
        
        # Process and store in vector database
        logger.info("Processing and storing in vector database...")
        stored_count = 0
        failed_count = 0
        
        for page_data in scraped_data:
            if page_data['status'] != 'success':
                continue
                
            try:
                # Generate embedding
                content = page_data['content']
                if len(content) < 50:  # Skip very short content
                    logger.warning(f"Skipping short content from {page_data['url']}")
                    continue
                
                embedding = await openai_service.generate_embeddings(content)
                
                # Prepare vector data with proper source attribution
                vector_data = {
                    "id": f"aven_{hash(page_data['url'])}",
                    "values": embedding,
                    "metadata": {
                        "url": page_data['url'],
                        "title": page_data['title'],
                        "content": content[:1000],  # Store first 1000 chars
                        "content_length": page_data['content_length'],
                        "page_type": page_data.get('metadata', {}).get('page_type', 'unknown'),
                        "content_quality": page_data.get('metadata', {}).get('content_quality_score', 0.0),
                        "crawl_depth": page_data.get('source_info', {}).get('crawl_depth', 0),
                        "crawled_at": page_data.get('crawled_at', datetime.utcnow().isoformat()),
                        "source_id": f"aven_site_{datetime.now().strftime('%Y%m%d')}"
                    }
                }
                
                # Store in Pinecone
                await pinecone_service.upsert_documents([vector_data])
                stored_count += 1
                
                logger.info(f"Stored: {page_data['url']} ({page_data['content_length']} chars)")
                
            except Exception as e:
                logger.error(f"Failed to process {page_data['url']}: {str(e)}")
                failed_count += 1
                continue
        
        # Final statistics
        logger.info(f"Vector database update completed:")
        logger.info(f"  - Total pages crawled: {len(scraped_data)}")
        logger.info(f"  - Successfully stored: {stored_count}")
        logger.info(f"  - Failed to store: {failed_count}")
        logger.info(f"  - Success rate: {stored_count/(stored_count+failed_count)*100:.1f}%")
        
        # Save source tracking data
        source_data = crawler.source_tracker.get_all_sources()
        source_file = f"aven_sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Source tracking data saved to: {source_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in crawl_and_store: {str(e)}")
        return False

async def test_crawler():
    """Test the crawler with a small sample"""
    logger.info("Testing crawler with small sample...")
    
    try:
        crawler = CrawlerService()
        crawler.max_pages = 5  # Limit for testing
        
        scraped_data = await crawler.crawl_and_scrape_site()
        
        logger.info(f"Test crawl completed: {len(scraped_data)} pages")
        
        for page in scraped_data:
            logger.info(f"  - {page['url']}: {page['content_length']} chars")
        
        return True
        
    except Exception as e:
        logger.error(f"Test crawl failed: {str(e)}")
        return False

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crawl Aven website comprehensively')
    parser.add_argument('--test', action='store_true', help='Run test crawl (5 pages)')
    parser.add_argument('--full', action='store_true', help='Run full crawl and store in vector DB')
    
    args = parser.parse_args()
    
    if args.test:
        success = await test_crawler()
    elif args.full:
        success = await crawl_and_store()
    else:
        logger.info("No action specified. Use --test for test crawl or --full for complete crawl")
        return
    
    if success:
        logger.info("Crawl completed successfully!")
    else:
        logger.error("Crawl failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 