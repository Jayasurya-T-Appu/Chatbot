#!/usr/bin/env python3
"""
Migration script to move from JSON files to SQLite database
"""

import json
import os
import sys
from datetime import datetime
from src.core.database import Database
from src.core.config import settings

def load_json_file(file_path: str) -> dict:
    """Load JSON file safely"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def migrate_clients(db: Database, clients_data: dict) -> int:
    """Migrate clients data"""
    migrated_count = 0
    
    for client_id, client_data in clients_data.items():
        try:
            # Ensure client_id is set
            client_data['client_id'] = client_id
            
            # Convert status to lowercase if needed
            if 'status' in client_data:
                client_data['status'] = client_data['status'].lower()
            
            # Create client in database
            if db.clients.create_client(client_data):
                migrated_count += 1
                print(f"✓ Migrated client: {client_id}")
            else:
                print(f"✗ Failed to migrate client: {client_id}")
                
        except Exception as e:
            print(f"✗ Error migrating client {client_id}: {e}")
    
    return migrated_count

def migrate_api_keys(db: Database, api_keys_data: dict) -> int:
    """Migrate API keys data"""
    migrated_count = 0
    
    for key_id, key_data in api_keys_data.items():
        try:
            # Ensure key_id is set
            key_data['key_id'] = key_id
            
            # Convert boolean values
            if 'is_active' in key_data:
                key_data['is_active'] = bool(key_data['is_active'])
            
            # Create API key in database
            if db.api_keys.create_api_key(key_data):
                migrated_count += 1
                print(f"✓ Migrated API key: {key_id}")
            else:
                print(f"✗ Failed to migrate API key: {key_id}")
                
        except Exception as e:
            print(f"✗ Error migrating API key {key_id}: {e}")
    
    return migrated_count

def migrate_usage_stats(db: Database, usage_data: dict) -> int:
    """Migrate usage statistics data"""
    migrated_count = 0
    
    for client_id, stats_data in usage_data.items():
        try:
            # Create usage stats in database
            if db.usage_stats.create_usage_stats(client_id, stats_data):
                migrated_count += 1
                print(f"✓ Migrated usage stats: {client_id}")
            else:
                print(f"✗ Failed to migrate usage stats: {client_id}")
                
        except Exception as e:
            print(f"✗ Error migrating usage stats {client_id}: {e}")
    
    return migrated_count

def backup_json_files():
    """Create backup of JSON files"""
    backup_dir = "./data/backup_json"
    os.makedirs(backup_dir, exist_ok=True)
    
    json_files = ['clients.json', 'api_keys.json', 'usage.json']
    
    for filename in json_files:
        source_path = f"./data/{filename}"
        backup_path = f"{backup_dir}/{filename}"
        
        if os.path.exists(source_path):
            try:
                import shutil
                shutil.copy2(source_path, backup_path)
                print(f"✓ Backed up {filename}")
            except Exception as e:
                print(f"✗ Failed to backup {filename}: {e}")

def main():
    """Main migration function"""
    print("🚀 Starting migration from JSON to SQLite...")
    print("=" * 50)
    
    # Initialize database
    db = Database(settings.DATA_DIR + "/chatbot_saas.db")
    
    # Create backup of JSON files
    print("\n📦 Creating backup of JSON files...")
    backup_json_files()
    
    # Load JSON data
    print("\n📖 Loading JSON data...")
    clients_data = load_json_file("./data/clients.json")
    api_keys_data = load_json_file("./data/api_keys.json")
    usage_data = load_json_file("./data/usage.json")
    
    print(f"Found {len(clients_data)} clients")
    print(f"Found {len(api_keys_data)} API keys")
    print(f"Found {len(usage_data)} usage records")
    
    # Migrate data
    print("\n🔄 Migrating data to SQLite...")
    
    clients_migrated = migrate_clients(db, clients_data)
    api_keys_migrated = migrate_api_keys(db, api_keys_data)
    usage_migrated = migrate_usage_stats(db, usage_data)
    
    # Show results
    print("\n" + "=" * 50)
    print("📊 Migration Results:")
    print(f"✓ Clients migrated: {clients_migrated}/{len(clients_data)}")
    print(f"✓ API keys migrated: {api_keys_migrated}/{len(api_keys_data)}")
    print(f"✓ Usage records migrated: {usage_migrated}/{len(usage_data)}")
    
    # Show database info
    db_info = db.get_database_info()
    print(f"\n📁 Database location: {db_info['database_path']}")
    print(f"📊 Database statistics:")
    print(f"   - Clients: {db_info['clients']}")
    print(f"   - API Keys: {db_info['api_keys']}")
    print(f"   - Usage Stats: {db_info['usage_stats']}")
    print(f"   - Documents: {db_info['documents']}")
    
    print("\n✅ Migration completed!")
    print("\n📝 Next steps:")
    print("1. Test your application with the new database")
    print("2. If everything works, you can delete the JSON files")
    print("3. Update your client_manager.py to use the new database")
    print("4. The JSON files are backed up in ./data/backup_json/")

if __name__ == "__main__":
    main()
