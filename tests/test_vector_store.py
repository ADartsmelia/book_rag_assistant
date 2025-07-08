#!/usr/bin/env python3
"""
Test script to check vector store functionality
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from rag_chain import chunk_and_embed, load_existing_vector_store
from database import BookDatabase

def test_vector_store():
    """Test vector store loading and querying"""
    print("Testing vector store functionality...")
    
    # Get book from database
    db = BookDatabase()
    books = db.get_all_books()
    
    if not books:
        print("❌ No books found in database")
        return
    
    print(f"📚 Found {len(books)} book(s) in database")
    
    for book in books:
        book_id, title, filename, pages, chars, upload_date, last_accessed = book
        print(f"\n📖 Testing book: {title}")
        print(f"   Pages: {pages}")
        print(f"   Characters: {chars}")
        
        # Get book details
        book_info = db.get_book_by_id(book_id)
        if not book_info:
            print(f"❌ Could not get book info for ID {book_id}")
            continue
            
        collection_name = book_info[4]  # collection_name
        print(f"   Collection: {collection_name}")
        
        try:
            # Try to load vector store
            print("   🔍 Loading vector store...")
            vector_store = load_existing_vector_store(persist_directory="./chroma_db", collection_name=collection_name)
            
            if not vector_store:
                print("   ❌ Could not load vector store")
                return
            
            # Test if collection has data
            print("   🔍 Testing collection data...")
            test_docs = vector_store.similarity_search("test", k=1)
            
            if test_docs:
                print(f"   ✅ Collection has {len(test_docs)} document(s)")
                print(f"   📄 First document preview: {test_docs[0].page_content[:100]}...")
            else:
                print("   ❌ Collection is empty!")
                
        except Exception as e:
            print(f"   ❌ Error loading vector store: {str(e)}")

if __name__ == "__main__":
    test_vector_store() 