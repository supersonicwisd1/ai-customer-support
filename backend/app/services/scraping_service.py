# app/services/scraping_service.py

import asyncio
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import re
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup
import logging
import os

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        self.base_url = "https://aven.com"
        self.visited_urls = set()
        self.scraped_data = []
        
    async def scrape_page(self, url: str, max_wait: int = 10000) -> Dict:
        """Scrape a single page using Firecrawl.dev"""
        try:
            logger.info(f"Scraping page with Firecrawl: {url}")
            
            # Use Firecrawl to scrape the page with correct parameters (synchronous)
            response = self.firecrawl.scrape_url(
                url=url,
                formats=['html', 'markdown'],  # Get both HTML and markdown
                wait_for=3000,  # Wait 3 seconds for dynamic content (number, not string)
                timeout=30000,  # 30 second timeout
                only_main_content=False  # Get full page content
            )
            
            # Check if scraping was successful
            if not response.success:
                logger.warning(f"Firecrawl scraping failed for {url}: {response.error}")
                return {
                    "url": url,
                    "title": "",
                    "content": f"Firecrawl error: {response.error}",
                    "links": [],
                    "structured_data": {},
                    "content_length": 0,
                    "status": "error"
                }
            
            if not response.html:
                logger.warning(f"No HTML content received for {url}")
                return {
                    "url": url,
                    "title": "",
                    "content": "No HTML content received from Firecrawl",
                    "links": [],
                    "structured_data": {},
                    "content_length": 0,
                    "status": "error"
                }
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.html, 'html.parser')
            
            # Extract title from metadata or HTML
            title = ""
            if response.metadata and response.metadata.get('title'):
                title = response.metadata['title']
            else:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            
            # Extract text content
            text_content = self._extract_text_content(soup)
            
            # Extract links from HTML (Firecrawl doesn't provide links in response)
            links = await self._extract_links_from_soup(soup)
            
            # Extract structured data
            structured_data = self._extract_structured_data(soup)
            
            result = {
                "url": url,
                "title": title,
                "content": text_content,
                "links": links,
                "structured_data": structured_data,
                "content_length": len(text_content),
                "status": "success"
            }
            
            logger.info(f"Successfully scraped {url}: {len(text_content)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "title": "",
                "content": f"Error scraping page: {str(e)}",
                "links": [],
                "structured_data": {},
                "content_length": 0,
                "status": "error"
            }
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from soup"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Find main content areas - be more flexible
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_=re.compile(r'content|main|hero|section', re.IGNORECASE)) or
            soup.find('section') or
            soup.find('body')  # Fallback to body if no specific content area
        )
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text - be less aggressive
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace but keep meaningful content
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def _extract_links_from_soup(self, soup: BeautifulSoup) -> List[str]:
        """Extract internal links from BeautifulSoup"""
        try:
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/') or 'aven.com' in href:
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)
                    links.append(href)
            
            # Remove duplicates and limit
            return list(set(links))[:50]
            
        except Exception as e:
            logger.error(f"Error extracting links from soup: {str(e)}")
            return []
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data like pricing, features, etc."""
        structured: dict[str, Any] = {}
        
        # Extract meta information
        structured['meta'] = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                structured['meta'][name] = content
        
        # Extract headings
        structured['headings'] = {}
        for i in range(1, 7):
            headings = [h.get_text().strip() for h in soup.find_all(f'h{i}')]
            if headings:
                structured['headings'][f'h{i}'] = headings
        
        # Look for pricing information
        pricing_keywords = ['price', 'cost', 'fee', 'rate', 'apr', '$', '%']
        pricing_elements = []
        for keyword in pricing_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            pricing_elements.extend([elem.strip() for elem in elements if elem.strip()])
        
        if pricing_elements:
            structured['pricing_info'] = pricing_elements[:10]  # Limit results
        
        return structured
    
    async def scrape_site_comprehensive(self, max_pages: int = 20) -> List[Dict]:
        """Comprehensively scrape Aven's website using Firecrawl"""
        logger.info(f"Starting comprehensive scrape of {self.base_url} with Firecrawl")
        
        try:
            # Start with main pages
            urls_to_scrape = [
                self.base_url,
                f"{self.base_url}/about",
                f"{self.base_url}/products",
                f"{self.base_url}/pricing",
                f"{self.base_url}/features",
                f"{self.base_url}/how-it-works",
                f"{self.base_url}/support",
                f"{self.base_url}/contact",
                f"{self.base_url}/faq",
                f"{self.base_url}/blog"
            ]
            
            all_scraped_data: list[Dict] = []
            discovered_urls = set()
            
            for url in urls_to_scrape[:max_pages]:
                if url in self.visited_urls:
                    continue
                
                logger.info(f"Scraping page {len(all_scraped_data) + 1}/{max_pages}: {url}")
                
                data = await self.scrape_page(url)
                self.visited_urls.add(url)
                
                # Add all successful scrapes, regardless of content length
                if data['status'] == 'success':
                    all_scraped_data.append(data)
                    logger.info(f"Added page: {url} with {data['content_length']} characters")
                    
                    # Discover more URLs from this page
                    discovered_urls.update(data['links'])
                else:
                    logger.warning(f"Failed to scrape {url}: {data['content']}")
                
                # Rate limiting - Firecrawl handles this, but we can add a small delay
                await asyncio.sleep(0.5)
            
            # Scrape some discovered URLs if we haven't hit the limit
            remaining_slots = max_pages - len(all_scraped_data)
            new_urls = list(discovered_urls - self.visited_urls)[:remaining_slots]
            
            for url in new_urls:
                logger.info(f"Scraping discovered page: {url}")
                data = await self.scrape_page(url)
                self.visited_urls.add(url)
                
                if data['status'] == 'success':
                    all_scraped_data.append(data)
                    logger.info(f"Added discovered page: {url} with {data['content_length']} characters")
                
                await asyncio.sleep(0.5)
            
            logger.info(f"Comprehensive scrape completed: {len(all_scraped_data)} pages scraped")
            return all_scraped_data
            
        except Exception as e:
            logger.error(f"Error in comprehensive scrape: {str(e)}")
            return []
    
    async def update_vector_database(self, pinecone_service, openai_service) -> Dict:
        """Scrape and update vector database with fresh content"""
        logger.info("Starting vector database update with fresh content")
        
        try:
            # Scrape fresh content
            scraped_data = await self.scrape_site_comprehensive(max_pages=15)
            
            if not scraped_data:
                return {"status": "error", "message": "No content scraped"}
            
            # Process and store in vector database
            stored_count = 0
            for data in scraped_data:
                try:
                    # Generate embedding
                    embedding = await openai_service.get_embeddings(data['content'])
                    
                    # Store in Pinecone
                    vector_data = {
                        "id": f"aven_{hash(data['url'])}",
                        "values": embedding,
                        "metadata": {
                            "url": data['url'],
                            "title": data['title'],
                            "content": data['content'][:1000],  # Store first 1000 chars
                            "content_length": data['content_length'],
                            "scraped_at": str(asyncio.get_event_loop().time())
                        }
                    }
                    
                    await pinecone_service.upsert_vectors([vector_data])
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {data['url']}: {str(e)}")
                    continue
            
            result = {
                "status": "success",
                "pages_scraped": len(scraped_data),
                "vectors_stored": stored_count,
                "urls_processed": [data['url'] for data in scraped_data]
            }
            
            logger.info(f"Vector database update completed: {stored_count} vectors stored")
            return result
            
        except Exception as e:
            logger.error(f"Error updating vector database: {str(e)}")
            return {"status": "error", "message": str(e)}
