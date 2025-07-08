import streamlit as st
import os
import warnings
import json
import logging
from ui.main_ui import main_ui
from core.rag_chain import get_ollama_llm, get_qa_chain, get_summary_chain, chunk_and_embed, load_existing_vector_store
from core.database import BookDatabase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Suppress telemetry
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TELEMETRY"] = "false"

def handle_chat_interaction():
    """Handle chat interactions when a question is asked"""
    if hasattr(st.session_state, 'pending_question') and st.session_state.pending_question:
        question = st.session_state.pending_question
        book_id = st.session_state.current_book_id
        logger.info(f"Chat question received: {question} (book_id={book_id})")
        if book_id:
            try:
                db = BookDatabase()
                book_info = db.get_book_by_id(book_id)
                if book_info:
                    llm = get_ollama_llm()
                    collection_name = book_info[4]
                    logger.info(f"Loading vector store for collection: {collection_name}")
                    vector_store = load_existing_vector_store(persist_directory="./chroma_db", collection_name=collection_name)
                    if not vector_store:
                        logger.error("Could not load vector store.")
                        st.error("❌ Could not load book data. Please re-upload and process the book.")
                        st.session_state["chat_loading"] = False
                        return
                    test_docs = vector_store.similarity_search("test", k=1)
                    if not test_docs:
                        logger.error("Vector store is empty.")
                        st.error("❌ This book has no processed content. Please re-upload and process the book.")
                        st.session_state["chat_loading"] = False
                        return
                    qa_chain = get_qa_chain(vector_store, llm)
                    logger.info("Invoking QA chain...")
                    response = qa_chain.invoke({"query": question})
                    sources = []
                    if hasattr(response, 'source_documents'):
                        for doc in response.source_documents:
                            if hasattr(doc, 'metadata'):
                                sources.append(doc.metadata)
                    db.add_chat_history(
                        book_id=book_id,
                        question=question,
                        answer=response['result'] if 'result' in response else str(response),
                        sources=json.dumps(sources) if sources else None
                    )
                    db.update_last_accessed(book_id)
                    del st.session_state.pending_question
                    st.session_state["chat_loading"] = False
                    logger.info("Chat answer stored and UI updated.")
                    st.rerun()
                else:
                    logger.error("Book not found in database.")
                    st.error("❌ Book not found!")
                    st.session_state["chat_loading"] = False
            except Exception as e:
                logger.exception(f"Error processing chat question: {e}")
                st.error(f"❌ Error processing question: {str(e)}")
                if hasattr(st.session_state, 'pending_question'):
                    del st.session_state.pending_question
                st.session_state["chat_loading"] = False

def handle_summary_generation():
    """Handle summary generation requests"""
    if hasattr(st.session_state, 'generate_summary') and st.session_state.generate_summary:
        book_id = st.session_state.current_book_id
        logger.info(f"Manual summary generation triggered for book_id={book_id}")
        if book_id:
            try:
                db = BookDatabase()
                book_info = db.get_book_by_id(book_id)
                if book_info:
                    llm = get_ollama_llm()
                    collection_name = book_info[4]
                    logger.info(f"Loading vector store for summary: {collection_name}")
                    vector_store = load_existing_vector_store(persist_directory="./chroma_db", collection_name=collection_name)
                    if not vector_store:
                        logger.error("Could not load vector store for summary.")
                        st.error("❌ Could not load book data. Please re-upload and process the book.")
                        return
                    test_docs = vector_store.similarity_search("test", k=1)
                    if not test_docs:
                        logger.error("Vector store is empty for summary.")
                        st.error("❌ This book has no processed content. Please re-upload and process the book.")
                        return
                    summary_chain = get_summary_chain(vector_store, llm)
                    logger.info("Invoking summary chain...")
                    summary = summary_chain()
                    if summary:
                        db.add_summary(book_id, summary)
                        st.success("✅ Summary generated successfully!")
                        del st.session_state.generate_summary
                        logger.info("Summary stored in database.")
                    else:
                        logger.error("Summary chain returned no summary.")
                        st.error("❌ Unable to generate summary. Please try again.")
                else:
                    logger.error("Book not found in database for summary.")
                    st.error("❌ Book not found!")
            except Exception as e:
                logger.exception(f"Error generating summary: {e}")
                st.error(f"❌ Error generating summary: {str(e)}")
                if hasattr(st.session_state, 'generate_summary'):
                    del st.session_state.generate_summary

def main():
    logger.info("Starting Book RAG Assistant app...")
    db = BookDatabase()
    main_ui()
    handle_chat_interaction()
    handle_summary_generation()

if __name__ == "__main__":
    main() 