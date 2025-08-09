# GCP Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Prerequisites
- [ ] Google Cloud Platform account created
- [ ] Billing enabled on GCP account
- [ ] Google Cloud SDK installed (or Cloud Shell ready)
- [ ] GitHub repository: `https://github.com/Jayasurya-T-Appu/Chatbot.git`
- [ ] SSH key pair (optional, but recommended)

### 2. GCP Setup
- [ ] Create new GCP project
- [ ] Enable Compute Engine API
- [ ] Enable Cloud Build API (optional)
- [ ] Set default project

### 3. VM Configuration
- [ ] Choose VM specs (e2-standard-4 recommended)
- [ ] Select Ubuntu 20.04 LTS image
- [ ] Configure 50GB boot disk
- [ ] Set up firewall rules (HTTP, HTTPS, port 8000)

## 🚀 Deployment Steps

### Step 1: Create VM Instance
```bash
# Option A: Using automated script (Recommended)
git clone https://github.com/Jayasurya-T-Appu/Chatbot.git
cd Chatbot
chmod +x scripts/deploy_gcp_from_github.sh
./scripts/deploy_gcp_from_github.sh

# Option B: Manual deployment
gcloud compute instances create chatbot-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server
```

### Step 2: Connect to VM
```bash
# Get VM IP
gcloud compute instances describe chatbot-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"

# SSH to VM
gcloud compute ssh chatbot-vm --zone=us-central1-a
```

### Step 3: Setup Application
```bash
# Navigate to application directory
cd /opt/chatbot

# Clone repository
git clone https://github.com/Jayasurya-T-Appu/Chatbot.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy environment file
cp env.example .env

# Edit environment file
nano .env
```

**Required environment variables:**
```env
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

### Step 5: Setup Services
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

### Step 6: Start Services
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

## ✅ Post-Deployment Checklist

### 1. Health Checks
- [ ] Test application health: `curl http://localhost:8000/health`
- [ ] Test Ollama: `curl http://localhost:11434/api/tags`
- [ ] Test external access: `curl http://YOUR_VM_IP:8000/health`

### 2. Application Access
- [ ] Main app: `http://YOUR_VM_IP:8000`
- [ ] Admin dashboard: `http://YOUR_VM_IP:8000/admin`
- [ ] Demo page: `http://YOUR_VM_IP:8000/static/html/demo.html`

### 3. Security
- [ ] Change default admin key
- [ ] Configure firewall rules
- [ ] Set up SSL certificate (optional)
- [ ] Configure Nginx (optional)

### 4. Monitoring
- [ ] Set up log monitoring
- [ ] Configure backup scripts
- [ ] Set up health checks
- [ ] Monitor resource usage

## 🔧 Optional Enhancements

### 1. Nginx Setup
```bash
# Install Nginx
sudo apt update && sudo apt install -y nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/chatbot

# Enable site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 2. SSL Certificate
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Backup Setup
```bash
# Create backup directory
mkdir -p /opt/backups

# Create backup script
nano /opt/backups/backup.sh

# Make executable
chmod +x /opt/backups/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/backups/backup.sh
```

## 🚨 Troubleshooting

### Common Issues
1. **Port already in use**: `sudo lsof -i :8000`
2. **Permission issues**: `sudo chown -R ubuntu:ubuntu /opt/chatbot`
3. **Ollama not starting**: `sudo systemctl status ollama`
4. **Memory issues**: Check with `free -h`

### Useful Commands
```bash
# View logs
sudo journalctl -u chatbot -f
sudo journalctl -u ollama -f

# Check status
sudo systemctl status chatbot
sudo systemctl status ollama

# Restart services
sudo systemctl restart chatbot
sudo systemctl restart ollama
```

## 💰 Cost Optimization

### 1. Stop/Start Instance
```bash
# Stop when not in use
gcloud compute instances stop chatbot-vm --zone=us-central1-a

# Start when needed
gcloud compute instances start chatbot-vm --zone=us-central1-a
```

### 2. Use Preemptible Instances (for testing)
```bash
gcloud compute instances create chatbot-vm-test \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --preemptible \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud
```

## 📞 Support

- **Documentation**: `docs/GCP_DEPLOYMENT.md`
- **GitHub Repository**: `https://github.com/Jayasurya-T-Appu/Chatbot.git`
- **Issues**: Check troubleshooting section above
- **Logs**: `sudo journalctl -u chatbot -f`

---

**🎉 Congratulations! Your ChatBot Plugin is now deployed and running on GCP!**
