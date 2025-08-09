# 🤖 ChatBot Widget

A professional AI-powered chatbot widget that can be easily embedded into any website with just 2 lines of code.

## Features

- ✅ **Easy Integration**: Add to any website with 2 lines of code
- ✅ **AI-Powered**: Advanced RAG (Retrieval-Augmented Generation) system
- ✅ **Document Support**: Upload PDFs, documents, and text files
- ✅ **Customizable**: Fully customizable appearance and behavior
- ✅ **Mobile Friendly**: Responsive design for all devices
- ✅ **Secure**: API key authentication and isolated data storage
- ✅ **Multi-tenant**: Each client gets isolated document storage

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. View Demo

Open your browser and go to: `http://localhost:8000`

## Integration Guide

### For Website Owners

Add the chatbot to your website in just 2 steps:

```html
<!-- Step 1: Add the widget script -->
<script src="https://your-domain.com/widget.js"></script>

<!-- Step 2: Initialize with your settings -->
<script>
  ChatBotWidget.init({
    clientId: 'your-client-id',
    apiKey: 'your-api-key',
    title: 'Chat with us',
    primaryColor: '#007bff'
  });
</script>
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `clientId` | string | ✅ | - | Your unique client identifier |
| `apiKey` | string | ✅ | - | Your API authentication key |
| `title` | string | ❌ | "Chat with us" | Chat window title |
| `primaryColor` | string | ❌ | "#007bff" | Main color theme |
| `position` | string | ❌ | "bottom-right" | Widget position |
| `welcomeMessage` | string | ❌ | "Hello! How can I help you today?" | Initial greeting |
| `apiUrl` | string | ❌ | Auto-detected | API endpoint URL |

### Available Positions

- `bottom-right` (default)
- `bottom-left`
- `top-right`
- `top-left`

## API Endpoints

### Authentication

All API endpoints require authentication using an API key in the `Authorization` header:

```
Authorization: Bearer your-api-key
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Demo page |
| `GET` | `/health` | Health check |
| `GET` | `/widget.js` | Widget JavaScript file |
| `POST` | `/ask` | Ask a question |
| `POST` | `/upload` | Upload text content |
| `POST` | `/upload-pdf` | Upload PDF file |
| `DELETE` | `/documents/{client_id}/{doc_id}` | Delete document |
| `GET` | `/stats/{client_id}` | Get client statistics |

### Example API Usage

```bash
# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"client_id": "your-client-id", "query": "What services do you offer?"}'

# Upload a PDF
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "Authorization: Bearer your-api-key" \
  -F "client_id=your-client-id" \
  -F "doc_id=document-1" \
  -F "file=@document.pdf"
```

## Widget Features

### User Interface
- **Floating chat button**: Always visible, non-intrusive
- **Expandable chat window**: Opens/closes smoothly
- **Message bubbles**: Clear distinction between user and bot messages
- **Typing indicators**: Shows when bot is processing
- **File upload**: Drag & drop or click to upload
- **Minimize/close**: User-friendly controls

### File Support
- **PDF files**: Automatic text extraction
- **Text files**: Direct processing
- **Word documents**: DOC and DOCX support
- **Size limit**: 10MB maximum
- **Drag & drop**: Intuitive file upload

### Customization
- **Colors**: Customizable primary color
- **Position**: 4 corner positions available
- **Text**: Customizable titles and messages
- **Styling**: Responsive design that adapts to any website

## Development

### Project Structure

```
ChatBotPlugin/
├── main.py              # FastAPI application
├── rag.py               # RAG system implementation
├── pdf_util.py          # PDF processing utilities
├── requirements.txt     # Python dependencies
├── static/              # Static files
│   ├── widget.js        # JavaScript widget
│   └── demo.html        # Demo page
├── chroma/              # ChromaDB storage
├── tmp/                 # Temporary files
└── README.md           # This file
```

### Key Technologies

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: Sentence Transformers, ChromaDB
- **LLM**: Ollama (Mistral model)
- **Frontend**: Vanilla JavaScript (no dependencies)
- **File Processing**: PyPDF2
- **Vector Database**: ChromaDB

### Performance Optimizations

- **Batch processing**: Multiple embeddings at once
- **Async operations**: Non-blocking API calls
- **Caching**: Model and embedding caching
- **Connection pooling**: Efficient HTTP connections
- **Optimized chunking**: Sentence-based text splitting

## Deployment

### Production Setup

1. **Environment Variables**:
   ```bash
   export API_KEYS="client1:key1,client2:key2"
   export OLLAMA_URL="http://your-ollama-server:11434"
   ```

2. **Database**: Use PostgreSQL or MongoDB for API key storage

3. **File Storage**: Use cloud storage (AWS S3, Google Cloud) for documents

4. **CDN**: Serve widget.js from a CDN for better performance

5. **SSL**: Use HTTPS in production

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security

- **API Key Authentication**: All requests require valid API keys
- **Client Isolation**: Each client has isolated document storage
- **Input Validation**: Comprehensive validation for all inputs
- **File Validation**: Type and size restrictions on uploads
- **CORS Configuration**: Configurable cross-origin requests

## Support

For support and questions:
- Check the demo page: `http://localhost:8000`
- Review the API documentation: `http://localhost:8000/docs`
- Test the health endpoint: `http://localhost:8000/health`

## License

This project is licensed under the MIT License.
