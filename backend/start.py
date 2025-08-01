#!/usr/bin/env python3
"""
Startup script for Render deployment
Handles environment setup and graceful startup
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY', 
        'PINECONE_ENVIRONMENT',
        'VAPI_PRIVATE_KEY',
        'VAPI_PUBLIC_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly")
    else:
        logger.info("All required environment variables are set")

def main():
    """Main startup function"""
    try:
        logger.info("Starting Aven AI Support Backend...")
        
        # Check environment
        check_environment()
        
        # Import and start the app
        from app.main import app
        import uvicorn
        
        # Get port from environment (Render sets PORT)
        port = int(os.getenv('PORT', 9003))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Starting server on {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 