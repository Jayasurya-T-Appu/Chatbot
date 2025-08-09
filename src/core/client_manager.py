"""
Client Management System
Handles client registration, API key management, and usage tracking
"""

import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from src.api.models import (
    ClientCreate, ClientUpdate, ClientResponse, ClientStatus, PlanType,
    APIKeyCreate, APIKeyResponse, UsageStats
)

logger = logging.getLogger(__name__)

from src.core.config import settings

class ClientManager:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.clients_file = os.path.join(data_dir, "clients.json")
        self.api_keys_file = os.path.join(data_dir, "api_keys.json")
        self.usage_file = os.path.join(data_dir, "usage.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data structures
        self.clients: Dict[str, dict] = self._load_data(self.clients_file, {})
        self.api_keys: Dict[str, dict] = self._load_data(self.api_keys_file, {})
        self.usage: Dict[str, dict] = self._load_data(self.usage_file, {})
        
        # Plan configurations
        self.plans = {
            PlanType.FREE: {"max_documents": 10, "max_requests_per_month": 1000},
            PlanType.BASIC: {"max_documents": 100, "max_requests_per_month": 10000},
            PlanType.PRO: {"max_documents": 1000, "max_requests_per_month": 100000},
            PlanType.ENTERPRISE: {"max_documents": -1, "max_requests_per_month": -1}
        }
    
    def _load_data(self, file_path: str, default: dict) -> dict:
        """Load data from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
        return default
    
    def _save_data(self, data: dict, file_path: str):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
    


    def _generate_client_id(self) -> str:
        """Generate a unique client ID"""
        while True:
            client_id = f"{settings.CLIENT_ID_PREFIX}{secrets.token_hex(8)}"
            if client_id not in self.clients:
                return client_id
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"{settings.API_KEY_PREFIX}{secrets.token_hex(32)}"
    
    def create_client(self, client_data: ClientCreate) -> ClientResponse:
        """Create a new client"""
        client_id = self._generate_client_id()
        
        # Get plan limits
        plan_config = self.plans[client_data.plan_type]
        
        client = {
            "client_id": client_id,
            "company_name": client_data.company_name,
            "contact_email": client_data.contact_email,
            "contact_name": client_data.contact_name,
            "plan_type": client_data.plan_type.value,
            "status": ClientStatus.ACTIVE.value,
            "max_documents": plan_config["max_documents"],
            "max_requests_per_month": plan_config["max_requests_per_month"],
            "created_at": datetime.now().isoformat(),
            "last_active": None,
            "api_keys": []
        }
        
        self.clients[client_id] = client
        
        # Initialize usage tracking
        self.usage[client_id] = {
            "total_requests": 0,
            "total_documents": 0,
            "requests_this_month": 0,
            "documents_this_month": 0,
            "last_request": None,
            "last_document_upload": None,
            "monthly_reset": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Save data
        self._save_data(self.clients, self.clients_file)
        self._save_data(self.usage, self.usage_file)
        
        logger.info(f"Created new client: {client_id} ({client_data.company_name})")
        
        return ClientResponse(**client)
    
    def get_client(self, client_id: str) -> Optional[ClientResponse]:
        """Get client by ID"""
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id].copy()
        client["api_keys"] = [key_id for key_id, key_data in self.api_keys.items() 
                             if key_data["client_id"] == client_id and key_data["is_active"]]
        
        return ClientResponse(**client)
    
    def update_client(self, client_id: str, update_data: ClientUpdate) -> Optional[ClientResponse]:
        """Update client information"""
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id]
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field == "plan_type":
                client[field] = value.value
                # Update plan limits
                plan_config = self.plans[value]
                client["max_documents"] = plan_config["max_documents"]
                client["max_requests_per_month"] = plan_config["max_requests_per_month"]
            elif field == "status":
                client[field] = value.value
            else:
                client[field] = value
        
        self._save_data(self.clients, self.clients_file)
        
        return self.get_client(client_id)
    
    def create_api_key(self, key_data: APIKeyCreate) -> Optional[APIKeyResponse]:
        """Create a new API key for a client"""
        if key_data.client_id not in self.clients:
            return None
        
        key_id = f"key_{secrets.token_hex(8)}"
        api_key = self._generate_api_key()
        
        key_info = {
            "key_id": key_id,
            "client_id": key_data.client_id,
            "key_name": key_data.key_name,
            "api_key": api_key,
            "created_at": datetime.now().isoformat(),
            "expires_at": key_data.expires_at.isoformat() if key_data.expires_at else None,
            "last_used": None,
            "is_active": True
        }
        
        self.api_keys[key_id] = key_info
        
        # Add to client's API keys list
        self.clients[key_data.client_id]["api_keys"].append(key_id)
        
        self._save_data(self.api_keys, self.api_keys_file)
        self._save_data(self.clients, self.clients_file)
        
        logger.info(f"Created API key {key_id} for client {key_data.client_id}")
        
        return APIKeyResponse(**key_info)
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return client ID"""
        for key_id, key_data in self.api_keys.items():
            if key_data["api_key"] == api_key and key_data["is_active"]:
                # Check if key is expired
                if key_data["expires_at"]:
                    expires_at = datetime.fromisoformat(key_data["expires_at"])
                    if datetime.now() > expires_at:
                        continue
                
                # Update last used
                key_data["last_used"] = datetime.now().isoformat()
                self._save_data(self.api_keys, self.api_keys_file)
                
                return key_data["client_id"]
        
        return None
    
    def get_client_by_api_key(self, api_key: str) -> Optional[ClientResponse]:
        """Get client information by API key"""
        client_id = self.verify_api_key(api_key)
        if client_id:
            return self.get_client(client_id)
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id not in self.api_keys:
            return False
        
        self.api_keys[key_id]["is_active"] = False
        self._save_data(self.api_keys, self.api_keys_file)
        
        logger.info(f"Revoked API key: {key_id}")
        return True
    
    def track_request(self, client_id: str):
        """Track API request usage"""
        if client_id not in self.usage:
            return
        
        usage = self.usage[client_id]
        usage["total_requests"] += 1
        usage["requests_this_month"] += 1
        usage["last_request"] = datetime.now().isoformat()
        
        # Check monthly reset
        if usage["monthly_reset"]:
            reset_date = datetime.fromisoformat(usage["monthly_reset"])
            if datetime.now() > reset_date:
                usage["requests_this_month"] = 1
                usage["documents_this_month"] = 0
                usage["monthly_reset"] = (datetime.now() + timedelta(days=30)).isoformat()
        
        self._save_data(self.usage, self.usage_file)
    
    def track_document_upload(self, client_id: str):
        """Track document upload usage"""
        if client_id not in self.usage:
            return
        
        usage = self.usage[client_id]
        usage["total_documents"] += 1
        usage["documents_this_month"] += 1
        usage["last_document_upload"] = datetime.now().isoformat()
        
        self._save_data(self.usage, self.usage_file)
    
    def get_usage_stats(self, client_id: str) -> Optional[UsageStats]:
        """Get usage statistics for a client"""
        if client_id not in self.usage:
            return None
        
        usage = self.usage[client_id]
        return UsageStats(
            client_id=client_id,
            total_requests=usage["total_requests"],
            total_documents=usage["total_documents"],
            requests_this_month=usage["requests_this_month"],
            documents_this_month=usage["documents_this_month"],
            last_request=datetime.fromisoformat(usage["last_request"]) if usage["last_request"] else None,
            last_document_upload=datetime.fromisoformat(usage["last_document_upload"]) if usage["last_document_upload"] else None
        )
    
    def check_limits(self, client_id: str) -> Tuple[bool, str]:
        """Check if client is within their plan limits"""
        if client_id not in self.clients or client_id not in self.usage:
            return False, "Client not found"
        
        client = self.clients[client_id]
        usage = self.usage[client_id]
        
        # Check status
        if client["status"] != ClientStatus.ACTIVE.value:
            return False, f"Client account is {client['status']}"
        
        # Check document limit
        if client["max_documents"] != -1 and usage["total_documents"] >= client["max_documents"]:
            return False, f"Document limit exceeded ({usage['total_documents']}/{client['max_documents']})"
        
        # Check monthly request limit
        if client["max_requests_per_month"] != -1 and usage["requests_this_month"] >= client["max_requests_per_month"]:
            return False, f"Monthly request limit exceeded ({usage['requests_this_month']}/{client['max_requests_per_month']})"
        
        return True, "OK"
    
    def list_clients(self) -> List[ClientResponse]:
        """List all clients"""
        return [self.get_client(client_id) for client_id in self.clients.keys()]
    
    def list_api_keys(self, client_id: str) -> List[APIKeyResponse]:
        """List all API keys for a client"""
        keys = []
        for key_id, key_data in self.api_keys.items():
            if key_data["client_id"] == client_id:
                keys.append(APIKeyResponse(**key_data))
        return keys
