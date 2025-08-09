# Ollama Deployment on AWS Guide

This guide covers deploying Ollama alongside your ChatBot SaaS platform on various AWS services.

## Table of Contents
1. [Overview](#overview)
2. [EC2 Deployment](#ec2-deployment)
3. [Docker Deployment](#docker-deployment)
4. [ECS/Fargate Deployment](#ecsfargate-deployment)
5. [Performance Considerations](#performance-considerations)
6. [Model Management](#model-management)
7. [Monitoring and Scaling](#monitoring-and-scaling)
8. [Cost Optimization](#cost-optimization)

## Overview

Ollama is required for your RAG chatbot to generate responses. It runs as a separate service that your FastAPI application communicates with via HTTP.

### Architecture Options:

1. **Single EC2 Instance**: Both app and Ollama on same server
2. **Separate Containers**: App and Ollama in different containers
3. **Microservices**: App and Ollama on separate instances

## EC2 Deployment

### Option 1: Single EC2 Instance (Recommended for Small Scale)

#### 1. Launch EC2 Instance
```bash
# Recommended instance types for Ollama:
# - t3.large (2 vCPU, 8GB RAM) - for testing
# - t3.xlarge (4 vCPU, 16GB RAM) - for production
# - c5.xlarge (4 vCPU, 8GB RAM) - for better CPU performance
```

#### 2. Install Ollama
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify installation
ollama --version
```

#### 3. Pull and Configure Model
```bash
# Pull Mistral model (recommended for RAG)
ollama pull mistral

# For better performance, consider:
# ollama pull llama2:7b
# ollama pull codellama:7b
# ollama pull mistral:7b-instruct

# Test the model
ollama run mistral "What is 2+2?"
```

#### 4. Deploy Your Application
```bash
# Clone your repository
git clone <your-repo-url>
cd ChatBotPlugin

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install your package
pip install -e .

# Create .env file
cp env.example .env
```

#### 5. Configure Environment Variables
```bash
# Edit .env file
nano .env
```

```bash
# Production .env configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
ADMIN_API_KEY=your-secure-admin-key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=30
OLLAMA_MAX_TOKENS=2048
OLLAMA_TEMPERATURE=0.7

# Other configurations...
```

#### 6. Setup Systemd Services
```bash
# Create service file for your app
sudo nano /etc/systemd/system/chatbot-saas.service
```

```ini
[Unit]
Description=ChatBot SaaS Application
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ChatBotPlugin
Environment=PATH=/home/ubuntu/ChatBotPlugin/venv/bin
ExecStart=/home/ubuntu/ChatBotPlugin/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7. Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl enable chatbot-saas
sudo systemctl start ollama
sudo systemctl start chatbot-saas

# Check status
sudo systemctl status ollama
sudo systemctl status chatbot-saas
```

### Option 2: Separate EC2 Instances (Recommended for Production)

#### 1. Launch Two EC2 Instances
- **App Instance**: t3.medium (for FastAPI app)
- **Ollama Instance**: t3.xlarge or c5.xlarge (for Ollama)

#### 2. Configure Security Groups
```bash
# App Instance Security Group
aws ec2 create-security-group \
    --group-name chatbot-app-sg \
    --description "Security group for ChatBot app"

# Allow HTTP/HTTPS to app
aws ec2 authorize-security-group-ingress \
    --group-name chatbot-app-sg \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0

# Ollama Instance Security Group
aws ec2 create-security-group \
    --group-name ollama-sg \
    --description "Security group for Ollama"

# Allow app to connect to Ollama
aws ec2 authorize-security-group-ingress \
    --group-name ollama-sg \
    --protocol tcp \
    --port 11434 \
    --source-group chatbot-app-sg
```

#### 3. Deploy Ollama on Ollama Instance
```bash
# On Ollama instance
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
ollama pull mistral
```

#### 4. Deploy App on App Instance
```bash
# On App instance
# Set OLLAMA_BASE_URL to Ollama instance private IP
OLLAMA_BASE_URL=http://10.0.1.100:11434  # Replace with actual private IP
```

## Docker Deployment

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  chatbot-saas:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - ADMIN_API_KEY=${ADMIN_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./data:/app/data
      - ./tmp:/app/tmp
    depends_on:
      - ollama
    restart: unless-stopped
    networks:
      - chatbot-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    networks:
      - chatbot-network
    deploy:
      resources:
        reservations:
          memory: 4G
        limits:
          memory: 8G

networks:
  chatbot-network:
    driver: bridge

volumes:
  ollama_data:
```

### Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# Pull model (first time only)
docker-compose exec ollama ollama pull mistral

# Check logs
docker-compose logs -f chatbot-saas
docker-compose logs -f ollama
```

## ECS/Fargate Deployment

### Task Definition with Two Containers

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
      "image": "YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com/chatbot-saas:latest",
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
        },
        {
          "name": "OLLAMA_MODEL",
          "value": "mistral"
        }
      ],
      "dependsOn": [
        {
          "containerName": "ollama",
          "condition": "START"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/chatbot-saas",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "app"
        }
      }
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
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/chatbot-saas",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "ollama"
        }
      }
    }
  ]
}
```

## Performance Considerations

### 1. Instance Sizing

| Use Case | Instance Type | RAM | CPU | Cost/Month |
|----------|---------------|-----|-----|------------|
| Development | t3.medium | 4GB | 2 vCPU | ~$30 |
| Small Production | t3.large | 8GB | 2 vCPU | ~$60 |
| Medium Production | t3.xlarge | 16GB | 4 vCPU | ~$120 |
| High Performance | c5.xlarge | 8GB | 4 vCPU | ~$150 |

### 2. Model Selection

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| mistral:7b | 4GB | 8GB | Fast | Good |
| llama2:7b | 4GB | 8GB | Fast | Good |
| codellama:7b | 4GB | 8GB | Fast | Excellent for code |
| mistral:13b | 8GB | 16GB | Medium | Better |
| llama2:13b | 8GB | 16GB | Medium | Better |

### 3. Memory Optimization

```bash
# For better performance, set environment variables
export OLLAMA_HOST=0.0.0.0
export OLLAMA_ORIGINS=*

# Use GPU if available (requires NVIDIA drivers)
export OLLAMA_GPU_LAYERS=35
```

## Model Management

### 1. Pre-load Models on Startup

```bash
# Create startup script
nano /home/ubuntu/startup.sh
```

```bash
#!/bin/bash
# Startup script for EC2
systemctl start ollama
sleep 10
ollama pull mistral
systemctl start chatbot-saas
```

### 2. Model Switching

```bash
# Switch models dynamically
ollama pull llama2:7b
ollama pull codellama:7b

# List available models
ollama list

# Remove unused models
ollama rm unused-model
```

### 3. Model Persistence

```bash
# Backup models
tar -czf ollama-models-backup.tar.gz ~/.ollama

# Restore models
tar -xzf ollama-models-backup.tar.gz -C ~/
```

## Monitoring and Scaling

### 1. Health Checks

```python
# Add to your FastAPI app
@app.get("/health/ollama")
async def ollama_health_check():
    """Check Ollama service health"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.OLLAMA_BASE_URL}/api/tags") as response:
                if response.status == 200:
                    return {"status": "healthy", "service": "ollama"}
                else:
                    raise HTTPException(status_code=503, detail="Ollama unhealthy")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {str(e)}")
```

### 2. Auto Scaling

```yaml
# .ebextensions/ollama-autoscaling.config
option_settings:
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 5
  aws:autoscaling:trigger:
    BreachDuration: 5
    LowerBreachScaleIncrement: -1
    UpperBreachScaleIncrement: 1
    LowerThreshold: 20
    UpperThreshold: 80
```

### 3. CloudWatch Monitoring

```python
# Monitor Ollama performance
import boto3
import time

def log_ollama_metrics(response_time, model_used):
    cloudwatch = boto3.client('cloudwatch')
    cloudwatch.put_metric_data(
        Namespace='ChatBot/Ollama',
        MetricData=[
            {
                'MetricName': 'ResponseTime',
                'Value': response_time,
                'Unit': 'Milliseconds'
            },
            {
                'MetricName': 'ModelUsage',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {
                        'Name': 'Model',
                        'Value': model_used
                    }
                ]
            }
        ]
    )
```

## Cost Optimization

### 1. Spot Instances for Development

```bash
# Use Spot instances for cost savings
aws ec2 run-instances \
    --instance-market-options MarketType=spot \
    --spot-options MaxPrice=0.05 \
    --instance-type t3.large
```

### 2. Reserved Instances for Production

```bash
# Purchase reserved instances for predictable workloads
aws ec2 describe-reserved-instances-offerings \
    --instance-type t3.xlarge \
    --offering-type All Upfront
```

### 3. Model Optimization

```bash
# Use quantized models for better performance
ollama pull mistral:7b-q4_K_M  # Quantized version
ollama pull llama2:7b-q4_K_M   # Quantized version
```

## Troubleshooting

### Common Issues

1. **Ollama not starting**:
```bash
# Check logs
sudo journalctl -u ollama -f

# Check if port is in use
sudo netstat -tlnp | grep 11434
```

2. **Model not loading**:
```bash
# Check available disk space
df -h

# Check model status
ollama list
ollama show mistral
```

3. **Slow responses**:
```bash
# Check memory usage
free -h

# Check CPU usage
top

# Consider upgrading instance or using quantized models
```

### Debug Commands

```bash
# Test Ollama directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral", "prompt": "Hello, world!"}'

# Check Ollama API
curl http://localhost:11434/api/tags

# Monitor system resources
htop
iotop
```

This comprehensive guide should help you deploy Ollama successfully on AWS with your ChatBot SaaS platform!
