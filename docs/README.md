# 📚 Book RAG Assistant

A production-ready, offline Retrieval-Augmented Generation (RAG) application for analyzing PDF books using local AI. Built with Streamlit, LangChain, Ollama, and ChromaDB.

## ✨ Features

- **🔒 100% Offline**: All processing happens locally on your machine
- **📖 Multi-Book Support**: Upload and manage multiple PDF books
- **💬 Chat Interface**: Ask questions about your books with context-aware answers
- **📝 Smart Summaries**: Generate comprehensive book summaries
- **📊 Analytics**: Track usage statistics and book insights
- **💾 Persistent Storage**: Save uploaded books, chat history, and summaries
- **🐳 Docker Support**: Easy deployment with Docker and docker-compose
- **📱 Modern UI**: Beautiful, responsive interface with Streamlit

## 🏗️ Architecture

```
Book RAG Assistant
├── 📄 PDF Upload & Processing
├── 🔍 Text Extraction (PyMuPDF + pdfminer)
├── 📝 Text Chunking & Embedding
├── 🗄️ Vector Storage (ChromaDB)
├── 🤖 Local LLM (Ollama + llama2)
├── 💬 Q&A Chain (LangChain)
├── 📊 Database (SQLite)
└── 🎨 Web UI (Streamlit)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- 8GB+ RAM (for LLM processing)
- 5GB+ free disk space

### Option 1: Local Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd book-rag-assistant
   ```

2. **Run the setup script**

   ```bash
   python setup_production.py
   ```

3. **Start the application**

   ```bash
   streamlit run app.py
   ```

4. **Access the app**
   Open http://localhost:8501 in your browser

### Option 2: Docker Deployment

1. **Build and run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

2. **Access the app**
   Open http://localhost:8501 in your browser

## 📋 Installation Details

### Manual Setup

1. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama**

   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Start Ollama and pull the model**

   ```bash
   ollama serve
   ollama pull llama2
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🎯 Usage Guide

### 1. Upload Books

- Click "Choose PDF files" in the sidebar
- Select one or more PDF files
- Click "Process Uploaded Files"
- Wait for processing to complete

### 2. Chat with Books

- Select a book from the sidebar
- Go to the "💬 Chat" tab
- Ask questions about the book content
- View source citations from the original text

### 3. Generate Summaries

- Select a book from the sidebar
- Go to the "📝 Summary" tab
- Click "Generate Summary"
- Download the summary as a text file

### 4. View Analytics

- Go to the "📊 Analytics" tab
- View statistics about your books
- Track usage and activity

## 🛠️ Configuration

The application uses a `config.ini` file for configuration:

```ini
[APP]
debug = false
log_level = INFO

[DATABASE]
path = books.db

[STORAGE]
uploads_dir = uploads
chroma_dir = chroma_db

[OLLAMA]
model = llama2
host = http://localhost:11434
```

## 📁 Project Structure

```
book-rag-assistant/
├── app.py                 # Main application
├── ui.py                  # UI components
├── database.py            # Database management
├── pdf_utils.py           # PDF processing
├── rag_chain.py           # RAG chains
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── setup_production.py   # Production setup script
├── uploads/              # Uploaded PDF files
├── chroma_db/            # Vector database
└── books.db              # SQLite database
```

## 🔧 Development

### Running Tests

```bash
python test_pdf.py
python test_setup.py
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Update tests
4. Submit pull request

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Configuration

```bash
# Override environment variables
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 📊 Performance

### System Requirements

- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 5GB+ for models and data

### Optimization Tips

- Use SSD storage for better I/O performance
- Increase Docker memory limits for large PDFs
- Monitor Ollama resource usage

## 🔒 Security

- All data stays on your local machine
- No external API calls (except model downloads)
- SQLite database with local file storage
- No user authentication required (single-user app)

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not running**

   ```bash
   ollama serve
   ```

2. **Model not found**

   ```bash
   ollama pull llama2
   ```

3. **Port already in use**

   ```bash
   streamlit run app.py --server.port 8502
   ```

4. **Memory issues**
   - Reduce chunk size in `rag_chain.py`
   - Use smaller models (llama2:7b instead of llama2:13b)

### Logs

- Application logs: Check Streamlit output
- Ollama logs: `ollama logs`
- Docker logs: `docker-compose logs`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

see LICENSE file for details

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [LangChain](https://langchain.com/) for the RAG framework
- [Ollama](https://ollama.ai/) for local LLM inference
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

## 📞 Support

For issues and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details
