import streamlit as st
import os
import sys
from datetime import datetime
import json
from core.database import BookDatabase
import tempfile
import uuid
from pathlib import Path
from utils.pdf_utils import extract_text_from_pdf
from core.rag_chain import chunk_and_embed, get_ollama_llm, get_summary_chain, load_existing_vector_store
import logging
logger = logging.getLogger(__name__)

def init_session_state():
    """Initialize session state variables"""
    if 'current_book_id' not in st.session_state:
        st.session_state.current_book_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'db' not in st.session_state:
        st.session_state.db = BookDatabase()
    if 'upload_processed' not in st.session_state:
        st.session_state.upload_processed = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True

def render_header():
    """Render the main header with centered title and logo"""
    st.set_page_config(
        page_title="Book RAG Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Centered header
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 1.5rem;">
        <img src="https://img.icons8.com/color/96/000000/book-shelf.png" width="60" style="margin-bottom: 0.5rem;"/>
        <h1 style="margin-bottom: 0.2rem;">Book RAG Assistant</h1>
        <div style="font-size: 1.2rem; color: #bbb;">Transform PDFs into Interactive Knowledge Bases</div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Render navigation sidebar (no quick actions, smaller width)"""
    sidebar_style = """
    <style>
    section[data-testid="stSidebar"] {
        min-width: 180px !important;
        max-width: 200px !important;
        width: 180px !important;
    }
    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)
    with st.sidebar:
        st.header("🧭 Navigation")
        pages = {
            "🏠 Home": "home",
            "📚 Library": "library", 
            "📤 Upload": "upload",
            "📊 Analytics": "analytics",
            "⚙️ Settings": "settings"
        }
        for page_name, page_id in pages.items():
            if st.button(page_name, key=f"sidebar_nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        st.markdown("---")

def render_home_page():
    """Render the home page with welcome and overview"""
    st.header("🎉 Welcome to Book RAG Assistant")
    
    # Welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Transform your PDF books into interactive knowledge bases!**
        
        This powerful application allows you to:
        - 📖 **Upload and process** PDF books with advanced text extraction
        - 💬 **Chat with your books** using AI-powered Q&A
        - 📝 **Generate comprehensive summaries** automatically
        - 📊 **Track your library** with detailed analytics
        - 🔒 **100% offline** - Your data stays on your machine
        
        **Everything runs locally - your privacy is guaranteed!**
        """)
    
    with col2:
        st.info("""
        **🚀 Quick Start:**
        1. Go to **Upload** page
        2. Select your PDF files
        3. Process and analyze
        4. Start chatting!
        """)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    books = st.session_state.db.get_all_books()
    
    if books:
        recent_books = books[:3]
        cols = st.columns(len(recent_books))
        
        for i, book in enumerate(recent_books):
            with cols[i]:
                book_id, title, filename, pages, chars, upload_date, last_accessed = book
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0;">
                    <h4>📖 {title}</h4>
                    <p><strong>Pages:</strong> {pages or 0}</p>
                    <p><strong>Last accessed:</strong> {last_accessed}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Open {title}", key=f"home_open_{book_id}"):
                    st.session_state.current_book_id = book_id
                    st.session_state.current_page = "library"
                    st.rerun()
    else:
        st.info("No books uploaded yet. Start by uploading your first PDF!")
        if st.button("📤 Upload Your First Book", type="primary", key="home_upload_first"):
            st.session_state.current_page = "upload"
            st.rerun()

def render_upload_page():
    """Render the upload page with simple file uploader"""
    st.header("📤 Upload Books")
    uploaded_files = st.file_uploader(
        "Select PDF files to analyze",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload and process",
        key="upload_page_uploader"
    )
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} file(s) selected")
        st.subheader("📋 Selected Files")
        file_data = []
        for file in uploaded_files:
            file_data.append({
                "Name": file.name,
                "Size": f"{file.size:,} bytes",
                "Type": file.type
            })
        st.dataframe(file_data, use_container_width=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Process Files", type="primary"):
                with st.spinner("Processing files..."):
                    process_uploaded_files(uploaded_files)
                    st.success("✅ Files processed successfully!")
                    st.session_state.current_page = "library"
                    st.rerun()
    st.markdown("---")
    st.subheader("💡 Upload Tips")
    st.markdown("""
    - **Supported format**: PDF files only
    - **File size**: Up to 100MB per file
    - **Processing time**: Depends on file size and content
    - **Text extraction**: Works best with searchable PDFs
    - **Multiple files**: You can upload several files at once
    """)

def render_library_page():
    """Render the library page with book management"""
    st.header("📚 Your Book Library")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search books...", placeholder="Enter book title or filename")
    with col2:
        sort_by = st.selectbox("Sort by", ["Recent", "Name", "Size", "Date"])
    
    # Get books
    books = st.session_state.db.get_all_books()
    
    if not books:
        st.info("""
        📖 **No books uploaded yet!**
        
        Upload your first PDF to get started with your digital library.
        """)
        if st.button("📤 Upload Your First Book", type="primary", key="library_upload_first"):
            st.session_state.current_page = "upload"
            st.rerun()
        return
    
    # Filter books based on search
    if search_term:
        books = [book for book in books if search_term.lower() in book[1].lower() or search_term.lower() in book[2].lower()]
    
    if not books:
        st.warning("No books match your search criteria.")
        return
    
    # Sort books
    if sort_by == "Recent":
        books = sorted(books, key=lambda x: x[6], reverse=True)  # last_accessed
    elif sort_by == "Name":
        books = sorted(books, key=lambda x: x[1])  # title
    elif sort_by == "Size":
        books = sorted(books, key=lambda x: x[4] or 0, reverse=True)  # total_chars
    elif sort_by == "Date":
        books = sorted(books, key=lambda x: x[5], reverse=True)  # upload_date
    
    # Display books in grid
    st.subheader(f"📚 {len(books)} Book(s)")
    
    # Pagination
    items_per_page = 6
    total_pages = (len(books) + items_per_page - 1) // items_per_page
    
    if 'library_page' not in st.session_state:
        st.session_state.library_page = 0
    
    # Page navigation
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.library_page == 0):
                st.session_state.library_page = max(0, st.session_state.library_page - 1)
                st.rerun()
        with col2:
            st.markdown(f"**Page {st.session_state.library_page + 1} of {total_pages}**")
        with col3:
            if st.button("Next ➡️", disabled=st.session_state.library_page == total_pages - 1):
                st.session_state.library_page = min(total_pages - 1, st.session_state.library_page + 1)
                st.rerun()
    
    # Display books for current page
    start_idx = st.session_state.library_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(books))
    current_books = books[start_idx:end_idx]
    
    # Book grid
    cols = st.columns(3)
    for i, book in enumerate(current_books):
        col = cols[i % 3]
        with col:
            book_id, title, filename, pages, chars, upload_date, last_accessed = book
            
            # Book card
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: {'#f0f8ff' if book_id == st.session_state.current_book_id else 'white'};">
                <h4>📖 {title}</h4>
                <p><strong>Pages:</strong> {pages or 0}</p>
                <p><strong>Characters:</strong> {chars or 0:,}</p>
                <p><strong>Uploaded:</strong> {upload_date}</p>
                <p><strong>Last accessed:</strong> {last_accessed}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📖 Open", key=f"open_{book_id}"):
                    st.session_state.current_book_id = book_id
                    st.session_state.db.update_last_accessed(book_id)
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{book_id}"):
                    # Add confirmation
                    if st.session_state.get(f"confirm_delete_{book_id}", False):
                        st.session_state.db.delete_book(book_id)
                        if st.session_state.current_book_id == book_id:
                            st.session_state.current_book_id = None
                        # Clear confirmation state
                        if f"confirm_delete_{book_id}" in st.session_state:
                            del st.session_state[f"confirm_delete_{book_id}"]
                        st.rerun()
                    else:
                        # Show confirmation
                        st.session_state[f"confirm_delete_{book_id}"] = True
                        st.warning(f"⚠️ Are you sure you want to delete '{title}'? Click Delete again to confirm.")
                        st.rerun()
            with col3:
                if st.button("📊 Info", key=f"info_{book_id}"):
                    st.session_state.current_book_id = book_id
                    st.session_state.current_page = "book_detail"
                    st.rerun()
    
    # Current book interface
    if st.session_state.current_book_id:
        st.markdown("---")
        render_current_book_interface()

def render_current_book_interface():
    """Render the current book interface"""
    book_info = st.session_state.db.get_book_by_id(st.session_state.current_book_id)
    if not book_info:
        st.error("Book not found!")
        return
    
    st.header(f"📖 {book_info[1]}")
    
    # Book metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages", book_info[5] or 0)
    with col2:
        chars = int(book_info[6] or 0)
        st.metric("Characters", f"{chars:,}")
    with col3:
        st.metric("Upload Date", str(book_info[7]))
    with col4:
        history_count = len(st.session_state.db.get_chat_history(st.session_state.current_book_id))
        st.metric("Conversations", history_count)
    
    # Book actions
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📝 Summary", "📊 History", "⚙️ Settings"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_summary_tab()
    
    with tab3:
        render_history_tab()
    
    with tab4:
        render_book_settings_tab()

def render_chat_tab():
    """Render the chat tab (history only, no chat_input here)"""
    if st.session_state.current_book_id is None:
        st.info("👆 Please select a book from the library to start chatting!")
        return
    book_info = st.session_state.db.get_book_by_id(st.session_state.current_book_id)
    if book_info and book_info[5] == 0:
        st.warning("⚠️ This book hasn't been processed yet. Please re-upload and process the book.")
        return
    
    # Display chat history/messages only
    history = st.session_state.db.get_chat_history(st.session_state.current_book_id)
    
    # Show current question being processed if loading
    if st.session_state.get("chat_loading", False) and st.session_state.get("pending_question"):
        with st.chat_message("user"):
            st.write(st.session_state.pending_question)
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                st.write("Processing your question...")
    
    # Display chat history
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    for question, answer, sources, timestamp in reversed(history):
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(answer)
            if sources:
                try:
                    sources_data = json.loads(sources)
                    if sources_data:
                        st.caption("📄 Sources:")
                        for i, source in enumerate(sources_data[:3]):
                            st.caption(f"  {i+1}. Page {source.get('page', 'N/A')}")
                except:
                    pass
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

def generate_summary_for_book(book_id):
    """Generate summary for a specific book"""
    try:
        book_info = st.session_state.db.get_book_by_id(book_id)
        if not book_info:
            return False, "Book not found"
        
        collection_name = book_info[4]
        vector_store = load_existing_vector_store(persist_directory="./chroma_db", collection_name=collection_name)
        
        if not vector_store:
            return False, "Could not load vector store"
        
        # Test if vector store has content
        test_docs = vector_store.similarity_search("test", k=1)
        if not test_docs:
            return False, "Vector store is empty"
        
        llm = get_ollama_llm()
        summary_chain = get_summary_chain(vector_store, llm)
        
        with st.spinner("Generating summary..."):
            summary_result = summary_chain()
            # Extract the result string from the dictionary
            if isinstance(summary_result, dict) and 'result' in summary_result:
                summary = summary_result['result']
            else:
                summary = str(summary_result)
        
        if summary:
            st.session_state.db.add_summary(book_id, summary)
            return True, summary
        else:
            return False, "No summary generated"
            
    except Exception as e:
        logger.exception(f"Error generating summary for book {book_id}: {e}")
        return False, str(e)

def render_summary_tab():
    """Render the summary tab (summary only, no chat)"""
    if st.session_state.current_book_id is None:
        st.info("👆 Please select a book from the library to view a summary!")
        return
    book_info = st.session_state.db.get_book_by_id(st.session_state.current_book_id)
    if not book_info:
        st.error("Book not found!")
        return
    if book_info[5] == 0:
        st.warning("⚠️ This book hasn't been processed yet. Please re-upload and process the book.")
        return
    st.subheader("📝 Book Summary")
    existing_summary = st.session_state.db.get_latest_summary(st.session_state.current_book_id)
    if existing_summary:
        st.success("✅ Summary generated!")
        st.text_area(
            "Generated Summary:",
            value=existing_summary[0],
            height=300,
            disabled=True
        )
        st.download_button(
            label="📥 Download Summary",
            data=existing_summary[0],
            file_name=f"{book_info[1]}_summary.txt",
            mime="text/plain"
        )
    else:
        st.info("No summary available yet.")
        if st.button("🔄 Generate Summary", key="generate_summary_button"):
            success, result = generate_summary_for_book(st.session_state.current_book_id)
            if success:
                st.success("✅ Summary generated successfully!")
                st.rerun()
            else:
                st.error(f"❌ Failed to generate summary: {result}")

def render_history_tab():
    """Render the history tab"""
    if st.session_state.current_book_id is None:
        st.info("👆 Please select a book to view chat history!")
        return
    
    history = st.session_state.db.get_chat_history(st.session_state.current_book_id)
    
    if not history:
        st.info("No chat history yet. Start a conversation in the Chat tab!")
        return
    
    st.subheader("📊 Chat History")
    
    for i, (question, answer, sources, timestamp) in enumerate(history):
        with st.expander(f"Q&A #{len(history) - i} - {timestamp}"):
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Answer:** {answer}")
            if sources:
                try:
                    sources_data = json.loads(sources)
                    if sources_data:
                        st.markdown("**Sources:**")
                        for j, source in enumerate(sources_data[:3]):
                            st.markdown(f"  {j+1}. Page {source.get('page', 'N/A')}")
                except:
                    pass

def render_book_settings_tab():
    """Render the book settings tab"""
    if st.session_state.current_book_id is None:
        st.info("👆 Please select a book to view settings!")
        return
    
    book_info = st.session_state.db.get_book_by_id(st.session_state.current_book_id)
    if not book_info:
        st.error("Book not found!")
        return
    
    st.subheader("⚙️ Book Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Book Information:**
        - **Title:** {book_info[1]}
        - **Filename:** {book_info[2]}
        - **Pages:** {book_info[5] or 0}
        - **Characters:** {book_info[6] or 0:,}
        - **Upload Date:** {book_info[7]}
        """)
    
    with col2:
        st.subheader("Actions")
        if st.button("🗑️ Delete Book", type="secondary", key="settings_delete_book"):
            # Add confirmation
            if st.session_state.get("confirm_settings_delete", False):
                st.session_state.db.delete_book(st.session_state.current_book_id)
                st.session_state.current_book_id = None
                # Clear confirmation state
                if "confirm_settings_delete" in st.session_state:
                    del st.session_state["confirm_settings_delete"]
                st.rerun()
            else:
                # Show confirmation
                st.session_state["confirm_settings_delete"] = True
                st.warning(f"⚠️ Are you sure you want to delete this book? Click Delete again to confirm.")
                st.rerun()
        
        if st.button("🔄 Reprocess Book", type="secondary"):
            st.info("Reprocessing feature coming soon!")

