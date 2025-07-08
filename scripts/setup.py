#!/usr/bin/env python3
"""
Setup script for Offline Book RAG Application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def check_ollama():
    """Check if Ollama is installed and running"""
    print("Checking Ollama installation...")
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if llama2 model is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama2" in result.stdout:
                print("✅ llama2 model is available")
                return True
            else:
                print("⚠️  llama2 model not found. Installing...")
                subprocess.run(["ollama", "pull", "llama2"])
                print("✅ llama2 model installed")
                return True
        else:
            print("❌ Ollama not found. Please install Ollama first.")
            print("Visit: https://ollama.ai/")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found. Please install Ollama first.")
        print("Visit: https://ollama.ai/")
        return False

def main():
    print("🚀 Setting up Offline Book RAG Application")
    print("=" * 50)
    
    # Install Python packages
    if not install_requirements():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Please install Ollama before running the application.")
        print("Visit: https://ollama.ai/")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\nTo run the application:")
    print("streamlit run app.py")
    
    print("\nTo start Ollama (if not already running):")
    print("ollama serve")

if __name__ == "__main__":
    main() 