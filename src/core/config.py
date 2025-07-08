import os
import warnings
import logging

def configure_app():
    """Configure the application to suppress warnings and telemetry"""
    
    # Disable ChromaDB telemetry
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
    
    # Disable LangChain telemetry
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    os.environ["LANGCHAIN_API_KEY"] = ""
    os.environ["LANGCHAIN_PROJECT"] = ""
    
    # Suppress specific warnings
    warnings.filterwarnings("ignore", message=".*torch.classes.*")
    warnings.filterwarnings("ignore", message=".*Examining the path of torch.classes.*")
    warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress specific logger warnings
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING) 