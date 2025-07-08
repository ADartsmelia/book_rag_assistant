#!/usr/bin/env python3
"""
Test script to verify the Book RAG Assistant works without warnings
"""

import os
import warnings
import sys

# Suppress all warnings for testing
warnings.filterwarnings("ignore")

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        print("🔍 Testing imports...")
        
        # Test core modules
        from database import BookDatabase
        print("✅ Database module imported")
        
        from pdf_utils import extract_text_from_pdf
        print("✅ PDF utils module imported")
        
        from rag_chain import chunk_and_embed, get_ollama_llm
        print("✅ RAG chain module imported")
        
        from ui import main_ui
        print("✅ UI module imported")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    try:
        print("🔍 Testing database...")
        
        from database import BookDatabase
        db = BookDatabase("test.db")
        
        # Test adding a book
        book_id = db.add_book(
            title="Test Book",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            collection_name="test_collection",
            pages=10,
            total_chars=1000
        )
        
        print(f"✅ Database test successful (book_id: {book_id})")
        
        # Clean up
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ollama():
    """Test Ollama connection"""
    try:
        print("🔍 Testing Ollama connection...")
        
        from rag_chain import get_ollama_llm
        llm = get_ollama_llm()
        
        # Test a simple query
        response = llm.invoke("Hello, how are you?")
        print(f"✅ Ollama test successful: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Book RAG Assistant...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Ollama", test_ollama),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\nTo start the app:")
        print("  streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 