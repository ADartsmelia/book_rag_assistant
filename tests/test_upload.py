#!/usr/bin/env python3
"""
Test script to verify file upload and processing functionality
"""

import os
import tempfile
from pathlib import Path
from database import BookDatabase
from pdf_utils import extract_text_from_pdf
from rag_chain import chunk_and_embed

def create_test_pdf():
    """Create a simple test PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            c = canvas.Canvas(tmp_file.name, pagesize=letter)
            c.drawString(100, 750, "Test Book Title")
            c.drawString(100, 700, "This is a test PDF for the Book RAG Assistant.")
            c.drawString(100, 650, "It contains sample text to test the upload functionality.")
            c.drawString(100, 600, "The application should be able to process this file.")
            c.drawString(100, 550, "And extract the text content for analysis.")
            c.save()
            return tmp_file.name
    except ImportError:
        print("⚠️  reportlab not installed, creating dummy text file instead")
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"Test Book Content\nThis is a test file for the Book RAG Assistant.")
            return tmp_file.name

def test_file_processing():
    """Test the complete file processing pipeline"""
    print("🧪 Testing file processing pipeline...")
    
    # Create test file
    test_file = create_test_pdf()
    print(f"✅ Created test file: {test_file}")
    
    try:
        # Test PDF extraction
        if test_file.endswith('.pdf'):
            pages = extract_text_from_pdf(test_file)
            print(f"✅ PDF extraction successful: {len(pages)} pages")
        else:
            # For text files, create dummy pages
            with open(test_file, 'r') as f:
                content = f.read()
            pages = [(1, content)]
            print(f"✅ Text file processing: {len(pages)} pages")
        
        # Test database operations
        db = BookDatabase("test_upload.db")
        print("✅ Database initialized")
        
        # Test vector storage
        collection_name = "test_collection"
        vector_store = chunk_and_embed(
            pages,
            persist_directory="./test_chroma_db",
            collection_name=collection_name
        )
        print("✅ Vector storage successful")
        
        # Test database insertion
        book_id = db.add_book(
            title="Test Book",
            filename="test.pdf",
            file_path=test_file,
            collection_name=collection_name,
            pages=len(pages),
            total_chars=sum(len(text) for _, text in pages)
        )
        print(f"✅ Database insertion successful: book_id={book_id}")
        
        # Test retrieval
        books = db.get_all_books()
        print(f"✅ Database retrieval successful: {len(books)} books")
        
        # Cleanup
        os.unlink(test_file)
        if os.path.exists("test_upload.db"):
            os.unlink("test_upload.db")
        if os.path.exists("./test_chroma_db"):
            import shutil
            shutil.rmtree("./test_chroma_db")
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Book RAG Assistant Upload Functionality")
    print("=" * 60)
    
    if test_file_processing():
        print("\n✅ Upload functionality is working correctly!")
        print("\nTo test the full application:")
        print("1. Open http://localhost:8505 in your browser")
        print("2. Upload a PDF file in the sidebar")
        print("3. Click 'Process Uploaded Files'")
        print("4. Select the book from the dropdown")
        print("5. Start chatting or generating summaries!")
    else:
        print("\n❌ Upload functionality has issues. Please check the errors above.")

if __name__ == "__main__":
    main() 