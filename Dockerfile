# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements first for better caching
COPY src/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py ./
COPY uploads ./uploads
COPY chroma_db ./chroma_db
COPY books.db ./books.db
COPY app.log ./app.log

# Create necessary directories
RUN mkdir -p uploads chroma_db

# Expose port
EXPOSE 8501

# Create a startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in the background\n\
ollama serve &\n\
\n# Wait for Ollama to start\n\
sleep 5\n\
\n# Pull the llama2 model\n\
ollama pull llama2\n\
\n# Start Streamlit\n\
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"] 