"""
SQLite Database Management for ChatBot SaaS
Replaces JSON file storage with proper database
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "./data/chatbot_saas.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize database with tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    contact_email TEXT NOT NULL,
                    contact_name TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    max_documents INTEGER NOT NULL,
                    max_requests_per_month INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_active TEXT,
                    UNIQUE(client_id)
                )
            """)
            
            # Create api_keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    key_name TEXT NOT NULL,
                    api_key TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_used TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE CASCADE,
                    UNIQUE(key_id)
                )
            """)
            
            # Create usage_stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    client_id TEXT PRIMARY KEY,
                    total_requests INTEGER NOT NULL DEFAULT 0,
                    total_documents INTEGER NOT NULL DEFAULT 0,
                    requests_this_month INTEGER NOT NULL DEFAULT 0,
                    documents_this_month INTEGER NOT NULL DEFAULT 0,
                    last_request TEXT,
                    last_document_upload TEXT,
                    monthly_reset TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE CASCADE,
                    UNIQUE(client_id)
                )
            """)
            
            # Create documents table for RAG system
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE CASCADE,
                    UNIQUE(client_id, doc_id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_client_id ON api_keys(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_api_key ON api_keys(api_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_stats_client_id ON usage_stats(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_client_id ON documents(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_client_doc ON documents(client_id, doc_id)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries in a transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

# Client operations
class ClientDB:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_client(self, client_data: Dict) -> bool:
        """Create a new client"""
        query = """
            INSERT INTO clients (
                client_id, company_name, contact_email, contact_name,
                plan_type, status, max_documents, max_requests_per_month,
                created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            client_data['client_id'],
            client_data['company_name'],
            client_data['contact_email'],
            client_data['contact_name'],
            client_data['plan_type'],
            client_data['status'],
            client_data['max_documents'],
            client_data['max_requests_per_month'],
            client_data['created_at'],
            client_data.get('last_active')
        )
        return self.db.execute_update(query, params) > 0
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID"""
        query = "SELECT * FROM clients WHERE client_id = ?"
        results = self.db.execute_query(query, (client_id,))
        return results[0] if results else None
    
    def update_client(self, client_id: str, update_data: Dict) -> bool:
        """Update client information"""
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['company_name', 'contact_email', 'contact_name', 'plan_type', 
                      'status', 'max_documents', 'max_requests_per_month', 'last_active']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(client_id)
        query = f"UPDATE clients SET {', '.join(set_clauses)} WHERE client_id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def list_clients(self) -> List[Dict]:
        """List all clients"""
        query = "SELECT * FROM clients ORDER BY created_at DESC"
        return self.db.execute_query(query)
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client (cascades to related data)"""
        query = "DELETE FROM clients WHERE client_id = ?"
        return self.db.execute_update(query, (client_id,)) > 0

# API Key operations
class APIKeyDB:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_api_key(self, key_data: Dict) -> bool:
        """Create a new API key"""
        query = """
            INSERT INTO api_keys (
                key_id, client_id, key_name, api_key, created_at,
                expires_at, last_used, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            key_data['key_id'],
            key_data['client_id'],
            key_data['key_name'],
            key_data['api_key'],
            key_data['created_at'],
            key_data.get('expires_at'),
            key_data.get('last_used'),
            key_data.get('is_active', True)
        )
        return self.db.execute_update(query, params) > 0
    
    def get_api_key(self, key_id: str) -> Optional[Dict]:
        """Get API key by ID"""
        query = "SELECT * FROM api_keys WHERE key_id = ?"
        results = self.db.execute_query(query, (key_id,))
        return results[0] if results else None
    
    def get_api_key_by_value(self, api_key: str) -> Optional[Dict]:
        """Get API key by its value"""
        query = "SELECT * FROM api_keys WHERE api_key = ?"
        results = self.db.execute_query(query, (api_key,))
        return results[0] if results else None
    
    def update_api_key(self, key_id: str, update_data: Dict) -> bool:
        """Update API key"""
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['key_name', 'expires_at', 'last_used', 'is_active']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(key_id)
        query = f"UPDATE api_keys SET {', '.join(set_clauses)} WHERE key_id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def list_api_keys(self, client_id: str) -> List[Dict]:
        """List all API keys for a client"""
        query = "SELECT * FROM api_keys WHERE client_id = ? ORDER BY created_at DESC"
        return self.db.execute_query(query, (client_id,))
    
    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        query = "DELETE FROM api_keys WHERE key_id = ?"
        return self.db.execute_update(query, (key_id,)) > 0

# Usage Stats operations
class UsageStatsDB:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_usage_stats(self, client_id: str, stats_data: Dict) -> bool:
        """Create usage stats for a client"""
        query = """
            INSERT INTO usage_stats (
                client_id, total_requests, total_documents,
                requests_this_month, documents_this_month,
                last_request, last_document_upload, monthly_reset
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            client_id,
            stats_data.get('total_requests', 0),
            stats_data.get('total_documents', 0),
            stats_data.get('requests_this_month', 0),
            stats_data.get('documents_this_month', 0),
            stats_data.get('last_request'),
            stats_data.get('last_document_upload'),
            stats_data.get('monthly_reset')
        )
        return self.db.execute_update(query, params) > 0
    
    def get_usage_stats(self, client_id: str) -> Optional[Dict]:
        """Get usage stats for a client"""
        query = "SELECT * FROM usage_stats WHERE client_id = ?"
        results = self.db.execute_query(query, (client_id,))
        return results[0] if results else None
    
    def update_usage_stats(self, client_id: str, update_data: Dict) -> bool:
        """Update usage stats"""
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['total_requests', 'total_documents', 'requests_this_month',
                      'documents_this_month', 'last_request', 'last_document_upload', 'monthly_reset']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(client_id)
        query = f"UPDATE usage_stats SET {', '.join(set_clauses)} WHERE client_id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def increment_requests(self, client_id: str) -> bool:
        """Increment request counts"""
        query = """
            UPDATE usage_stats 
            SET total_requests = total_requests + 1,
                requests_this_month = requests_this_month + 1,
                last_request = ?
            WHERE client_id = ?
        """
        return self.db.execute_update(query, (datetime.now().isoformat(), client_id)) > 0
    
    def increment_documents(self, client_id: str) -> bool:
        """Increment document counts"""
        query = """
            UPDATE usage_stats 
            SET total_documents = total_documents + 1,
                documents_this_month = documents_this_month + 1,
                last_document_upload = ?
            WHERE client_id = ?
        """
        return self.db.execute_update(query, (datetime.now().isoformat(), client_id)) > 0

# Documents operations for RAG system
class DocumentsDB:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_document(self, client_id: str, doc_id: str, content: str) -> bool:
        """Create or update a document"""
        query = """
            INSERT OR REPLACE INTO documents (
                client_id, doc_id, content, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        params = (client_id, doc_id, content, now, now)
        return self.db.execute_update(query, params) > 0
    
    def get_document(self, client_id: str, doc_id: str) -> Optional[Dict]:
        """Get a document"""
        query = "SELECT * FROM documents WHERE client_id = ? AND doc_id = ?"
        results = self.db.execute_query(query, (client_id, doc_id))
        return results[0] if results else None
    
    def list_documents(self, client_id: str) -> List[Dict]:
        """List all documents for a client"""
        query = "SELECT * FROM documents WHERE client_id = ? ORDER BY updated_at DESC"
        return self.db.execute_query(query, (client_id,))
    
    def delete_document(self, client_id: str, doc_id: str) -> bool:
        """Delete a document"""
        query = "DELETE FROM documents WHERE client_id = ? AND doc_id = ?"
        return self.db.execute_update(query, (client_id, doc_id)) > 0
    
    def get_all_documents_content(self, client_id: str) -> List[str]:
        """Get all document content for a client (for RAG)"""
        query = "SELECT content FROM documents WHERE client_id = ?"
        results = self.db.execute_query(query, (client_id,))
        return [row['content'] for row in results]

# Main database interface
class Database:
    def __init__(self, db_path: str = "./data/chatbot_saas.db"):
        self.db_manager = DatabaseManager(db_path)
        self.clients = ClientDB(self.db_manager)
        self.api_keys = APIKeyDB(self.db_manager)
        self.usage_stats = UsageStatsDB(self.db_manager)
        self.documents = DocumentsDB(self.db_manager)
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_manager.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def get_database_info(self) -> Dict:
        """Get database statistics"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) FROM clients")
            client_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM api_keys")
            api_key_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM usage_stats")
            usage_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            document_count = cursor.fetchone()[0]
            
            return {
                "database_path": self.db_manager.db_path,
                "clients": client_count,
                "api_keys": api_key_count,
                "usage_stats": usage_count,
                "documents": document_count
            }
