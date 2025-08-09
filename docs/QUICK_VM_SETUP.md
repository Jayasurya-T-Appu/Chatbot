# Quick VM Setup Guide

Since you've already created a GCP project, follow these steps to create your VM:

## 🎯 Quick Start

### Step 1: Update Project ID

1. **Edit the script** to use your project ID:
   ```bash
   # Open the script
   nano scripts/create_vm_only.sh
   
   # Find this line and replace with your actual project ID:
   PROJECT_ID="your-project-id"  # Replace with your actual project ID
   ```

2. **Or run this command** to find your project ID:
   ```bash
   gcloud projects list
   ```

### Step 2: Run VM Creation Script

```bash
# Make script executable
chmod +x scripts/create_vm_only.sh

# Run the script
./scripts/create_vm_only.sh
```

### Step 3: Follow the Prompts

The script will:
- ✅ Set your project as default
- ✅ Enable required APIs
- ✅ Create VM instance (e2-standard-4, Ubuntu 20.04)
- ✅ Install Ollama and Mistral model
- ✅ Configure firewall rules
- ✅ Display next steps

## 🚀 Alternative: Manual VM Creation

If you prefer to create the VM manually:

### 1. Set Project
```bash
# Replace with your actual project ID
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable APIs
```bash
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Create VM
```bash
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

### 4. Configure Firewall
```bash
# HTTP
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# HTTPS
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server

# Application port
gcloud compute firewall-rules create allow-chatbot \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

## 🔗 Next Steps After VM Creation

### 1. SSH to VM
```bash
gcloud compute ssh chatbot-vm --zone=us-central1-a
```

### 2. Clone Repository
```bash
cd /opt/chatbot
git clone https://github.com/Jayasurya-T-Appu/Chatbot.git .
```

### 3. Setup Application
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env
```

### 4. Configure Environment Variables
```env
# Production .env configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
ADMIN_API_KEY=your-secure-production-admin-key-here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
CHROMA_DB_PATH=/opt/chatbot/data/chroma
DATA_DIR=/opt/chatbot/data
TEMP_DIR=/opt/chatbot/tmp
STATIC_DIR=/opt/chatbot/static
CORS_ORIGINS=*
```

### 5. Create Systemd Service
```bash
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

### 6. Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl enable chatbot
sudo systemctl start ollama
sudo systemctl start chatbot
```

### 7. Test Application
```bash
# Check status
sudo systemctl status ollama
sudo systemctl status chatbot

# Test health
curl http://localhost:8000/health
curl http://localhost:11434/api/tags
```

## 🌐 Access Your Application

Once everything is set up:

- **Main App**: `http://YOUR_VM_IP:8000`
- **Admin Dashboard**: `http://YOUR_VM_IP:8000/admin`
- **Demo Page**: `http://YOUR_VM_IP:8000/static/html/demo.html`

## 🎯 Quick Commands

```bash
# Get VM IP
gcloud compute instances describe chatbot-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"

# SSH to VM
gcloud compute ssh chatbot-vm --zone=us-central1-a

# View logs
sudo journalctl -u chatbot -f
sudo journalctl -u ollama -f

# Restart services
sudo systemctl restart chatbot
sudo systemctl restart ollama
```

## 🚨 Troubleshooting

### Common Issues:

1. **Permission denied**: `sudo chown -R ubuntu:ubuntu /opt/chatbot`
2. **Port already in use**: `sudo lsof -i :8000`
3. **Ollama not starting**: `sudo systemctl status ollama`
4. **Memory issues**: `free -h`

### Useful Commands:
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python
ps aux | grep ollama

# View recent logs
sudo journalctl -u chatbot --since "5 minutes ago"
```

---

**🎉 Your ChatBot Plugin VM is now ready!**
