# AWS Deployment Guide for ChatBot SaaS

This guide covers deploying your ChatBot SaaS platform on various AWS services using the `setup.py` configuration.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [EC2 Deployment](#ec2-deployment)
3. [AWS Lambda Deployment](#aws-lambda-deployment)
4. [ECS/Fargate Deployment](#ecsfargate-deployment)
5. [Elastic Beanstalk Deployment](#elastic-beanstalk-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring and Scaling](#monitoring-and-scaling)

## Prerequisites

### 1. AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.8+ installed

### 2. Local Setup
```bash
# Clone your repository
git clone <your-repo-url>
cd ChatBotPlugin

# Install dependencies
pip install -e .

# Test locally
python main.py
```

## EC2 Deployment

### Option 1: Manual EC2 Setup

1. **Launch EC2 Instance**
```bash
# Launch Ubuntu 20.04 LTS instance
# Instance type: t3.medium or larger
# Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (App)
```

2. **Install Dependencies**
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies for ChromaDB
sudo apt install build-essential -y
```

3. **Deploy Application**
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
# Edit .env with your production settings
```

4. **Setup Systemd Service**
```bash
# Create service file
sudo nano /etc/systemd/system/chatbot-saas.service
```

```ini
[Unit]
Description=ChatBot SaaS Application
After=network.target

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

5. **Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbot-saas
sudo systemctl start chatbot-saas
sudo systemctl status chatbot-saas
```

### Option 2: Using setup.py with EC2

```bash
# On EC2 instance
pip install -e .

# Run using entry point
chatbot-saas
```

## AWS Lambda Deployment

### 1. Create Lambda Function

```python
# lambda_function.py
import os
import sys
from pathlib import Path

# Add your package to Python path
package_path = Path(__file__).parent / "package"
sys.path.insert(0, str(package_path))

from main import app
from mangum import Mangum

# Create handler for Lambda
handler = Mangum(app)
```

### 2. Package for Lambda

```bash
# Create deployment package
mkdir lambda-package
cd lambda-package

# Install your package
pip install -e .. -t .

# Install Lambda dependencies
pip install mangum -t .

# Copy your application
cp -r ../src .
cp ../main.py .
cp ../lambda_function.py .

# Create ZIP file
zip -r chatbot-saas-lambda.zip .
```

### 3. Deploy to Lambda

```bash
# Create Lambda function
aws lambda create-function \
    --function-name chatbot-saas \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
    --handler lambda_function.handler \
    --zip-file fileb://chatbot-saas-lambda.zip \
    --timeout 30 \
    --memory-size 1024

# Update function
aws lambda update-function-code \
    --function-name chatbot-saas \
    --zip-file fileb://chatbot-saas-lambda.zip
```

## ECS/Fargate Deployment

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy setup files
COPY setup.py requirements.txt ./

# Install your package
RUN pip install -e .

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data tmp static

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

### 2. Build and Push Docker Image

```bash
# Build image
docker build -t chatbot-saas .

# Tag for ECR
docker tag chatbot-saas:latest YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com/chatbot-saas:latest

# Push to ECR
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker push YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com/chatbot-saas:latest
```

### 3. Create ECS Task Definition

```json
{
  "family": "chatbot-saas",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
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
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/chatbot-saas",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Elastic Beanstalk Deployment

### 1. Create Application

```bash
# Initialize EB application
eb init chatbot-saas --platform python-3.9 --region us-east-1

# Create environment
eb create chatbot-saas-prod --instance-type t3.medium
```

### 2. Configure Environment

Create `.ebextensions/01_packages.config`:
```yaml
packages:
  yum:
    gcc: []
    gcc-c++: []
```

Create `.ebextensions/02_environment.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    HOST: 0.0.0.0
    PORT: 8000
    DEBUG: false
    LOG_LEVEL: INFO
```

### 3. Deploy

```bash
# Deploy to Elastic Beanstalk
eb deploy
```

## Docker Deployment

### 1. Local Docker

```bash
# Build image
docker build -t chatbot-saas .

# Run container
docker run -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e ADMIN_API_KEY=your-admin-key \
  chatbot-saas
```

### 2. Docker Compose

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
    volumes:
      - ./data:/app/data
      - ./tmp:/app/tmp
    restart: unless-stopped
```

## Environment Configuration

### Production Environment Variables

```bash
# .env.production
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
ADMIN_API_KEY=your-secure-admin-key
CHROMA_DB_PATH=/app/data/chroma
DATA_DIR=/app/data
TEMP_DIR=/app/tmp
STATIC_DIR=/app/static
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### AWS Parameter Store Integration

```python
# In your settings.py, add AWS Parameter Store support
import boto3

def get_parameter(parameter_name):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']

# Use in settings
ADMIN_API_KEY = get_parameter('/chatbot-saas/admin-api-key')
```

## Monitoring and Scaling

### 1. CloudWatch Monitoring

```python
# Add CloudWatch logging
import boto3
import logging
from botocore.exceptions import ClientError

class CloudWatchHandler(logging.Handler):
    def __init__(self, log_group, log_stream):
        super().__init__()
        self.client = boto3.client('logs')
        self.log_group = log_group
        self.log_stream = log_stream
        
    def emit(self, record):
        try:
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': int(record.created * 1000),
                    'message': self.format(record)
                }]
            )
        except ClientError:
            pass
```

### 2. Auto Scaling

```yaml
# .ebextensions/03_autoscaling.config
option_settings:
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 10
  aws:autoscaling:trigger:
    BreachDuration: 5
    LowerBreachScaleIncrement: -1
    UpperBreachScaleIncrement: 1
    LowerThreshold: 30
    UpperThreshold: 70
```

### 3. Health Checks

```python
# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check for load balancers"""
    try:
        # Check database connectivity
        # Check ChromaDB status
        # Check disk space
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "services": {
                "chromadb": "healthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

## Security Best Practices

### 1. IAM Roles and Policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 2. Security Groups

```bash
# EC2 Security Group
aws ec2 create-security-group \
    --group-name chatbot-saas-sg \
    --description "Security group for ChatBot SaaS"

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
    --group-name chatbot-saas-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name chatbot-saas-sg \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

## Cost Optimization

### 1. EC2 Spot Instances
```bash
# Use Spot instances for cost savings
aws ec2 run-instances \
    --instance-market-options MarketType=spot \
    --spot-options MaxPrice=0.05
```

### 2. Lambda Provisioned Concurrency
```bash
# For predictable workloads
aws lambda put-provisioned-concurrency-config \
    --function-name chatbot-saas \
    --qualifier PROD \
    --provisioned-concurrent-executions 10
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `setup.py` is properly configured
2. **Permission Issues**: Check IAM roles and security groups
3. **Memory Issues**: Increase Lambda memory or EC2 instance size
4. **Timeout Issues**: Adjust timeout settings for long-running operations

### Debug Commands

```bash
# Check application status
sudo systemctl status chatbot-saas

# View logs
sudo journalctl -u chatbot-saas -f

# Test API endpoints
curl -X GET http://localhost:8000/health

# Check disk space
df -h

# Monitor memory usage
free -h
```

This comprehensive guide should help you deploy your ChatBot SaaS platform on AWS using the `setup.py` configuration effectively!