def render_analytics_page():
    """Render the analytics page"""
    st.header("📊 Analytics Dashboard")
    
    books = st.session_state.db.get_all_books()
    
    if not books:
        st.info("No books uploaded yet!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Books", len(books))
    
    with col2:
        total_pages = sum(book[3] or 0 for book in books)
        st.metric("Total Pages", total_pages)
    
    with col3:
        total_chars = sum(int(book[4] or 0) for book in books)
        st.metric("Total Characters", f"{total_chars:,}")
    
    with col4:
        total_chats = sum(len(st.session_state.db.get_chat_history(book[0])) for book in books)
        st.metric("Total Conversations", total_chats)
    
    # Charts and visualizations
    st.subheader("📈 Usage Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Books by Size")
        # Simple bar chart of book sizes
        book_sizes = [(book[1], book[4] or 0) for book in books]
        book_sizes.sort(key=lambda x: x[1], reverse=True)
        
        for title, size in book_sizes[:5]:
            st.markdown(f"**{title}:** {size:,} characters")
    
    with col2:
        st.subheader("🕒 Recent Activity")
        recent_books = books[:5]
        for book in recent_books:
            book_id, title, filename, pages, chars, upload_date, last_accessed = book
            st.caption(f"📖 {title} - Last accessed: {last_accessed}")

