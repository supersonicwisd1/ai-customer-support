python -c " 
import asyncio
from app.services.enhanced_knowledge_service import EnhancedKnowledgeService

async def run_enhanced_scrape():
    async with EnhancedKnowledgeService() as service:
        result = await service.build_comprehensive_knowledge_base()
        print(f'Enhanced scrape completed: {result}')

asyncio.run(run_enhanced_scrape())"