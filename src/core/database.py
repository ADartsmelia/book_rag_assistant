import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

class BookDatabase:
    def __init__(self, db_path="books.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                collection_name TEXT NOT NULL,
                pages INTEGER,
                total_chars INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                summary TEXT NOT NULL,
                generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_book(self, title, filename, file_path, collection_name, pages=0, total_chars=0):
        """Add a new book to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO books (title, filename, file_path, collection_name, pages, total_chars)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, filename, file_path, collection_name, pages, total_chars))
        
        book_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return book_id
    
    def get_all_books(self):
        """Get all books from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, filename, pages, total_chars, upload_date, last_accessed
            FROM books
            ORDER BY last_accessed DESC
        ''')
        
        books = cursor.fetchall()
        conn.close()
        return books
    
    def get_book_by_id(self, book_id):
        """Get a specific book by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, filename, file_path, collection_name, pages, total_chars, upload_date
            FROM books
            WHERE id = ?
        ''', (book_id,))
        
        book = cursor.fetchone()
        conn.close()
        return book
    
    def update_last_accessed(self, book_id):
        """Update the last accessed timestamp for a book"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE books
            SET last_accessed = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (book_id,))
        
        conn.commit()
        conn.close()
    
    def add_chat_history(self, book_id, question, answer, sources=None):
        """Add a chat interaction to the history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sources_json = json.dumps(sources) if sources else None
        
        cursor.execute('''
            INSERT INTO chat_history (book_id, question, answer, sources)
            VALUES (?, ?, ?, ?)
        ''', (book_id, question, answer, sources_json))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, book_id, limit=50):
        """Get chat history for a specific book"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question, answer, sources, timestamp
            FROM chat_history
            WHERE book_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (book_id, limit))
        
        history = cursor.fetchall()
        conn.close()
        return history
    
    def add_summary(self, book_id, summary):
        """Add a generated summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO summaries (book_id, summary)
            VALUES (?, ?)
        ''', (book_id, summary))
        
        conn.commit()
        conn.close()
    
    def get_latest_summary(self, book_id):
        """Get the latest summary for a book"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT summary, generated_date
            FROM summaries
            WHERE book_id = ?
            ORDER BY generated_date DESC
            LIMIT 1
        ''', (book_id,))
        
        summary = cursor.fetchone()
        conn.close()
        return summary
    
    def delete_book(self, book_id):
        """Delete a book and all associated data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get book info before deletion
        cursor.execute('SELECT file_path, collection_name FROM books WHERE id = ?', (book_id,))
        book_info = cursor.fetchone()
        
        # Delete chat history
        cursor.execute('DELETE FROM chat_history WHERE book_id = ?', (book_id,))
        
        # Delete summaries
        cursor.execute('DELETE FROM summaries WHERE book_id = ?', (book_id,))
        
        # Delete book
        cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
        
        conn.commit()
        conn.close()
        
        # Delete physical files if they exist
        if book_info:
            file_path, collection_name = book_info
            
            # Delete the PDF file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
            
            # Delete vector store collection
            try:
                import shutil
                collection_path = f"./chroma_db/{collection_name}"
                if os.path.exists(collection_path):
                    shutil.rmtree(collection_path)
                    print(f"Deleted vector store: {collection_path}")
            except Exception as e:
                print(f"Error deleting vector store {collection_path}: {e}") 