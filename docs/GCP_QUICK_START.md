# GCP VM Quick Start Guide

This guide will help you deploy your ChatBot Plugin to GCP VM in under 30 minutes.

## Prerequisites

1. **Google Cloud Platform Account**
   - Sign up at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable billing for your account

2. **Google Cloud SDK**
   - Install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Or use Cloud Shell (recommended for beginners)

3. **Git Repository**
   - Your ChatBot Plugin code should be in a Git repository (GitHub, GitLab, etc.)

## Option 1: Using Cloud Shell (Recommended for Beginners)

### Step 1: Open Cloud Shell
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the Cloud Shell icon (terminal icon) in the top-right corner
3. Wait for Cloud Shell to initialize

### Step 2: Clone and Deploy
```bash
# Clone your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/ChatBotPlugin.git
cd ChatBotPlugin

# Make deployment script executable
chmod +x scripts/deploy_gcp.sh

# Run deployment script
./scripts/deploy_gcp.sh
```

### Step 3: Follow the Prompts
The script will:
- Create a new GCP project
- Enable required APIs
- Create a VM instance with Ubuntu 20.04
- Install Ollama and pull Mistral model
- Configure firewall rules
- Display next steps

## Option 2: Manual Deployment

### Step 1: Create Project
```bash
# Create new project
gcloud projects create chatbot-plugin-123 --name="ChatBot Plugin"

# Set as default project
gcloud config set project chatbot-plugin-123
```

### Step 2: Enable APIs
```bash
# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Create VM
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
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl wget build-essential
    mkdir -p /opt/chatbot
    chown -R ubuntu:ubuntu /opt/chatbot
    curl -fsSL https://ollama.ai/install.sh | sh
    systemctl enable ollama
    systemctl start ollama
    ollama pull mistral'
```

### Step 4: Configure Firewall
```bash
# Create firewall rules
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server

gcloud compute firewall-rules create allow-chatbot \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

## Step 4: Connect and Setup Application

### Get VM IP
```bash
# Get external IP
gcloud compute instances describe chatbot-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```

### SSH to VM
```bash
# SSH to VM
gcloud compute ssh chatbot-vm --zone=us-central1-a
```

### Setup Application
```bash
# Navigate to application directory
cd /opt/chatbot

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/ChatBotPlugin.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
nano .env
```

### Configure Environment Variables
Edit the `.env` file with these production settings:
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

## Step 5: Create Systemd Service

### Create Service File
```bash
# Create systemd service file
sudo nano /etc/systemd/system/chatbot.service
```

Add this content:
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

### Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable ollama
sudo systemctl enable chatbot
sudo systemctl start ollama
sudo systemctl start chatbot

# Check status
sudo systemctl status ollama
sudo systemctl status chatbot
```

## Step 6: Test Your Deployment

### Health Checks
```bash
# Test application health
curl http://localhost:8000/health

# Test Ollama
curl http://localhost:11434/api/tags

# Test external access (replace with your VM IP)
curl http://YOUR_VM_IP:8000/health
```

### Access Your Application
- **Main App**: `http://YOUR_VM_IP:8000`
- **Admin Dashboard**: `http://YOUR_VM_IP:8000/admin`
- **Demo Page**: `http://YOUR_VM_IP:8000/static/html/demo.html`

## Step 7: Optional - Setup Nginx and SSL

### Install Nginx
```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/chatbot
```

Add this configuration:
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

### Enable Nginx Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL (Optional)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission issues**
   ```bash
   sudo chown -R ubuntu:ubuntu /opt/chatbot
   sudo chmod -R 755 /opt/chatbot
   ```

3. **Ollama not starting**
   ```bash
   sudo systemctl status ollama
   sudo systemctl restart ollama
   ```

4. **Memory issues**
   ```bash
   free -h
   # If needed, increase swap
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### View Logs
```bash
# Application logs
sudo journalctl -u chatbot -f

# Ollama logs
sudo journalctl -u ollama -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Cost Optimization

### Stop/Start Instance
```bash
# Stop instance when not in use
gcloud compute instances stop chatbot-vm --zone=us-central1-a

# Start instance when needed
gcloud compute instances start chatbot-vm --zone=us-central1-a
```

### Use Preemptible Instances (for testing)
```bash
# Create preemptible instance for cost savings
gcloud compute instances create chatbot-vm-test \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --preemptible \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud
```

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
