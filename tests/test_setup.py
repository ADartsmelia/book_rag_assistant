#!/usr/bin/env python3
"""
Test script to verify Offline Book RAG setup
"""

import sys
import subprocess
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    packages = [
        'streamlit',
        'PyPDF2',  # Changed from fitz
        'langchain',
        'langchain_community',
        'chromadb',
        'sentence_transformers',
        'ollama',
        'numpy',
        'pandas'
    ]
    
    failed_imports = []
    
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_ollama():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    
    try:
        from langchain.llms import Ollama
        llm = Ollama(model="llama2")
        
        # Test with a simple prompt
        response = llm("Hello, this is a test. Please respond with 'Test successful' if you can see this message.")
        print("✅ Ollama connection successful")
        print(f"Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_embeddings():
    """Test sentence transformers"""
    print("\nTesting embeddings...")
    
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Test embedding
        test_text = "This is a test sentence."
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ Embeddings working (vector size: {len(embedding)})")
        return True
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False

def test_chroma():
    """Test ChromaDB"""
    print("\nTesting ChromaDB...")
    
    try:
        import chromadb
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Test vector store creation
        texts = ["This is a test document.", "This is another test document."]
        vector_store = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            persist_directory="./test_chroma_db"
        )
        
        # Test similarity search
        results = vector_store.similarity_search("test", k=1)
        
        print("✅ ChromaDB working")
        return True
    except Exception as e:
        print(f"❌ ChromaDB failed: {e}")
        return False

def main():
    print("🧪 Testing Offline Book RAG Setup")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Ollama Connection", test_ollama),
        ("Embeddings", test_embeddings),
        ("ChromaDB", test_chroma)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        print("\nCommon issues:")
        print("- Install Ollama: https://ollama.ai/")
        print("- Run: ollama pull llama2")
        print("- Install requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 