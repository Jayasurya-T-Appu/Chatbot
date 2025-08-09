from sentence_transformers import SentenceTransformer
import chromadb
import requests
from typing import List, Optional
import logging
import time
from functools import lru_cache
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from src.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Global thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=4)

# Load embedding model (cached for performance)
@lru_cache(maxsize=1)
def get_embedder():
    """Get cached embedding model"""
    logger.info("Loading embedding model...")
    return SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")

# ChromaDB client with error handling
def get_chroma_client():
    """Get ChromaDB client with error handling"""
    try:
        # Ensure chroma directory exists
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        return chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
        raise

# Global client instance
chroma_client = get_chroma_client()

def embed_text(text: str) -> List[float]:
    """Embed text with error handling"""
    try:
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        embedder = get_embedder()
        embedding = embedder.encode([text])[0].tolist()
        
        if not embedding or len(embedding) == 0:
            raise ValueError("Failed to generate embedding")
            
        return embedding
    except Exception as e:
        logger.error(f"Error embedding text: {str(e)}")
        raise

def embed_batch_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple texts in batch for better performance"""
    try:
        if not texts:
            return []
        
        embedder = get_embedder()
        embeddings = embedder.encode(texts).tolist()
        return embeddings
    except Exception as e:
        logger.error(f"Error batch embedding texts: {str(e)}")
        raise

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Chunk text with validation - optimized version"""
    # Use settings defaults if not provided
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP
    try:
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if chunk_size <= 0 or overlap < 0:
            raise ValueError("Invalid chunk parameters")
        
        # Use sentences instead of words for better semantic chunks
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [text]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # If no chunks were created, return original text
        if not chunks:
            chunks = [text]
            
        return chunks
    except Exception as e:
        logger.error(f"Error chunking text: {str(e)}")
        raise

def get_client_collection(client_id: str):
    """Get client collection with validation"""
    try:
        if not client_id or len(client_id.strip()) == 0:
            raise ValueError("Client ID cannot be empty")
        
        # Sanitize collection name
        collection_name = f"docs_{client_id.strip().replace(' ', '_').replace('-', '_')}"
        
        return chroma_client.get_or_create_collection(name=collection_name)
    except Exception as e:
        logger.error(f"Error getting collection for client {client_id}: {str(e)}")
        raise

async def call_llm_async(prompt: str) -> str:
    """Async LLM call for better performance"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=aiohttp.ClientTimeout(total=15)  # Reduced timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["response"]
                else:
                    raise Exception(f"LLM request failed with status {response.status}")
    except Exception as e:
        logger.error(f"Async LLM request failed: {str(e)}")
        return "Sorry, I couldn't find that information."

def add_document(client_id: str, doc_id: str, content: str) -> dict:
    """Add document with comprehensive error handling - optimized"""
    try:
        start_time = time.time()
        
        # Validate inputs
        if not client_id or len(client_id.strip()) == 0:
            raise ValueError("Client ID cannot be empty")
        if not doc_id or len(doc_id.strip()) == 0:
            raise ValueError("Document ID cannot be empty")
        if not content or len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        logger.info(f"Adding document {doc_id} for client {client_id}")
        
        # Get collection
        collection = get_client_collection(client_id)
        
        # Check if document already exists
        existing = collection.get(ids=[doc_id])
        if existing and existing['ids']:
            logger.warning(f"Document {doc_id} already exists for client {client_id}, updating...")
            # Remove existing chunks
            existing_ids = [id for id in existing['ids'] if id.startswith(f"{doc_id}_")]
            if existing_ids:
                collection.delete(ids=existing_ids)
        
        # Chunk content
        chunks = chunk_text(content)
        logger.info(f"Created {len(chunks)} chunks for document {doc_id}")
        
        # Batch embed all chunks at once
        embeddings = embed_batch_texts(chunks)
        
        # Generate IDs for chunks
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Add to collection in batch
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Document {doc_id} added successfully in {processing_time:.2f}s")
        
        return {
            "doc_id": doc_id,
            "client_id": client_id,
            "chunks_created": len(chunks),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error adding document {doc_id} for client {client_id}: {str(e)}")
        raise

async def query_rag_async(client_id: str, user_query: str, n_results: int = 3) -> str:
    """Async query RAG system for better performance"""
    try:
        start_time = time.time()
        
        # Validate inputs
        if not client_id or len(client_id.strip()) == 0:
            raise ValueError("Client ID cannot be empty")
        if not user_query or len(user_query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        logger.info(f"Processing query for client {client_id}: {user_query[:50]}...")
        
        # Get collection
        collection = get_client_collection(client_id)
        
        # Check if collection has documents
        count = collection.count()
        if count == 0:
            logger.warning(f"No documents found for client {client_id}")
            return "Sorry, I couldn't find that information. No documents have been uploaded yet."
        
        # Embed query
        query_embedding = embed_text(user_query)
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count)
        )
        
        documents = results["documents"][0]
        
        if not documents:
            logger.warning(f"No relevant documents found for query: {user_query}")
            return "Sorry, I couldn't find that information."
        
        # Create context
        context = "\n".join(documents)
        
        # Create prompt
        prompt = f"""
