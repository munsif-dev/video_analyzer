#!/usr/bin/env python3
"""
Video Content Analyzer - Run Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import openai
        import chromadb
        print("✓ Dependencies check passed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: uv sync")
        return False

def setup_environment():
    """Setup environment and data directories"""
    # Create data directories
    data_dirs = [
        'data',
        'data/transcripts',
        'data/notes', 
        'data/embeddings',
        'data/cache'
    ]
    
    for dir_path in data_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠ No .env file found. Please create one from .env.example")
        print("Required API keys: OPENAI_API_KEY, ASSEMBLYAI_API_KEY")
        return False
    
    print("✓ Environment setup complete")
    return True

def run_app():
    """Run the Streamlit application"""
    try:
        # Check if we're in a uv environment
        if os.path.exists('uv.lock'):
            cmd = ['uv', 'run', 'streamlit', 'run', 'app.py']
        else:
            cmd = ['streamlit', 'run', 'app.py']
        
        print("🚀 Starting Video Content Analyzer...")
        print("📱 App will open in your browser")
        print("Press Ctrl+C to stop")
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

def main():
    """Main entry point"""
    print("🎥 Video Content Analyzer")
    print("=" * 40)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    run_app()

if __name__ == "__main__":
    main()