import os
import json
import logging
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
from firecrawl import FirecrawlApp
from app.config import settings

class Scraper:
    def __init__(self, sitemap_url: str, extra_links: List[str], archive_dir: str = "archive", output_file: str = "scraped_data.json"):
        self.sitemap_url = sitemap_url
        self.extra_links = extra_links
        self.archive_dir = archive_dir
        self.output_file = output_file
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict[str, Any]] = []
        os.makedirs(self.archive_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        self.firecrawl = FirecrawlApp(api_key=settings.firecrawl_api_key)

    def fetch_sitemap_links(self) -> List[str]:
        import requests
        links = []
        try:
            resp = requests.get(self.sitemap_url, timeout=20)
            resp.raise_for_status()
            content = resp.text.strip()
            # Try XML parsing
            if self.sitemap_url.endswith('.xml') or content.startswith('<?xml') or '<urlset' in content or '<sitemapindex' in content:
                try:
                    root = ET.fromstring(content)
                    for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        url = loc.text
                        if url:
                            links.append(url)
                except Exception as e:
                    logging.warning(f"Error parsing sitemap XML: {e}")
            else:
                # Fallback: treat as HTML and extract <a href> links
                soup = BeautifulSoup(content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http'):
                        links.append(href)
                    elif href.startswith('/'):
                        links.append(urljoin(self.sitemap_url, href))
            logging.info(f"Discovered {len(links)} links from sitemap.")
        except Exception as e:
            logging.error(f"Failed to fetch sitemap: {e}")
        return links

    def scrape_url(self, url: str) -> Dict[str, Any]:
        try:
            # Use Firecrawl to scrape the page
            response = self.firecrawl.scrape_url(
                url=url,
                formats=['html', 'markdown'],
                wait_for=5000,  # Wait for dynamic content
                timeout=45000,  # 45 second timeout
                only_main_content=False
            )
            if not response.success:
                logging.error(f"Firecrawl scraping failed for {url}: {response.error}")
                return {
                    "url": url,
                    "title": "",
                    "content": f"Firecrawl error: {response.error}",
                    "links": [],
                    "structured_data": {},
                    "content_length": 0,
                    "status": "error",
                    "scraped_at": datetime.utcnow().isoformat()
                }
            if not response.html:
                logging.error(f"No HTML content received for {url}")
                return {
                    "url": url,
                    "title": "",
                    "content": "No HTML content received from Firecrawl",
                    "links": [],
                    "structured_data": {},
                    "content_length": 0,
                    "status": "error",
                    "scraped_at": datetime.utcnow().isoformat()
                }
            html = response.html
            soup = BeautifulSoup(html, 'html.parser')
            title = response.metadata.get('title') if response.metadata and response.metadata.get('title') else (soup.title.string.strip() if soup.title and soup.title.string else '')
            text = self.extract_text(soup)
            self.archive_scrape(url, html, text)
            links = self.extract_links(soup, url)
            structured_data = self.extract_structured_data(soup)
            return {
                "url": url,
                "title": title,
                "content": text,
                "links": links,
                "structured_data": structured_data,
                "content_length": len(text),
                "status": "success",
                "scraped_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "title": "",
                "content": f"Error: {e}",
                "links": [],
                "structured_data": {},
                "content_length": 0,
                "status": "error",
                "scraped_at": datetime.utcnow().isoformat()
            }

    def extract_text(self, soup: BeautifulSoup) -> str:
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        main = soup.find('main') or soup.find('article') or soup.find('body')
        text = main.get_text(separator=' ', strip=True) if main else soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http'):
                links.add(href)
            elif href.startswith('/'):
                links.add(urljoin(base_url, href))
        return list(links)

    def extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        data = {}
        # Meta tags
        data['meta'] = {meta.get('name') or meta.get('property'): meta.get('content') for meta in soup.find_all('meta') if meta.get('content')}
        # Headings
        data['headings'] = {f'h{i}': [h.get_text(strip=True) for h in soup.find_all(f'h{i}')] for i in range(1, 7)}
        return data

    def archive_scrape(self, url: str, html: str, text: str):
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%S')
        base_path = os.path.join(self.archive_dir, f"{url_hash}_{timestamp}")
        try:
            with open(base_path + '.html', 'w', encoding='utf-8') as f:
                f.write(html)
            with open(base_path + '.txt', 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            logging.warning(f"Failed to archive {url}: {e}")

    def run(self):
        all_links = set(self.fetch_sitemap_links()) | set(self.extra_links)
        logging.info(f"Total URLs to scrape: {len(all_links)}")
        for url in all_links:
            if url not in self.visited_urls:
                result = self.scrape_url(url)
                self.scraped_data.append(result)
                self.visited_urls.add(url)
        # Save all results
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2)
            logging.info(f"Scraping complete. Results saved to {self.output_file}")
        except Exception as e:
            logging.error(f"Failed to save results: {e}")

    def get_content_type(self, url: str, title: str, content: str) -> str:
        """Get content type using hybrid approach: URL patterns + keyword analysis"""
        
        # Primary: URL-based detection (fast, reliable)
        if "/education" in url:
            return "education"
        elif "/docs" in url or url.endswith('.pdf'):
            return "document"
        elif "forbes.com" in url or "/press" in url:
            return "press"
        elif "trustpilot.com" in url or "/review" in url:
            return "review"
        elif "/support" in url or "/help" in url:
            return "support"
        elif "/pricing" in url or "/rates" in url:
            return "pricing"
        elif "/about" in url or "/company" in url:
            return "about"
        elif "/faq" in url:
            return "faq"
        elif "/privacy" in url or "/terms" in url:
            return "legal"
        
        # Secondary: Keyword analysis (no API calls)
        text = f"{title} {content}".lower()
        
        # Pricing-related content
        if any(word in text for word in ['apr', 'rate', 'fee', 'cost', 'pricing', 'interest']):
            return "pricing"
        
        # Educational content
        if any(word in text for word in ['guide', 'learn', 'how to', 'what is', 'explain', 'tutorial']):
            return "education"
        
        # Support/FAQ content
        if any(word in text for word in ['faq', 'help', 'support', 'question', 'answer', 'troubleshoot']):
            return "support"
        
        # Legal content
        if any(word in text for word in ['privacy', 'terms', 'agreement', 'policy', 'legal', 'disclosure']):
            return "legal"
        
        # About/Company content
        if any(word in text for word in ['about us', 'company', 'team', 'mission', 'vision', 'story']):
            return "about"
        
        # Product/Feature content
        if any(word in text for word in ['feature', 'benefit', 'advantage', 'product', 'service']):
            return "product"
        
        # Fallback
        return "page"

    async def save_to_pinecone(self, pinecone_service, openai_service, min_content_length=0):
        """Process scraped data and save to Pinecone"""
        try:
            # Load scraped data from JSON file
            if not os.path.exists(self.output_file):
                logging.error(f"Scraped data file not found: {self.output_file}")
                return {"status": "error", "message": "Scraped data file not found"}
            
            with open(self.output_file, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            
            # Filter for successful pages with minimum content length
            quality_pages = [
                page for page in scraped_data 
                if page['status'] == 'success' and page['content_length'] >= min_content_length
            ]
            
            logging.info(f"Processing {len(quality_pages)} pages for Pinecone upload")
            
            # Initialize Pinecone index
            pinecone_service.initialize_index()
            
            # Process pages in batches
            batch_size = 10
            total_uploaded = 0
            failed_uploads = []
            
            for i in range(0, len(quality_pages), batch_size):
                batch = quality_pages[i:i + batch_size]
                vectors = []
                
                for page in batch:
                    try:
                        # Generate embedding
                        embedding = await openai_service.generate_embeddings(page['content'])
                        
                        # Determine content type using hybrid approach
                        content_type = self.get_content_type(
                            page['url'], 
                            page['title'], 
                            page['content']
                        )
                        
                        # Create vector data
                        vector_data = {
                            "id": f"aven_{hashlib.md5(page['url'].encode()).hexdigest()}",
                            "values": embedding,
                            "metadata": {
                                "text": page['content'][:40000],  # Limit to Pinecone's metadata size
                                "url": page['url'],
                                "title": page['title'],
                                "content_type": content_type,
                                "content_length": page['content_length'],
                                "scraped_at": page['scraped_at'],
                                "source": "aven_website_scraped"
                            }
                        }
                        vectors.append(vector_data)
                        
                    except Exception as e:
                        logging.error(f"Error processing {page['url']}: {e}")
                        failed_uploads.append({"url": page['url'], "error": str(e)})
                        continue
                
                # Upload batch to Pinecone
                if vectors:
                    try:
                        await pinecone_service.upsert_vectors(vectors)
                        total_uploaded += len(vectors)
                        logging.info(f"Uploaded batch {i//batch_size + 1}: {len(vectors)} vectors")
                    except Exception as e:
                        logging.error(f"Error uploading batch to Pinecone: {e}")
                        failed_uploads.extend([{"url": v["metadata"]["url"], "error": str(e)} for v in vectors])
            
            result = {
                "status": "success",
                "total_pages_processed": len(quality_pages),
                "total_uploaded": total_uploaded,
                "failed_uploads": len(failed_uploads),
                "failed_details": failed_uploads
            }
            
            logging.info(f"Pinecone upload complete: {total_uploaded} vectors uploaded, {len(failed_uploads)} failed")
            return result
            
        except Exception as e:
            logging.error(f"Error in save_to_pinecone: {e}")
            return {"status": "error", "message": str(e)} 