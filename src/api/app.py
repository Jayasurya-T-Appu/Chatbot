from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.core.rag import add_document, query_rag, delete_document, get_client_stats
from src.utils.pdf_util import extract_text_from_pdf
from src.api.models import ChatInput, UploadInput, ClientResponse
from src.api.admin import router as admin_router
from src.core.client_manager_sqlite import ClientManager
from src.core.config import settings
import os
import logging
import asyncio
from typing import Optional
import time

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

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include admin router
app.include_router(admin_router)

# Initialize client manager
client_manager = ClientManager(settings.DATA_DIR)

def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Remove 'Bearer ' prefix if present
    api_key = authorization.replace('Bearer ', '')
    
    # Verify API key and get client
    client = client_manager.get_client_by_api_key(api_key)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check if client is active
    if client.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is suspended. Please contact support for activation."
        )
    
    return client



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/")
async def root():
    """Redirect to demo page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/html/demo.html")

@app.get("/admin")
async def admin_login():
    """Admin login page"""
    from fastapi.responses import FileResponse
    return FileResponse("src/static/html/admin-login.html", media_type="text/html")

@app.get("/debug-admin")
async def debug_admin():
    """Debug admin page"""
    from fastapi.responses import FileResponse
    return FileResponse("debug_admin.html", media_type="text/html")

@app.post("/admin/auth")
async def admin_auth(authorization: str = Header(None)):
    """Authenticate admin API key"""
    try:
        # Verify the admin key using the same logic as admin router
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
        
        return {
            "success": True,
            "message": "Authentication successful",
            "admin_key": api_key
        }
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "status_code": e.status_code
        }

@app.get("/admin-dashboard")
async def admin_dashboard():
    """Admin dashboard page - authentication handled by frontend"""
    from fastapi.responses import FileResponse
    return FileResponse("src/static/html/admin-dashboard.html", media_type="text/html")

@app.get("/widget.js")
async def get_widget():
    """Serve the widget JavaScript file"""
    from fastapi.responses import FileResponse
    return FileResponse("src/static/js/widget.js", media_type="application/javascript")

@app.post("/ask")
async def ask(input: ChatInput, client: ClientResponse = Depends(verify_api_key)):
    """Ask a question to the RAG system"""
    try:
        start_time = time.time()
        logger.info(f"Processing query for client {client.client_id}")
        
        # Verify client_id matches API key
        if input.client_id != client.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client ID mismatch"
            )
        
        # Check client limits
        within_limits, message = client_manager.check_limits(client.client_id)
        if not within_limits:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Usage limit exceeded: {message}"
            )
        
        # Use async query for better performance
        from src.core.rag import query_rag_async
        answer = await query_rag_async(input.client_id, input.query)
        
        # Track usage
        client_manager.track_request(client.client_id)
        
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.2f}s for client {input.client_id}")
        
        return {
            "answer": answer,
            "processing_time": processing_time,
            "client_id": input.client_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query for client {input.client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

@app.post("/upload")
async def upload(input: UploadInput):
    """Upload text content to the RAG system"""
    try:
        start_time = time.time()
        logger.info(f"Uploading document {input.doc_id} for client {input.client_id}")
        
        add_document(input.client_id, input.doc_id, input.content)
        
        processing_time = time.time() - start_time
        logger.info(f"Document uploaded in {processing_time:.2f}s for client {input.client_id}")
        
        return {
            "message": "Document uploaded successfully!",
            "doc_id": input.doc_id,
            "client_id": input.client_id,
            "processing_time": processing_time
        }
    except Exception as e:
        logger.error(f"Error uploading document for client {input.client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@app.post("/upload-pdf")
async def upload_pdf(
    client_id: str = Form(...),
    doc_id: str = Form(...),
    file: UploadFile = File(...),
    client: ClientResponse = Depends(verify_api_key)
):
    """Upload PDF file to the RAG system"""
    try:
        start_time = time.time()
        
        # Validate inputs
        if not client_id or len(client_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id cannot be empty"
            )
        if not doc_id or len(doc_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="doc_id cannot be empty"
            )
        
        # Verify client_id matches API key
        if client_id != client.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client ID mismatch"
            )
        
        # Check client limits
        within_limits, message = client_manager.check_limits(client.client_id)
        if not within_limits:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Usage limit exceeded: {message}"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Check file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB"
            )
        
        logger.info(f"Processing PDF {file.filename} for client {client_id}")
        
        # Save file temporarily
        file_path = f"./tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        try:
            # Extract text from PDF
            extracted_content = extract_text_from_pdf(file_path)
            
            if not extracted_content or len(extracted_content.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from PDF. File might be corrupted or empty."
                )
            
            # Add to RAG system
            add_document(client_id, doc_id, extracted_content)
            
            # Track usage
            client_manager.track_document_upload(client.client_id)
            
            processing_time = time.time() - start_time
            logger.info(f"PDF processed in {processing_time:.2f}s for client {client_id}")
            
            return {
                "message": "PDF uploaded and processed successfully",
                "doc_id": doc_id,
                "client_id": client_id,
                "file_size": file_size,
                "content_length": len(extracted_content),
                "processing_time": processing_time
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

@app.delete("/documents/{client_id}/{doc_id}")
async def delete_doc(client_id: str, doc_id: str):
    """Delete a document"""
    try:
        result = delete_document(client_id, doc_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@app.get("/stats/{client_id}")
async def get_stats(client_id: str):
    """Get client statistics"""
    try:
        stats = get_client_stats(client_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred"
    }