def render_settings_page():
    """Render the settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("Application Settings")
    
    # Database info
    st.markdown("**Database Information:**")
    books = st.session_state.db.get_all_books()
    st.markdown(f"- Total books: {len(books)}")
    st.markdown(f"- Database file: books.db")
    
    # System info
    st.subheader("System Information")
    st.markdown(f"- Python version: {sys.version}")
    st.markdown(f"- Working directory: {os.getcwd()}")
    
    # Actions
    st.subheader("Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.warning("This will delete all books and data. Are you sure?")
            # Add confirmation dialog here
    
    with col2:
        if st.button("📥 Export Data", type="secondary"):
            st.info("Export feature coming soon!")

def render_chat_input():
    """Render the chat input (outside tabs)"""
    if st.session_state.current_book_id is None:
        return
    
    # Initialize loading state if not exists
    if "chat_loading" not in st.session_state:
        st.session_state["chat_loading"] = False
    
    # Disable chat input if waiting for answer
    disabled = st.session_state.get("chat_loading", False)
    
    # Show loading indicator if processing
    if disabled:
        st.info("🔄 Processing your question... Please wait.")
    
    prompt = st.chat_input(
        "Ask a question about your book...", 
        key="main_chat_input", 
        disabled=disabled
    )
    
    if prompt and not disabled:
        # Set loading state immediately
        st.session_state["chat_loading"] = True
        st.session_state.pending_question = prompt
        # Force rerun to show loading state
        st.rerun()

def process_uploaded_files(uploaded_files):
    """Process uploaded PDF files and store in database"""
    if not uploaded_files:
        return
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    processed_count = 0
    
    for uploaded_file in uploaded_files:
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = uploaded_file.name
            file_path = uploads_dir / f"{file_id}_{filename}"
            logger.info(f"Saving uploaded file: {file_path}")
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Extract text from PDF
            pages = extract_text_from_pdf(str(file_path))
            if not pages or all(not t[1].strip() for t in pages):
                logger.warning(f"No extractable text found in {filename}")
                st.error(f"No extractable text found in {filename}")
                continue
            
            # Calculate statistics
            total_chars = sum(len(text) for _, text in pages)
            total_pages = len(pages)
            
            # Generate collection name
            collection_name = f"book_{file_id}"
            logger.info(f"Embedding and storing vector store for: {collection_name}")
            
            # Store in vector database
            vector_store = chunk_and_embed(
                pages, 
                persist_directory="./chroma_db", 
                collection_name=collection_name
            )
            
            # Add to database
            book_id = st.session_state.db.add_book(
                title=filename.replace('.pdf', ''),
                filename=filename,
                file_path=str(file_path),
                collection_name=collection_name,
                pages=total_pages,
                total_chars=total_chars
            )
            
            # --- Automatic summary generation ---
            try:
                llm = get_ollama_llm()
                summary_chain = get_summary_chain(vector_store, llm)
                logger.info(f"Generating summary for {filename} (book_id={book_id})")
                with st.spinner(f"Generating summary for {filename}..."):
                    summary_result = summary_chain()
                    # Extract the result string from the dictionary
                    if isinstance(summary_result, dict) and 'result' in summary_result:
                        summary = summary_result['result']
                    else:
                        summary = str(summary_result)
                if summary:
                    st.session_state.db.add_summary(book_id, summary)
                    logger.info(f"Summary generated and stored for {filename} (book_id={book_id})")
                else:
                    logger.warning(f"Summary chain returned no summary for {filename}")
            except Exception as e:
                logger.exception(f"Could not generate summary for {filename}: {e}")
                st.warning(f"Could not generate summary for {filename}: {e}")
            
            processed_count += 1
            
        except Exception as e:
            logger.exception(f"Error processing {uploaded_file.name}: {e}")
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
    
    if processed_count > 0:
        logger.info(f"Successfully processed {processed_count} file(s)")
        st.success(f"✅ Successfully processed {processed_count} file(s)")
        st.session_state.upload_processed = True
        st.rerun()

def render_footer():
    """Render the footer"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>📚 Book RAG Assistant | Built with Streamlit, LangChain, and Ollama</p>
            <p>🔒 100% Offline - Your data stays on your machine</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main_ui():
    """Main UI function with page-based navigation"""
    init_session_state()
    render_header()
    render_navigation()
    
    # Page routing
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "upload":
        render_upload_page()
    elif st.session_state.current_page == "library":
        render_library_page()
    elif st.session_state.current_page == "analytics":
        render_analytics_page()
    elif st.session_state.current_page == "settings":
        render_settings_page()
    elif st.session_state.current_page == "book_detail":
        render_current_book_interface()
    else:
        render_home_page()
    
    # Place chat_input at the root level, only if library page and book is selected
    if (
        st.session_state.current_page == "library"
        and st.session_state.current_book_id is not None
    ):
        render_chat_input()
    
    render_footer() 