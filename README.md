# 🤖 ChatBot Plugin

A professional AI-powered chatbot widget that can be easily embedded into any website with just 2 lines of code.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your configuration
# See docs/DEPLOYMENT.md for detailed configuration options
```

### 3. Start the Server
```bash
python main.py
```

### 4. View Demo
Open your browser and go to: `http://localhost:8000`

## 📁 Project Structure

```
ChatBotPlugin/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── src/                    # Source code
│   ├── api/               # API layer
│   │   ├── __init__.py
│   │   └── app.py         # FastAPI application
│   ├── core/              # Core business logic
│   │   ├── __init__.py
│   │   └── rag.py         # RAG system implementation
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   └── pdf_util.py    # PDF processing utilities
│   └── static/            # Static assets
│       ├── js/
│       │   └── widget.js  # JavaScript widget
│       ├── css/
│       │   └── widget.css # Widget styles
│       └── html/
│           └── demo.html  # Demo page
├── config/                # Configuration
│   └── settings.py        # Application settings
├── docs/                  # Documentation
│   └── README.md          # Detailed documentation
├── chroma/                # ChromaDB storage
├── tmp/                   # Temporary files
└── chat_env/              # Virtual environment
```

## 🔧 Configuration

All configuration is managed through environment variables. Copy `env.example` to `.env` and customize the settings:

- **Server Settings**: Host, port, debug mode, logging
- **Admin Configuration**: Admin API key for client management
- **Database Settings**: ChromaDB and data storage paths
- **File Storage**: Temporary and static file directories
- **CORS Settings**: Allowed origins for cross-origin requests
- **Client Management**: Default plans and file size limits
- **RAG Configuration**: Text chunking and embedding model settings
- **Security**: API key and client ID prefixes

For detailed configuration options, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## 📚 Documentation

For detailed documentation, see [docs/README.md](docs/README.md).

## 🛠️ Development

### Running in Development Mode
```bash
python main.py
```

### Running with Uvicorn
```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Project Organization

- **`src/api/`**: FastAPI routes and endpoints
- **`src/core/`**: Core RAG functionality and business logic
- **`src/utils/`**: Utility functions and helpers
- **`src/static/`**: Frontend assets (JS, CSS, HTML)
- **`config/`**: Configuration files
- **`docs/`**: Documentation

## 🚀 Features

- ✅ **Easy Integration**: Add to any website with 2 lines of code
- ✅ **AI-Powered**: Advanced RAG (Retrieval-Augmented Generation) system
- ✅ **Document Support**: Upload PDFs, documents, and text files
- ✅ **Customizable**: Fully customizable appearance and behavior
- ✅ **Mobile Friendly**: Responsive design for all devices
- ✅ **Secure**: API key authentication and isolated data storage
- ✅ **Multi-tenant**: Each client gets isolated document storage

## 📄 License

This project is licensed under the MIT License.


<script src="http://localhost:8000/widget.js"></script>
<script>
ChatBotWidget.init({
    clientId: '[CLIENT_ID]',
    apiKey: '[API_KEY]',
    theme: 'light',
    position: 'bottom-right'
});
</script>