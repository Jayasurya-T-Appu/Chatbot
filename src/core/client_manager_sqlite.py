"""
Client Management System with SQLite Database
Replaces JSON file storage with proper database
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from src.api.models import (
    ClientCreate, ClientUpdate, ClientResponse, ClientStatus, PlanType,
    APIKeyCreate, APIKeyResponse, UsageStats
)
from src.core.database import Database
from src.core.config import settings

logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.db = Database(f"{data_dir}/chatbot_saas.db")
        
        # Plan configurations
        self.plans = {
            PlanType.FREE: {"max_documents": 10, "max_requests_per_month": 1000},
            PlanType.BASIC: {"max_documents": 100, "max_requests_per_month": 10000},
            PlanType.PRO: {"max_documents": 1000, "max_requests_per_month": 100000},
            PlanType.ENTERPRISE: {"max_documents": -1, "max_requests_per_month": -1}
        }
    
    def _generate_client_id(self) -> str:
        """Generate a unique client ID"""
        while True:
            client_id = f"{settings.CLIENT_ID_PREFIX}{secrets.token_hex(8)}"
            if not self.db.clients.get_client(client_id):
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
            "last_active": None
        }
        
        # Create client in database
        if not self.db.clients.create_client(client):
            raise Exception("Failed to create client in database")
        
        # Initialize usage tracking
        usage_stats = {
            "total_requests": 0,
            "total_documents": 0,
            "requests_this_month": 0,
            "documents_this_month": 0,
            "last_request": None,
            "last_document_upload": None,
            "monthly_reset": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        if not self.db.usage_stats.create_usage_stats(client_id, usage_stats):
            raise Exception("Failed to create usage stats")
        
        logger.info(f"Created new client: {client_id} ({client_data.company_name})")
        
        return ClientResponse(**client)
    
    def get_client(self, client_id: str) -> Optional[ClientResponse]:
        """Get client by ID"""
        client = self.db.clients.get_client(client_id)
        if not client:
            return None
        
        # Get API keys for this client
        api_keys = self.db.api_keys.list_api_keys(client_id)
        client["api_keys"] = [key["key_id"] for key in api_keys if key["is_active"]]
        
        return ClientResponse(**client)
    
    def update_client(self, client_id: str, update_data: ClientUpdate) -> Optional[ClientResponse]:
        """Update client information"""
        if not self.db.clients.get_client(client_id):
            return None
        
        update_dict = {}
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field == "plan_type":
                update_dict["plan_type"] = value.value
                # Update plan limits
                plan_config = self.plans[value]
                update_dict["max_documents"] = plan_config["max_documents"]
                update_dict["max_requests_per_month"] = plan_config["max_requests_per_month"]
            elif field == "status":
                update_dict["status"] = value.value
            else:
                update_dict[field] = value
        
        if update_dict and not self.db.clients.update_client(client_id, update_dict):
            return None
        
        return self.get_client(client_id)
    
    def create_api_key(self, key_data: APIKeyCreate) -> Optional[APIKeyResponse]:
        """Create a new API key for a client"""
        if not self.db.clients.get_client(key_data.client_id):
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
        
        if not self.db.api_keys.create_api_key(key_info):
            return None
        
        logger.info(f"Created API key {key_id} for client {key_data.client_id}")
        
        return APIKeyResponse(**key_info)
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return client ID"""
        key_data = self.db.api_keys.get_api_key_by_value(api_key)
        if not key_data or not key_data["is_active"]:
            return None
        
        # Check if key is expired
        if key_data["expires_at"]:
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if datetime.now() > expires_at:
                return None
        
        # Update last used
        self.db.api_keys.update_api_key(key_data["key_id"], {
            "last_used": datetime.now().isoformat()
        })
        
        return key_data["client_id"]
    
    def get_client_by_api_key(self, api_key: str) -> Optional[ClientResponse]:
        """Get client information by API key"""
        client_id = self.verify_api_key(api_key)
        if client_id:
            return self.get_client(client_id)
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        return self.db.api_keys.update_api_key(key_id, {"is_active": False})
    
    def track_request(self, client_id: str):
        """Track API request usage"""
        self.db.usage_stats.increment_requests(client_id)
        
        # Check monthly reset
        usage = self.db.usage_stats.get_usage_stats(client_id)
        if usage and usage["monthly_reset"]:
            reset_date = datetime.fromisoformat(usage["monthly_reset"])
            if datetime.now() > reset_date:
                self.db.usage_stats.update_usage_stats(client_id, {
                    "requests_this_month": 1,
                    "documents_this_month": 0,
                    "monthly_reset": (datetime.now() + timedelta(days=30)).isoformat()
                })
    
    def track_document_upload(self, client_id: str):
        """Track document upload usage"""
        self.db.usage_stats.increment_documents(client_id)
    
    def get_usage_stats(self, client_id: str) -> Optional[UsageStats]:
        """Get usage statistics for a client"""
        usage = self.db.usage_stats.get_usage_stats(client_id)
        if not usage:
            return None
        
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
        client = self.db.clients.get_client(client_id)
        usage = self.db.usage_stats.get_usage_stats(client_id)
        
        if not client or not usage:
            return False, "Client not found"
        
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
        clients = self.db.clients.list_clients()
        result = []
        
        for client in clients:
            # Get API keys for each client
            api_keys = self.db.api_keys.list_api_keys(client["client_id"])
            client["api_keys"] = [key["key_id"] for key in api_keys if key["is_active"]]
            result.append(ClientResponse(**client))
        
        return result
    
    def list_api_keys(self, client_id: str) -> List[APIKeyResponse]:
        """List all API keys for a client"""
        keys = self.db.api_keys.list_api_keys(client_id)
        return [APIKeyResponse(**key) for key in keys]
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client and all related data"""
        return self.db.clients.delete_client(client_id)
    
    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        return self.db.api_keys.delete_api_key(key_id)
    
    def get_database_info(self) -> Dict:
        """Get database statistics"""
        return self.db.get_database_info()
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        return self.db.backup_database(backup_path)
