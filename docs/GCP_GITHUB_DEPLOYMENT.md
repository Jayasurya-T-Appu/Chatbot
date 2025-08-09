# GCP Deployment Guide - From GitHub Repository

This guide will help you deploy your ChatBot Plugin from GitHub to Google Cloud Platform (GCP) in under 30 minutes.

## 🎯 Quick Start (Recommended)

### Option 1: Using Cloud Shell (Easiest)

1. **Open Cloud Shell**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click the Cloud Shell icon (terminal icon) in the top-right corner
   - Wait for Cloud Shell to initialize

2. **Clone and Deploy**
   ```bash
   # Clone your repository
   git clone https://github.com/Jayasurya-T-Appu/Chatbot.git
   cd Chatbot
   
   # Make deployment script executable
   chmod +x scripts/deploy_gcp_from_github.sh
   
   # Run deployment script
   ./scripts/deploy_gcp_from_github.sh
   ```

3. **Follow the Prompts**
   - The script will create a new GCP project
   - Enable required APIs
   - Create a VM instance with Ubuntu 20.04
   - Install Ollama and pull Mistral model
   - Configure firewall rules
   - Display next steps

### Option 2: Manual Deployment

## Prerequisites

1. **Google Cloud Platform Account**
   - Sign up at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable billing for your account

2. **Google Cloud SDK**
   - Install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Or use Cloud Shell (recommended for beginners)

3. **GitHub Repository**
   - Your repository: `https://github.com/Jayasurya-T-Appu/Chatbot.git`

## Step 1: Create GCP Project and Enable APIs

### 1.1 Create New Project
```bash
# Create new project (replace with your project name)
gcloud projects create chatbot-plugin-123 --name="ChatBot Plugin"

# Set the project as default
gcloud config set project chatbot-plugin-123
```

### 1.2 Enable Required APIs
```bash
# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Enable Cloud Build API (optional, for container builds)
gcloud services enable cloudbuild.googleapis.com
```

## Step 2: Create VM Instance

### 2.1 Create VM with Recommended Specs
```bash
# Create VM instance
gcloud compute instances create chatbot-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#! /bin/bash
    # Update system
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl wget
    
    # Install system dependencies
    apt-get install -y build-essential
    
    # Create application directory
    mkdir -p /opt/chatbot
    chown -R ubuntu:ubuntu /opt/chatbot
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    systemctl enable ollama
    systemctl start ollama
    
    # Pull Mistral model
    ollama pull mistral'
```

### 2.2 Configure Firewall Rules
```bash
# Create firewall rule for HTTP
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# Create firewall rule for HTTPS
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server

# Create firewall rule for application port
gcloud compute firewall-rules create allow-chatbot \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

## Step 3: Connect to VM and Setup Application

### 3.1 Connect to VM
```bash
# Get external IP
gcloud compute instances describe chatbot-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"

# SSH to VM
gcloud compute ssh chatbot-vm --zone=us-central1-a
```

### 3.2 Clone and Setup Application
```bash
# Navigate to application directory
cd /opt/chatbot

# Clone your repository
git clone https://github.com/Jayasurya-T-Appu/Chatbot.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3.3 Configure Environment
```bash
# Copy environment file
cp env.example .env

# Edit environment file
nano .env
```

**Production .env configuration:**
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Admin Configuration
ADMIN_API_KEY=your-secure-production-admin-key-here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=30
OLLAMA_MAX_TOKENS=2048
OLLAMA_TEMPERATURE=0.7

# Database Configuration
CHROMA_DB_PATH=/opt/chatbot/data/chroma
DATA_DIR=/opt/chatbot/data
TEMP_DIR=/opt/chatbot/tmp
STATIC_DIR=/opt/chatbot/static

# CORS Configuration
CORS_ORIGINS=*

# Security
API_KEY_PREFIX=cb_
CLIENT_ID_PREFIX=client_
```

## Step 4: Setup Systemd Service

### 4.1 Create Service File
```bash
# Create systemd service file
sudo nano /etc/systemd/system/chatbot.service
```

**Service file content:**
```ini
[Unit]
Description=ChatBot Plugin Application
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/chatbot
Environment=PATH=/opt/chatbot/venv/bin
ExecStart=/opt/chatbot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2 Enable and Start Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable ollama
sudo systemctl enable chatbot

