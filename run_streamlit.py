#!/usr/bin/env python3
"""
Simple script to run the Streamlit frontend for Blood Test Analyzer
Make sure the FastAPI backend is running on localhost:8000 first
"""

import subprocess
import sys
import time
import requests

def check_backend():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🩸 Blood Test Analyzer - Streamlit Frontend")
    print("=" * 50)
    
    # Check if backend is running
    if not check_backend():
        print("❌ FastAPI backend is not running!")
        print("Please start the backend first:")
        print("   cd blood-test-analyser-debug")
        print("   python main.py")
        print("\nThen run this script again.")
        return
    
    print("✅ FastAPI backend is running")
    print("🚀 Starting Streamlit frontend...")
    print("\nStreamlit will open automatically in your browser")
    print("URL: http://localhost:8501")
    print("\nPress Ctrl+C to stop")
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.headless=false",
            "--server.runOnSave=true",
            "--theme.primaryColor=#ff4b4b"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit frontend stopped")

if __name__ == "__main__":
    main() 