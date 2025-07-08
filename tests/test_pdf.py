#!/usr/bin/env python3
"""
Test PDF processing with a sample PDF
"""

import os
from pdf_utils import extract_text_from_pdf
from rag_chain import chunk_and_embed, get_ollama_llm, get_qa_chain

def test_pdf_processing():
    print("🧪 Testing PDF Processing")
    print("=" * 40)
    
    # Test PDF extraction
    pdf_path = "sample.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"📖 Processing: {pdf_path}")
    pages = extract_text_from_pdf(pdf_path)
    
    if not pages:
        print("❌ No text extracted from PDF")
        return False
    
    print(f"✅ Extracted {len(pages)} pages")
    total_chars = sum(len(text) for _, text in pages)
    print(f"📊 Total characters: {total_chars:,}")
    
    # Test chunking and embedding
    print("\n🔧 Testing chunking and embedding...")
    try:
        vector_store = chunk_and_embed(pages, collection_name="sample_document")
        print("✅ Vector store created successfully")
        
        # Test LLM connection
        print("\n🤖 Testing LLM connection...")
        llm = get_ollama_llm()
        qa_chain = get_qa_chain(vector_store, llm)
        print("✅ QA chain created successfully")
        
        # Test a simple question
        print("\n❓ Testing question answering...")
        result = qa_chain({"query": "What is this document about?"})
        answer = result['result']
        print(f"✅ Answer generated: {answer[:100]}...")
        
        print("\n🎉 All tests passed! The RAG system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

if __name__ == "__main__":
    test_pdf_processing() 