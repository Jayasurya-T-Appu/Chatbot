#!/bin/bash

# GCP VM Creation Script (for existing project)
# This script creates a VM instance for your ChatBot Plugin

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="your-project-id"  # Replace with your actual project ID
ZONE="us-central1-a"
INSTANCE_NAME="chatbot-vm"
MACHINE_TYPE="e2-standard-4"
DISK_SIZE="50GB"
GITHUB_REPO="https://github.com/Jayasurya-T-Appu/Chatbot.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# Check if user is authenticated
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "You are not authenticated with gcloud. Please run:"
        echo "gcloud auth login"
        exit 1
    fi
}

# Set project
set_project() {
    print_status "Setting project to: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."
    gcloud services enable compute.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
}

# Create VM instance
create_vm() {
    print_status "Creating VM instance..."
    
    # Check if instance already exists
    if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &> /dev/null; then
        print_warning "Instance $INSTANCE_NAME already exists"
        read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Deleting existing instance..."
            gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE --quiet
        else
            print_status "Using existing instance"
            return
        fi
    fi
    
    # Create startup script
    cat > /tmp/startup-script.sh << 'EOF'
#!/bin/bash
# Update system
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl wget build-essential

# Create application directory
mkdir -p /opt/chatbot
chown -R ubuntu:ubuntu /opt/chatbot

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
systemctl enable ollama
systemctl start ollama

# Pull Mistral model
ollama pull mistral
EOF

    # Create VM
    gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=$DISK_SIZE \
        --boot-disk-type=pd-standard \
        --tags=http-server,https-server \
        --metadata-from-file=startup-script=/tmp/startup-script.sh

    # Clean up startup script
    rm -f /tmp/startup-script.sh
}

# Configure firewall rules
setup_firewall() {
    print_status "Setting up firewall rules..."
    
    # Create firewall rules if they don't exist
    if ! gcloud compute firewall-rules describe allow-http &> /dev/null; then
        gcloud compute firewall-rules create allow-http \
            --allow tcp:80 \
            --source-ranges 0.0.0.0/0 \
            --target-tags http-server
    fi
    
    if ! gcloud compute firewall-rules describe allow-https &> /dev/null; then
        gcloud compute firewall-rules create allow-https \
            --allow tcp:443 \
            --source-ranges 0.0.0.0/0 \
            --target-tags https-server
    fi
    
    if ! gcloud compute firewall-rules describe allow-chatbot &> /dev/null; then
        gcloud compute firewall-rules create allow-chatbot \
            --allow tcp:8000 \
            --source-ranges 0.0.0.0/0 \
            --target-tags http-server
    fi
}

# Get VM IP
get_vm_ip() {
    print_status "Getting VM IP address..."
    VM_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
    echo "VM IP: $VM_IP"
}

# Display next steps
show_next_steps() {
    print_status "VM creation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. SSH to your VM:"
    echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo
    echo "2. Clone your repository:"
    echo "   cd /opt/chatbot"
    echo "   git clone $GITHUB_REPO ."
    echo
    echo "3. Setup the application:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   cp env.example .env"
    echo "   nano .env  # Edit with your production settings"
    echo
    echo "4. Create systemd service:"
    echo "   sudo nano /etc/systemd/system/chatbot.service"
    echo "   sudo systemctl enable chatbot"
    echo "   sudo systemctl start chatbot"
    echo
    echo "5. Access your application:"
    echo "   http://$VM_IP:8000"
    echo
    echo "For detailed instructions, see: docs/GCP_DEPLOYMENT.md"
}

# Main execution
main() {
    print_status "Starting VM creation for ChatBot Plugin..."
    print_status "Project ID: $PROJECT_ID"
    print_status "Repository: $GITHUB_REPO"
    
    check_gcloud
    check_auth
    set_project
    enable_apis
    create_vm
    setup_firewall
    get_vm_ip
    show_next_steps
}

# Run main function
main "$@"
