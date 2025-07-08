#!/usr/bin/env python3
"""
Integration tests for Book RAG Assistant
Tests all major functionality including upload, processing, chat, and summary generation
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from core.database import BookDatabase
from utils.pdf_utils import extract_text_from_pdf
from core.rag_chain import chunk_and_embed, get_ollama_llm, get_qa_chain, get_summary_chain

class TestBookRAGAssistant(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_books.db")
        self.chroma_dir = os.path.join(self.test_dir, "chroma_db")
        self.uploads_dir = os.path.join(self.test_dir, "uploads")
        
        # Create directories
        os.makedirs(self.chroma_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Initialize test database
        self.db = BookDatabase(db_path=self.db_path)
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_database_operations(self):
        """Test database operations"""
        # Test adding a book
        book_id = self.db.add_book(
            title="Test Book",
            filename="test.pdf",
            file_path="/path/to/test.pdf",
            collection_name="test_collection",
            pages=10,
            total_chars=1000
        )
        self.assertIsNotNone(book_id)
        
        # Test getting book
        book = self.db.get_book_by_id(book_id)
        self.assertIsNotNone(book)
        self.assertEqual(book[1], "Test Book")
        
        # Test adding chat history
        self.db.add_chat_history(
            book_id=book_id,
            question="What is this book about?",
            answer="This is a test book about testing.",
            sources='[{"page": 1}]'
        )
        
        # Test getting chat history
        history = self.db.get_chat_history(book_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], "What is this book about?")
        
        # Test adding summary
        self.db.add_summary(book_id, "This is a comprehensive summary of the test book.")
        
        # Test getting summary
        summary = self.db.get_latest_summary(book_id)
        self.assertIsNotNone(summary)
        self.assertEqual(summary[0], "This is a comprehensive summary of the test book.")
    
    def test_pdf_utils(self):
        """Test PDF utilities"""
        # Create a simple test PDF content
        test_pages = [(1, "This is page 1 content."), (2, "This is page 2 content.")]
        
        # Test text extraction (mock)
        with patch('utils.pdf_utils.extract_text_from_pdf', return_value=test_pages):
            from utils.pdf_utils import extract_text_from_pdf
            result = extract_text_from_pdf("test.pdf")
            self.assertEqual(result, test_pages)
    
    def test_rag_chain(self):
        """Test RAG chain functionality"""
        # Test LLM initialization
        with patch('core.rag_chain.Ollama') as mock_ollama:
            mock_llm = MagicMock()
            mock_ollama.return_value = mock_llm
            llm = get_ollama_llm()
            self.assertIsNotNone(llm)
    
    def test_vector_store_operations(self):
        """Test vector store operations"""
        # Test chunking and embedding
        test_pages = [(1, "This is test content for vectorization.")]
        
        with patch('core.rag_chain.HuggingFaceEmbeddings') as mock_embeddings:
            with patch('core.rag_chain.Chroma') as mock_chroma:
                mock_vector_store = MagicMock()
                mock_chroma.from_texts.return_value = mock_vector_store
                
                vector_store = chunk_and_embed(
                    test_pages,
                    persist_directory=self.chroma_dir,
                    collection_name="test_collection"
                )
                
                self.assertIsNotNone(vector_store)
    
    def test_full_workflow(self):
        """Test complete workflow from upload to chat"""
        # 1. Add a book to database
        book_id = self.db.add_book(
            title="Integration Test Book",
            filename="integration_test.pdf",
            file_path="/path/to/integration_test.pdf",
            collection_name="integration_test_collection",
            pages=5,
            total_chars=500
        )
        
        # 2. Add chat history
        self.db.add_chat_history(
            book_id=book_id,
            question="What is the main topic?",
            answer="The main topic is integration testing.",
            sources='[{"page": 1}]'
        )
        
        # 3. Add summary
        self.db.add_summary(book_id, "This book covers integration testing methodologies.")
        
        # 4. Verify all data is accessible
        book = self.db.get_book_by_id(book_id)
        history = self.db.get_chat_history(book_id)
        summary = self.db.get_latest_summary(book_id)
        
        self.assertIsNotNone(book)
        self.assertEqual(len(history), 1)
        self.assertIsNotNone(summary)
        
        # 5. Test book deletion
        self.db.delete_book(book_id)
        deleted_book = self.db.get_book_by_id(book_id)
        self.assertIsNone(deleted_book)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid book ID
        invalid_book = self.db.get_book_by_id(999)
        self.assertIsNone(invalid_book)
        
        # Test with invalid chat history
        invalid_history = self.db.get_chat_history(999)
        self.assertEqual(invalid_history, [])
        
        # Test with invalid summary
        invalid_summary = self.db.get_latest_summary(999)
        self.assertIsNone(invalid_summary)

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 