# Docker Deployment Guide

This guide covers deploying your ChatBot SaaS platform using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- At least 8GB of available RAM (for Ollama)
- At least 10GB of available disk space

## Quick Start

### 1. Clone and Setup

```bash
# Clone your repository
git clone <your-repo-url>
cd ChatBotPlugin

# Create necessary directories
mkdir -p data tmp static
```

### 2. Set Environment Variables (Optional)

```bash
# Create .env file for custom configuration
cp env.example .env

# Edit .env file with your settings
nano .env
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Pull Ollama Model (First Time Only)

```bash
# Pull the Mistral model
docker-compose exec ollama ollama pull mistral

# Verify model is available
docker-compose exec ollama ollama list
```

### 5. Access Your Application

- **Main App**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **Demo Page**: http://localhost:8000/static/html/demo.html
- **Ollama API**: http://localhost:11434

## Docker Commands Reference

### Basic Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f chatbot-saas
docker-compose logs -f ollama

# Check status
docker-compose ps

# Access container shell
docker-compose exec chatbot-saas bash
docker-compose exec ollama bash
```

### Development Commands

```bash
# Rebuild after code changes
docker-compose build chatbot-saas
docker-compose up -d chatbot-saas

# View real-time logs
docker-compose logs -f --tail=100

# Check resource usage
docker stats
```

### Ollama Management

```bash
# Pull different models
docker-compose exec ollama ollama pull llama2:7b
docker-compose exec ollama ollama pull codellama:7b

# List available models
docker-compose exec ollama ollama list

# Remove unused models
docker-compose exec ollama ollama rm unused-model

# Test Ollama directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral", "prompt": "Hello, world!"}'
```

## Configuration Options

### Environment Variables

You can customize the deployment by setting environment variables:

```bash
# In your .env file or environment
export ADMIN_API_KEY=your-secure-admin-key
export OLLAMA_MODEL=mistral
export DEBUG=false
export LOG_LEVEL=INFO
```

### Docker Compose Override

Create `docker-compose.override.yml` for development:

```yaml
version: '3.8'

services:
  chatbot-saas:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app  # Mount source code for development
```

## Production Deployment

### 1. Production Configuration

```bash
# Create production .env
cp env.example .env.production

# Edit production settings
nano .env.production
```

```bash
# Production .env example
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
ADMIN_API_KEY=your-secure-production-key
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=mistral
CORS_ORIGINS=https://yourdomain.com
```

### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  chatbot-saas:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
      - ./tmp:/app/tmp
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        limits:
          memory: 6G
          cpus: '2.0'

volumes:
  ollama_data:
```

### 3. Deploy to Production

```bash
# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d

# Check production logs
docker-compose -f docker-compose.prod.yml logs -f
```

## AWS ECS Deployment

### 1. Build and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR-ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t chatbot-saas .

# Tag for ECR
docker tag chatbot-saas:latest YOUR-ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-saas:latest

# Push to ECR
docker push YOUR-ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-saas:latest
```

### 2. ECS Task Definition

```json
{
  "family": "chatbot-saas",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "4096",
  "memory": "8192",
  "executionRoleArn": "arn:aws:iam::YOUR-ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "chatbot-saas",
      "image": "YOUR-ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-saas:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "HOST",
          "value": "0.0.0.0"
        },
        {
          "name": "PORT",
          "value": "8000"
        },
        {
          "name": "OLLAMA_BASE_URL",
          "value": "http://localhost:11434"
        }
      ],
      "dependsOn": [
        {
          "containerName": "ollama",
          "condition": "START"
        }
      ]
    },
    {
      "name": "ollama",
      "image": "ollama/ollama:latest",
      "portMappings": [
        {
          "containerPort": 11434,
          "protocol": "tcp"
        }
      ],
      "essential": true
    }
  ]
}
```

## Monitoring and Troubleshooting

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check Ollama health
curl http://localhost:11434/api/tags

# Check container health
docker-compose ps
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs chatbot-saas
docker-compose logs ollama

# Follow logs in real-time
docker-compose logs -f

# Check container resource usage
docker stats
```

### Common Issues

#### 1. Out of Memory
```bash
# Check available memory
free -h

# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory
```

#### 2. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tlnp | grep 8000
sudo netstat -tlnp | grep 11434

# Stop conflicting services
sudo systemctl stop conflicting-service
```

#### 3. Model Not Loading
```bash
# Check Ollama logs
docker-compose logs ollama

# Pull model manually
docker-compose exec ollama ollama pull mistral

# Check available disk space
df -h
```

### Performance Optimization

#### 1. Resource Limits

```yaml
# In docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        reservations:
          memory: 4G
        limits:
          memory: 8G
          cpus: '2.0'
```

#### 2. Volume Optimization

```yaml
# Use named volumes for better performance
volumes:
  - ollama_data:/root/.ollama
  - chroma_data:/app/data/chroma
```

#### 3. Network Optimization

```yaml
# Use host network for better performance (Linux only)
network_mode: host
```

## Backup and Recovery

### Backup Data

```bash
# Backup ChromaDB data
docker-compose exec chatbot-saas tar -czf /app/data-backup.tar.gz /app/data

# Backup Ollama models
docker-compose exec ollama tar -czf /root/ollama-backup.tar.gz /root/.ollama

# Copy backups to host
docker cp chatbot-saas:/app/data-backup.tar.gz ./data-backup.tar.gz
docker cp ollama:/root/ollama-backup.tar.gz ./ollama-backup.tar.gz
```

### Restore Data

```bash
# Restore ChromaDB data
docker cp ./data-backup.tar.gz chatbot-saas:/app/
docker-compose exec chatbot-saas tar -xzf /app/data-backup.tar.gz -C /app/

# Restore Ollama models
docker cp ./ollama-backup.tar.gz ollama:/root/
docker-compose exec ollama tar -xzf /root/ollama-backup.tar.gz -C /root/
```

## Security Considerations

### 1. Environment Variables

```bash
# Use secrets for sensitive data
echo "your-secure-admin-key" | docker secret create admin_api_key -
```

### 2. Network Security

```yaml
# Restrict network access
networks:
  chatbot-network:
    driver: bridge
    internal: true  # No external access
```

### 3. Resource Limits

```yaml
# Prevent resource exhaustion
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '2.0'
```

This comprehensive guide should help you deploy your ChatBot SaaS platform successfully using Docker!
