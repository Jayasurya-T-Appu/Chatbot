"""
Admin API endpoints for client management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header, Form, File, UploadFile
from typing import List, Optional
import logging
from src.api.models import (
    ClientCreate, ClientUpdate, ClientResponse, APIKeyCreate, APIKeyResponse, UsageStats
)
from src.core.client_manager_sqlite import ClientManager

logger = logging.getLogger(__name__)

# Initialize client manager
client_manager = ClientManager()

from src.core.config import settings

# Admin API key (in production, use proper authentication)
ADMIN_API_KEY = settings.ADMIN_API_KEY

def verify_admin_key(authorization: str = Header(None)):
    """Verify admin API key"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key required"
        )
    
    api_key = authorization.replace('Bearer ', '')
    if api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )
    
    return api_key

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/clients", response_model=ClientResponse)
async def create_client(
    company_name: str = Form(...),
    contact_email: str = Form(...),
    contact_name: str = Form(...),
    plan_type: str = Form("free"),
    initial_document: Optional[UploadFile] = File(None),
    admin_key: str = Depends(verify_admin_key)
):
    """Create a new client with optional initial document"""
    try:
        # Create client data
        client_data = ClientCreate(
            company_name=company_name,
            contact_email=contact_email,
            contact_name=contact_name,
            plan_type=plan_type
        )
        
        # Create the client
        client = client_manager.create_client(client_data)
        
        # If initial document is provided, upload it
        if initial_document:
            if not initial_document.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are supported"
                )
            
            # Read file content
            content = await initial_document.read()
            
            # Save file temporarily
            import os
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            file_path = f"{settings.TEMP_DIR}/{initial_document.filename}"
            
            try:
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Extract text from PDF
                from src.utils.pdf_util import extract_text_from_pdf
                extracted_content = extract_text_from_pdf(file_path)
                
                if extracted_content and len(extracted_content.strip()) > 0:
                    # Add to RAG system
                    from src.core.rag import add_document
                    add_document(client.client_id, "initial_document", extracted_content)
                    logger.info(f"Initial document uploaded for client: {client.client_id}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        logger.info(f"Admin created client: {client.client_id}")
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create client: {str(e)}"
        )

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(admin_key: str = Depends(verify_admin_key)):
    """List all clients"""
    try:
        clients = client_manager.list_clients()
        return clients
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list clients: {str(e)}"
        )

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Get client by ID"""
    client = client_manager.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    update_data: ClientUpdate,
    admin_key: str = Depends(verify_admin_key)
):
    """Update client information"""
    try:
        client = client_manager.update_client(client_id, update_data)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        logger.info(f"Admin updated client: {client_id}")
        return client
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update client: {str(e)}"
        )

@router.post("/clients/{client_id}/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    client_id: str,
    key_data: APIKeyCreate,
    admin_key: str = Depends(verify_admin_key)
):
    """Create a new API key for a client"""
    try:
        # Override client_id from path
        key_data.client_id = client_id
        
        api_key = client_manager.create_api_key(key_data)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        logger.info(f"Admin created API key for client: {client_id}")
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )

@router.get("/clients/{client_id}/api-keys", response_model=List[APIKeyResponse])
async def list_client_api_keys(
    client_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """List all API keys for a client"""
    try:
        api_keys = client_manager.list_api_keys(client_id)
        return api_keys
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list API keys: {str(e)}"
        )

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Revoke an API key"""
    try:
        success = client_manager.revoke_api_key(key_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        logger.info(f"Admin revoked API key: {key_id}")
        return {"message": "API key revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )

@router.delete("/api-keys/{key_id}/permanent")
async def delete_api_key(
    key_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Permanently delete an API key"""
    try:
        success = client_manager.delete_api_key(key_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        logger.info(f"Admin permanently deleted API key: {key_id}")
        return {"message": "API key permanently deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )

@router.get("/clients/{client_id}/usage", response_model=UsageStats)
async def get_client_usage(
    client_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Get usage statistics for a client"""
    try:
        usage = client_manager.get_usage_stats(client_id)
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )

@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Delete a client and all related data"""
    try:
        # Check if client exists first
        client = client_manager.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Delete the client
        success = client_manager.delete_client(client_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete client"
            )
        
        logger.info(f"Admin deleted client: {client_id} ({client.company_name})")
        return {
            "message": "Client deleted successfully",
            "client_id": client_id,
            "company_name": client.company_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete client: {str(e)}"
        )

@router.get("/dashboard")
async def get_dashboard(admin_key: str = Depends(verify_admin_key)):
    """Get admin dashboard data"""
    try:
        clients = client_manager.list_clients()
        
        # Calculate dashboard metrics
        total_clients = len(clients)
        active_clients = len([c for c in clients if c.status.value == "active"])
        total_requests = sum(client_manager.get_usage_stats(c.client_id).total_requests 
                           for c in clients if client_manager.get_usage_stats(c.client_id))
        total_documents = sum(client_manager.get_usage_stats(c.client_id).total_documents 
                             for c in clients if client_manager.get_usage_stats(c.client_id))
        
        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_requests": total_requests,
            "total_documents": total_documents,
            "recent_clients": clients[-5:] if clients else []  # Last 5 clients
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )
