import asyncio
from app.services.scraper import Scraper
from app.services.pinecone_service import PineconeService
from app.services.openai_service import OpenAIService

async def main():
    sitemap_url = "https://aven.com/sitemap.xml"
    extra_links = [
        "https://www.trustpilot.com/review/aven.com",
        "https://www.aven.com/docs/CFPBCharmBooklet.pdf",
        "https://www.aven.com/docs/ESIGNConsent.pdf",
        "https://www.aven.com/docs/CFPBHELOCBooklet.pdf",
        "https://www.aven.com/docs/PrivacyPolicy.html",
        "https://www.aven.com/docs/ConsumerPrivacyPolicyNotice.pdf",
        "https://www.coastalbank.com/privacy-center/",
        "https://www.forbes.com/sites/jeffkauflin/2024/07/17/inside-fintechs-newest-unicorn-a-credit-card-backed-by-your-home/",
        "https://www.aven.com/docs/AutoPayAgreement.pdf",
        "https://www.aven.com/public/docs/CashbackTerms/post2025JunMoapBucket",
        "https://www.aven.com/public/docs/HelocGuaranteedLowestCost/post2025JunMoapBucket",
    ]
    
    # Initialize scraper
    scraper = Scraper(sitemap_url, extra_links)
    
    # Run scraping
    print("Starting scraping...")
    scraper.run()
    
    # Ask user if they want to upload to Pinecone
    upload_to_pinecone = input("\nDo you want to upload the scraped data to Pinecone? (y/n): ").lower().strip()
    
    if upload_to_pinecone == 'y':
        print("Initializing services for Pinecone upload...")
        try:
            pinecone_service = PineconeService()
            openai_service = OpenAIService()
            
            print("Uploading to Pinecone...")
            result = await scraper.save_to_pinecone(pinecone_service, openai_service)
            
            if result["status"] == "success":
                print(f"✅ Successfully uploaded {result['total_uploaded']} vectors to Pinecone")
                print(f"📊 Processed {result['total_pages_processed']} pages")
                if result['failed_uploads'] > 0:
                    print(f"⚠️  {result['failed_uploads']} uploads failed")
            else:
                print(f"❌ Upload failed: {result['message']}")
                
        except Exception as e:
            print(f"❌ Error during Pinecone upload: {e}")
    else:
        print("Skipping Pinecone upload.")

if __name__ == "__main__":
    asyncio.run(main()) 