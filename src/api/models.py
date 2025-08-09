"""
Pydantic models for client management and API operations
"""

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ClientStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class PlanType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class ClientCreate(BaseModel):
    company_name: str
    contact_email: EmailStr
    contact_name: str
    plan_type: PlanType = PlanType.FREE
    max_documents: int = 10
    max_requests_per_month: int = 1000
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('company_name cannot be empty')
        if len(v) > 100:
            raise ValueError('company_name too long')
        return v.strip()
    
    @field_validator('contact_name')
    @classmethod
    def validate_contact_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('contact_name cannot be empty')
        if len(v) > 100:
            raise ValueError('contact_name too long')
        return v.strip()

class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    plan_type: Optional[PlanType] = None
    max_documents: Optional[int] = None
    max_requests_per_month: Optional[int] = None
    status: Optional[ClientStatus] = None

class ClientResponse(BaseModel):
    client_id: str
    company_name: str
    contact_email: str
    contact_name: str
    plan_type: PlanType
    status: ClientStatus
    max_documents: int
    max_requests_per_month: int
    created_at: datetime
    last_active: Optional[datetime] = None
    api_keys: List[str] = []

class APIKeyCreate(BaseModel):
    client_id: Optional[str] = None
    key_name: str
    expires_at: Optional[datetime] = None
    
    @field_validator('key_name')
    @classmethod
    def validate_key_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('key_name cannot be empty')
        if len(v) > 50:
            raise ValueError('key_name too long')
        return v.strip()

class APIKeyResponse(BaseModel):
    key_id: str
    client_id: str
    key_name: str
    api_key: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True

class UsageStats(BaseModel):
    client_id: str
    total_requests: int
    total_documents: int
    requests_this_month: int
    documents_this_month: int
    last_request: Optional[datetime] = None
    last_document_upload: Optional[datetime] = None

class ChatInput(BaseModel):
    client_id: str
    query: str
    
    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('client_id cannot be empty')
        if len(v) > 100:
            raise ValueError('client_id too long')
        return v.strip()
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('query cannot be empty')
        if len(v) > 1000:
            raise ValueError('query too long')
        return v.strip()

class UploadInput(BaseModel):
    client_id: str
    doc_id: str
    content: str
    
    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('client_id cannot be empty')
        if len(v) > 100:
            raise ValueError('client_id too long')
        return v.strip()
    
    @field_validator('doc_id')
    @classmethod
    def validate_doc_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('doc_id cannot be empty')
        if len(v) > 100:
            raise ValueError('doc_id too long')
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('content cannot be empty')
        if len(v) > 100000:  # 100KB limit
            raise ValueError('content too large')
        return v.strip()
