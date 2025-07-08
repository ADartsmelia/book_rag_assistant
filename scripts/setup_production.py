#!/usr/bin/env python3
"""
Production setup script for Book RAG Assistant
"""

import os
import sys
from pathlib import Path
import subprocess

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and accessible")
            return True
        else:
            print("❌ Ollama is not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama if not present"""
    print("📦 Installing Ollama...")
    try:
        subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                      shell=True, check=True)
        print("✅ Ollama installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Ollama")
        return False

def pull_llama_model():
    """Pull the llama2 model"""
    print("📥 Pulling llama2 model...")
    try:
        subprocess.run(["ollama", "pull", "llama2"], check=True)
        print("✅ llama2 model downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to download llama2 model")
        return False

def check_python_dependencies():
    """Check if all Python dependencies are installed"""
    required_packages = [
        "streamlit",
        "langchain",
        "langchain_community",
        "chromadb",
        "sentence_transformers",
        "torch"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All Python dependencies are installed")
        return True

def create_config():
    """Create configuration file"""
    config_content = """# Book RAG Assistant Configuration
[APP]
debug = false
log_level = INFO

[DATABASE]
path = books.db

[STORAGE]
uploads_dir = uploads
chroma_dir = chroma_db

[OLLAMA]
model = llama2
host = http://localhost:11434
"""
    
    with open("config.ini", "w") as f:
        f.write(config_content)
    print("✅ Created config.ini")

def main():
    """Main setup function"""
    print("🚀 Setting up Book RAG Assistant for production...")
    
    # Create directories
    create_directories()
    
    # Check Python dependencies
    if not check_python_dependencies():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("📦 Installing Ollama...")
        if not install_ollama():
            print("❌ Failed to install Ollama. Please install manually.")
            sys.exit(1)
    
    # Pull model
    if not pull_llama_model():
        print("❌ Failed to pull llama2 model")
        sys.exit(1)
    
    # Create config
    create_config()
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("  Local: streamlit run app.py")
    print("  Docker: docker-compose up --build")
    print("\nThe application will be available at: http://localhost:8501")

if __name__ == "__main__":
    main() 