You are a friendly and helpful assistant. Your main purpose is to answer questions using ONLY the information provided in the `Context`.

First, read the `Context` and identify its main subject.

Here are your rules:

1.  **Greeting:** If the user starts with a greeting or a conversational message, respond politely and state that you can help with questions about the main subject of the context. For example: "Hello! I'm here to help you with any questions you have about [main subject of the context]."
2.  **Answering Questions:** If the user asks a question, find the answer *solely* within the `Context` and provide it in a clear, conversational manner. Do not add any information that is not in the text.
3.  **Missing Information:** If the answer to a question is not found in the `Context`, politely inform the user that you cannot find that information in the text you have.
4.  **No Information Dumps:** Avoid preemptively providing large blocks of text from the context. Wait for the user to ask a specific question.

Context:
{context}

Question:
{user_query}

Answer:
"""
        
        # Call LLM asynchronously
        answer = await call_llm_async(prompt)
        
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.2f}s")
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing query for client {client_id}: {str(e)}")
        return "Sorry, I couldn't find that information."

def query_rag(client_id: str, user_query: str, n_results: int = 3) -> str:
    """Synchronous wrapper for async query"""
    try:
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(query_rag_async(client_id, user_query, n_results))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in sync query wrapper: {str(e)}")
        return "Sorry, I couldn't find that information."

def delete_document(client_id: str, doc_id: str) -> dict:
    """Delete document and its chunks"""
    try:
        if not client_id or len(client_id.strip()) == 0:
            raise ValueError("Client ID cannot be empty")
        if not doc_id or len(doc_id.strip()) == 0:
            raise ValueError("Document ID cannot be empty")
        
        collection = get_client_collection(client_id)
        
        # Find all chunks for this document
        existing = collection.get(ids=[doc_id])
        if existing and existing['ids']:
            existing_ids = [id for id in existing['ids'] if id.startswith(f"{doc_id}_")]
            if existing_ids:
                collection.delete(ids=existing_ids)
                logger.info(f"Deleted {len(existing_ids)} chunks for document {doc_id}")
        
        return {"message": f"Document {doc_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document {doc_id} for client {client_id}: {str(e)}")
        raise

def get_client_stats(client_id: str) -> dict:
    """Get statistics for a client"""
    try:
        if not client_id or len(client_id.strip()) == 0:
            raise ValueError("Client ID cannot be empty")
        
        collection = get_client_collection(client_id)
        count = collection.count()
        
        return {
            "client_id": client_id,
            "document_count": count,
            "collection_name": collection.name
        }
        
    except Exception as e:
        logger.error(f"Error getting stats for client {client_id}: {str(e)}")
        raise

