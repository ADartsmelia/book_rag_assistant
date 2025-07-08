import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", message=".*Examining the path of torch.classes.*")
warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

# Chunk and embed text, store in Chroma

def chunk_and_embed(pages, persist_directory="./chroma_db", collection_name="default_book"):
    """
    pages: list of (page_num, text)
    Returns: Chroma vector store
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = []
    metadatas = []
    for page_num, text in pages:
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({"page": page_num})
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    return vector_store

def load_existing_vector_store(persist_directory="./chroma_db", collection_name="default_book"):
    """
    Load an existing vector store collection
    Returns: Chroma vector store or None if collection doesn't exist
    """
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        vector_store = Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=embeddings
        )
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None


def get_ollama_llm(model_name="llama2"):
    return Ollama(model=model_name)


def get_qa_chain(vector_store, llm):
    prompt_template = """You are a helpful assistant that answers questions about a book based on the provided context.\n\nContext: {context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer based only on the information in the context. If the context doesn't contain enough information to answer the question, say so.\n\nAnswer:"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return qa_chain


def get_summary_chain(vector_store, llm):
    summary_prompt = """Based on the following context from a book, provide a comprehensive summary including:\n\n1. Main themes and topics\n2. Key concepts and ideas\n3. Important characters or subjects (if applicable)\n4. Overall structure and organization\n\nContext: {context}\n\nPlease provide a detailed summary:"""
    prompt = PromptTemplate(
        template=summary_prompt,
        input_variables=["context"]
    )
    
    # Create a simple chain for summary generation
    summary_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 20}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )
    
    return lambda: summary_chain.invoke({"query": "Generate a comprehensive summary of this book"}) 