#!/usr/bin/env python3
"""
Startup script for the Inventory Management System API server.
"""

import sys
import os
import uvicorn
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI server"""
    # Import after path setup
    from src.api.main import app
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
