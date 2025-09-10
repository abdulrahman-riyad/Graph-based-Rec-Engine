#!/usr/bin/env python3
"""
start_backend.py
Windows-compatible script to start the backend server
"""

import os
import sys
from pathlib import Path
import multiprocessing

def main():
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    # Set environment variable for Python path
    os.environ['PYTHONPATH'] = str(backend_dir)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     E-COMMERCE INTELLIGENCE PLATFORM                        ║
║     Starting Backend Server...                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server at http://localhost:8000
📚 Documentation at http://localhost:8000/docs
🔧 Alternative docs at http://localhost:8000/redoc

Press CTRL+C to stop the server
""")
    
    # Run the server
    import uvicorn
    
    try:
        # Use --no-reload for Windows to avoid multiprocessing issues
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload on Windows
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Neo4j is running")
        print("2. Check if port 8000 is already in use")
        print("3. Verify all dependencies are installed: pip install -r backend/requirements.txt")
        print("4. Check backend/.env file for any invalid settings")
        sys.exit(1)

if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    main()