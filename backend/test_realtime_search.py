#!/usr/bin/env python3
"""
Test script for real-time search functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.search_service import SearchService
from app.models.chat import SearchQuery

# Load environment variables
load_dotenv()

async def test_search_service():
    """Test the search service functionality"""
    
    print("🔍 Testing Real-time Search Service...")
    
    # Initialize search service
    search_service = SearchService()
    
    # Check if service is available
    if not search_service.is_available():
        print("⚠️  Search service not configured (missing API keys)")
        print("   To enable real-time search, set:")
        print("   - GOOGLE_SEARCH_API_KEY")
        print("   - GOOGLE_SEARCH_ENGINE_ID")
        return
    
    print("✅ Search service configured and available")
    
    # Test queries
    test_queries = [
        "Aven latest news",
        "Aven current rates",
        "Aven recent updates",
        "Aven new features"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        try:
            # Perform search
            results = await search_service.search(query, max_results=3)
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for j, result in enumerate(results, 1):
                    print(f"   {j}. {result.title}")
                    print(f"      Relevance: {result.relevance_score:.2f}")
                    print(f"      URL: {result.url}")
                    print(f"      Content: {result.content[:100]}...")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    print("\n🎉 Search service test completed!")

async def test_search_context():
    """Test search context generation"""
    
    print("\n🔍 Testing Search Context Generation...")
    
    search_service = SearchService()
    
    if not search_service.is_available():
        print("⚠️  Search service not available - skipping context test")
        return
    
    try:
        query = "Aven latest news"
        context = await search_service.get_search_context(query, max_results=2)
        
        if context:
            print(f"✅ Context generated successfully:")
            print(f"   Length: {len(context)} characters")
            print(f"   Preview: {context[:200]}...")
        else:
            print("❌ No context generated")
            
    except Exception as e:
        print(f"❌ Context generation error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_service())
    asyncio.run(test_search_context()) 