#!/usr/bin/env python3
"""
Client Onboarding Script
Helps create new clients and generate API keys
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"
ADMIN_API_KEY = "admin-secret-key-12345"

def create_client(company_name, contact_email, contact_name, plan_type="basic"):
    """Create a new client"""
    url = f"{API_BASE_URL}/admin/clients"
    headers = {
        "Authorization": f"Bearer {ADMIN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "company_name": company_name,
        "contact_email": contact_email,
        "contact_name": contact_name,
        "plan_type": plan_type
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating client: {e}")
        return None

def create_api_key(client_id, key_name, expires_in_days=None):
    """Create an API key for a client"""
    url = f"{API_BASE_URL}/admin/clients/{client_id}/api-keys"
    headers = {
        "Authorization": f"Bearer {ADMIN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "key_name": key_name,
        "expires_at": None
    }
    
    if expires_in_days:
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        data["expires_at"] = expires_at.isoformat()
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating API key: {e}")
        return None

def generate_integration_code(client_id, api_key, widget_url=None):
    """Generate integration code for the client"""
    if not widget_url:
        widget_url = f"{API_BASE_URL}/widget.js"
    
    integration_code = f"""
<!-- ChatBot Widget Integration -->
<script src="{widget_url}"></script>
<script>
  ChatBotWidget.init({{
    clientId: '{client_id}',
    apiKey: '{api_key}',
    title: 'Chat with us',
    primaryColor: '#007bff',
    welcomeMessage: 'Hello! How can I help you today?'
  }});
</script>
"""
    
    return integration_code

def main():
    print("🤖 ChatBot Client Onboarding")
    print("=" * 40)
    
    # Get client information
    company_name = input("Company Name: ").strip()
    contact_email = input("Contact Email: ").strip()
    contact_name = input("Contact Name: ").strip()
    
    print("\nAvailable Plans:")
    print("1. free - 10 documents, 1,000 requests/month")
    print("2. basic - 100 documents, 10,000 requests/month")
    print("3. pro - 1,000 documents, 100,000 requests/month")
    print("4. enterprise - Unlimited")
    
    plan_choice = input("Select plan (1-4) [2]: ").strip() or "2"
    plan_map = {"1": "free", "2": "basic", "3": "pro", "4": "enterprise"}
    plan_type = plan_map.get(plan_choice, "basic")
    
    # Create client
    print(f"\nCreating client for {company_name}...")
    client = create_client(company_name, contact_email, contact_name, plan_type)
    
    if not client:
        print("Failed to create client. Exiting.")
        sys.exit(1)
    
    print(f"✅ Client created successfully!")
    print(f"Client ID: {client['client_id']}")
    
    # Create API key
    key_name = input(f"\nAPI Key Name [Production]: ").strip() or "Production"
    expires_in_days = input("Expires in days (leave empty for no expiration): ").strip()
    expires_in_days = int(expires_in_days) if expires_in_days else None
    
    print(f"Creating API key '{key_name}'...")
    api_key_data = create_api_key(client['client_id'], key_name, expires_in_days)
    
    if not api_key_data:
        print("Failed to create API key. Exiting.")
        sys.exit(1)
    
    print(f"✅ API key created successfully!")
    print(f"API Key: {api_key_data['api_key']}")
    
    # Generate integration code
    widget_url = input(f"\nWidget URL [{API_BASE_URL}/widget.js]: ").strip() or f"{API_BASE_URL}/widget.js"
    
    integration_code = generate_integration_code(
        client['client_id'], 
        api_key_data['api_key'], 
        widget_url
    )
    
    # Save to file
    filename = f"integration_{client['client_id']}.html"
    with open(filename, 'w') as f:
        f.write(integration_code)
    
    # Display summary
    print("\n" + "=" * 40)
    print("🎉 CLIENT ONBOARDING COMPLETE!")
    print("=" * 40)
    print(f"Company: {company_name}")
    print(f"Contact: {contact_name} ({contact_email})")
    print(f"Plan: {plan_type}")
    print(f"Client ID: {client['client_id']}")
    print(f"API Key: {api_key_data['api_key']}")
    print(f"Integration file: {filename}")
    print("\nIntegration code:")
    print("-" * 20)
    print(integration_code)
    print("-" * 20)
    
    print(f"\n📋 Next Steps:")
    print(f"1. Send the integration code to {contact_name}")
    print(f"2. They can add it to their website")
    print(f"3. Monitor usage at: {API_BASE_URL}/admin/dashboard")
    print(f"4. Client can upload documents via API or admin panel")

if __name__ == "__main__":
    main()
