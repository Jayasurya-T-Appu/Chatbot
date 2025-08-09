# Deployment Guide

This guide explains how to deploy the ChatBot SaaS application using environment variables for easy configuration.

## Prerequisites

- Python 3.8 or higher
- Ollama with Mistral model installed and running
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ChatBotPlugin
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit the .env file with your configuration
   nano .env  # or use your preferred editor
   ```

## Environment Variables Configuration

### Server Configuration
```env
HOST=0.0.0.0          # Server host (0.0.0.0 for all interfaces)
PORT=8000             # Server port
DEBUG=True            # Enable debug mode (set to False in production)
LOG_LEVEL=info        # Logging level (debug, info, warning, error)
```

### Admin Configuration
```env
ADMIN_API_KEY=your-secure-admin-key-here  # Change this in production!
```

### Database Configuration
```env
CHROMA_DB_PATH=./chroma    # ChromaDB storage path
DATA_DIR=./data           # Client data storage path
```

### File Storage
```env
TEMP_DIR=./tmp            # Temporary file storage
STATIC_DIR=./static       # Static files directory
```

### CORS Configuration
```env
ALLOWED_ORIGINS=*         # CORS origins (comma-separated for multiple)
```

### Client Management
```env
DEFAULT_PLAN=free         # Default plan for new clients
MAX_FILE_SIZE=10485760    # Maximum file size in bytes (10MB)
```

### RAG Configuration
```env
CHUNK_SIZE=1000           # Text chunk size for embeddings
CHUNK_OVERLAP=200         # Overlap between chunks
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Sentence transformer model
```

### Security
```env
API_KEY_PREFIX=cb_        # Prefix for generated API keys
CLIENT_ID_PREFIX=client_  # Prefix for generated client IDs
```

### Logging
```env
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Production Deployment

### 1. Environment Setup
```bash
# Create production .env file
cp env.example .env.prod

# Edit with production values
nano .env.prod
```

**Production .env example:**
```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=warning
ADMIN_API_KEY=your-very-secure-production-key
CHROMA_DB_PATH=/var/lib/chatbot/chroma
DATA_DIR=/var/lib/chatbot/data
TEMP_DIR=/var/lib/chatbot/tmp
STATIC_DIR=/var/lib/chatbot/static
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DEFAULT_PLAN=basic
MAX_FILE_SIZE=10485760
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_KEY_PREFIX=cb_
CLIENT_ID_PREFIX=client_
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 2. Systemd Service (Linux)
Create `/etc/systemd/system/chatbot.service`:
```ini
[Unit]
Description=ChatBot SaaS Application
After=network.target

[Service]
Type=simple
User=chatbot
WorkingDirectory=/opt/chatbot
Environment=PATH=/opt/chatbot/venv/bin
ExecStart=/opt/chatbot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Nginx Configuration
Create `/etc/nginx/sites-available/chatbot`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=False
      - ADMIN_API_KEY=${ADMIN_API_KEY}
    volumes:
      - ./data:/app/data
      - ./chroma:/app/chroma
    restart: unless-stopped
```

## Security Considerations

1. **Change default admin key** - Always change the `ADMIN_API_KEY` in production
2. **Use HTTPS** - Always use SSL/TLS in production
3. **Restrict CORS** - Set specific origins instead of `*`
4. **File permissions** - Ensure proper file permissions for data directories
5. **Firewall** - Configure firewall to only allow necessary ports
6. **Regular updates** - Keep dependencies updated

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# View application logs
tail -f /var/log/chatbot.log

# View systemd logs
journalctl -u chatbot -f
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Kill the process or change PORT in .env
   ```

2. **Permission denied**
   ```bash
   # Fix directory permissions
   sudo chown -R chatbot:chatbot /var/lib/chatbot
   sudo chmod -R 755 /var/lib/chatbot
   ```

3. **ChromaDB errors**
   ```bash
   # Clear ChromaDB data (will delete all embeddings)
   rm -rf ./chroma/*
   ```

4. **Memory issues**
   - Reduce `CHUNK_SIZE` in .env
   - Use smaller embedding model
   - Increase system memory

## Backup and Recovery

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backup/chatbot/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup data
cp -r ./data $BACKUP_DIR/
cp -r ./chroma $BACKUP_DIR/

# Backup configuration
cp .env $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

### Restore
```bash
# Stop the service
sudo systemctl stop chatbot

# Restore from backup
cp -r /backup/chatbot/20231201_120000/data ./
cp -r /backup/chatbot/20231201_120000/chroma ./
cp /backup/chatbot/20231201_120000/.env ./

# Start the service
sudo systemctl start chatbot
```
