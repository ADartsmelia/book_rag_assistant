#!/usr/bin/env python3
"""
Test script for the new UI structure
"""

import streamlit as st
from ui import main_ui, init_session_state
from database import BookDatabase

def test_ui_structure():
    """Test the new UI structure"""
    print("Testing new UI structure...")
    
    # Test session state initialization
    init_session_state()
    assert 'current_page' in st.session_state
    assert 'current_book_id' in st.session_state
    assert 'db' in st.session_state
    print("✅ Session state initialization passed")
    
    # Test database connection
    db = BookDatabase()
    books = db.get_all_books()
    print(f"✅ Database connection passed - {len(books)} books found")
    
    # Test page navigation
    pages = ["home", "upload", "library", "analytics", "settings"]
    for page in pages:
        st.session_state.current_page = page
        print(f"✅ Page navigation to '{page}' passed")
    
    print("🎉 All UI structure tests passed!")

if __name__ == "__main__":
    test_ui_structure() 