# Start services
sudo systemctl start ollama
sudo systemctl start chatbot

# Check status
sudo systemctl status ollama
sudo systemctl status chatbot
```

## Step 5: Test Your Deployment

### 5.1 Health Checks
```bash
# Test application health
curl http://localhost:8000/health

# Test Ollama
curl http://localhost:11434/api/tags

# Test external access (replace with your VM IP)
curl http://YOUR_VM_IP:8000/health
```

### 5.2 Access Your Application
- **Main App**: `http://YOUR_VM_IP:8000`
- **Admin Dashboard**: `http://YOUR_VM_IP:8000/admin`
- **Demo Page**: `http://YOUR_VM_IP:8000/static/html/demo.html`

## Step 6: Optional - Setup Nginx and SSL

### 6.1 Install and Configure Nginx
```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/chatbot
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 6.2 Enable Nginx Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 6.3 Setup SSL (Optional)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

## Step 7: Monitoring and Logs

### 7.1 View Application Logs
```bash
# View application logs
sudo journalctl -u chatbot -f

# View Ollama logs
sudo journalctl -u ollama -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 7.2 Health Checks
```bash
# Test application health
curl http://localhost:8000/health

# Test Ollama
curl http://localhost:11434/api/tags

# Test external access (replace with your IP)
curl http://YOUR_VM_IP:8000/health
```

## Step 8: Backup and Maintenance

### 8.1 Create Backup Script
```bash
# Create backup directory
mkdir -p /opt/backups

# Create backup script
nano /opt/backups/backup.sh
```

**Backup script content:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
APP_DIR="/opt/chatbot"

# Create backup
tar -czf $BACKUP_DIR/chatbot_backup_$DATE.tar.gz \
    -C $APP_DIR data \
    -C $APP_DIR .env

# Keep only last 7 backups
find $BACKUP_DIR -name "chatbot_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: chatbot_backup_$DATE.tar.gz"
```

### 8.2 Setup Automated Backups
```bash
# Make script executable
chmod +x /opt/backups/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add this line:
# 0 2 * * * /opt/backups/backup.sh
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   sudo lsof -i :8000
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

2. **Permission issues**
   ```bash
   # Fix directory permissions
   sudo chown -R ubuntu:ubuntu /opt/chatbot
   sudo chmod -R 755 /opt/chatbot
   ```

3. **Ollama not starting**
   ```bash
   # Check Ollama status
   sudo systemctl status ollama
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap if needed
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## Cost Optimization

### 1. Use Preemptible Instances (for testing)
```bash
# Create preemptible instance for cost savings
gcloud compute instances create chatbot-vm-test \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --preemptible \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud
```

### 2. Stop/Start Instances
```bash
# Stop instance when not in use
gcloud compute instances stop chatbot-vm --zone=us-central1-a

# Start instance when needed
gcloud compute instances start chatbot-vm --zone=us-central1-a
```

## Security Best Practices

1. **Change default admin key** - Always change the `ADMIN_API_KEY` in production
2. **Use HTTPS** - Always use SSL/TLS in production
3. **Restrict firewall** - Only allow necessary ports
4. **Regular updates** - Keep system and dependencies updated
5. **Backup regularly** - Set up automated backups
6. **Monitor logs** - Regularly check application and system logs

## Next Steps

1. **Domain Setup** - Configure your domain to point to the VM
2. **Monitoring** - Set up Cloud Monitoring for better observability
3. **Load Balancer** - Add load balancer for high availability
4. **Auto-scaling** - Configure auto-scaling for traffic spikes
5. **CDN** - Add CDN for static assets

## Support

- **Documentation**: See `docs/GCP_DEPLOYMENT.md` for detailed instructions
- **Issues**: Check the troubleshooting section above
- **Logs**: Use `sudo journalctl -u chatbot -f` to view application logs

Your ChatBot Plugin is now deployed and running on GCP! 🎉
