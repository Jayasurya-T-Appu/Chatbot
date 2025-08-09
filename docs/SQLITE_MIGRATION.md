# SQLite Database Migration Guide

This guide covers migrating your ChatBot SaaS from JSON file storage to SQLite database for better performance, reliability, and scalability.

## Why Migrate to SQLite?

### Benefits:
- ✅ **Better Performance**: Faster queries and data access
- ✅ **Data Integrity**: ACID compliance and foreign key constraints
- ✅ **Concurrent Access**: Multiple processes can safely access data
- ✅ **Backup & Recovery**: Easy database backup and restore
- ✅ **Scalability**: Better handling of large datasets
- ✅ **Query Capabilities**: SQL queries for complex data operations

### Current JSON Files:
- `data/clients.json` - Client information
- `data/api_keys.json` - API key management
- `data/usage.json` - Usage statistics

### New SQLite Database:
- `data/chatbot_saas.db` - Single database file with all data

## Migration Steps

### 1. Backup Your Data

```bash
# Create backup directory
mkdir -p data/backup_json

# Backup existing JSON files
cp data/clients.json data/backup_json/
cp data/api_keys.json data/backup_json/
cp data/usage.json data/backup_json/

echo "✅ JSON files backed up to data/backup_json/"
```

### 2. Run Migration Script

```bash
# Run the migration script
python migrate_to_sqlite.py
```

**Expected Output:**
```
🚀 Starting migration from JSON to SQLite...
==================================================

📦 Creating backup of JSON files...
✓ Backed up clients.json
✓ Backed up api_keys.json
✓ Backed up usage.json

📖 Loading JSON data...
Found 2 clients
Found 5 API keys
Found 2 usage records

🔄 Migrating data to SQLite...
✓ Migrated client: client_97fd3395a4ee6f66
✓ Migrated client: client_e4004933ab3db2fb
✓ Migrated API key: key_2cc0dc0e801425bf
✓ Migrated API key: key_bdaacaba63048b1b
...

==================================================
📊 Migration Results:
✓ Clients migrated: 2/2
✓ API keys migrated: 5/5
✓ Usage records migrated: 2/2

📁 Database location: ./data/chatbot_saas.db
📊 Database statistics:
   - Clients: 2
   - API Keys: 5
   - Usage Stats: 2
   - Documents: 0

✅ Migration completed!
```

### 3. Test the Migration

```bash
# Test the new database
python test_database.py
```

**Expected Output:**
```
🧪 Testing SQLite Database Migration...
==================================================

📊 Database Information:
   database_path: ./data/chatbot_saas.db
   clients: 2
   api_keys: 5
   usage_stats: 2
   documents: 0

👥 Testing Client Manager:
   Found 2 clients in database
   - client_97fd3395a4ee6f66: TEST (suspended)
     API Keys: 4
     Usage: 3 requests, 0 documents
   - client_e4004933ab3db2fb: Test2 (suspended)
     API Keys: 1
     Usage: 8 requests, 0 documents

✅ Database test completed successfully!
```

### 4. Update Your Application

Replace the old client manager with the new SQLite version:

```python
# OLD: from src.core.client_manager import ClientManager
# NEW:
from src.core.client_manager_sqlite import ClientManager
```

### 5. Verify Everything Works

```bash
# Start your application
python main.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/admin
```

## Database Schema

### Tables Created:

#### 1. `clients` Table
```sql
CREATE TABLE clients (
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
);
```

#### 2. `api_keys` Table
```sql
CREATE TABLE api_keys (
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
);
```

#### 3. `usage_stats` Table
```sql
CREATE TABLE usage_stats (
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
);
```

#### 4. `documents` Table
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE CASCADE,
    UNIQUE(client_id, doc_id)
);
```

## Database Management

### Backup Database

```bash
# Create backup
python -c "
from src.core.database import Database
from src.core.config import settings
db = Database(settings.DATABASE_PATH)
db.backup_database('./data/backup_$(date +%Y%m%d_%H%M%S).db')
print('Database backed up successfully!')
"
```

### View Database Info

```bash
python -c "
from src.core.database import Database
from src.core.config import settings
db = Database(settings.DATABASE_PATH)
info = db.get_database_info()
for key, value in info.items():
    print(f'{key}: {value}')
"
```

### SQLite Browser (Optional)

Install SQLite Browser for GUI database management:

```bash
# Ubuntu/Debian
sudo apt install sqlitebrowser

# macOS
brew install db-browser-for-sqlite

# Windows
# Download from https://sqlitebrowser.org/
```

Then open your database:
```bash
sqlitebrowser data/chatbot_saas.db
```

## Docker Integration

### Update Docker Compose

The database file is automatically persisted through the volume mount:

```yaml
# docker-compose.yml
services:
  chatbot-saas:
    volumes:
      - ./data:/app/data  # This persists the SQLite database
```

### Database in Docker

```bash
# Access database inside container
docker-compose exec chatbot-saas sqlite3 /app/data/chatbot_saas.db

# View tables
.tables

# View clients
SELECT * FROM clients;

# Exit
.quit
```

## Troubleshooting

### Common Issues

#### 1. Migration Fails
```bash
# Check JSON file format
python -c "import json; print(json.load(open('data/clients.json')))"

# Check database permissions
ls -la data/
chmod 755 data/
```

#### 2. Database Locked
```bash
# Check if another process is using the database
lsof data/chatbot_saas.db

# Restart application
docker-compose restart chatbot-saas
```

#### 3. Data Not Migrated
```bash
# Check migration logs
python migrate_to_sqlite.py

# Manual migration
python -c "
from migrate_to_sqlite import main
main()
"
```

### Rollback Plan

If you need to rollback to JSON files:

```bash
# Restore from backup
cp data/backup_json/clients.json data/
cp data/backup_json/api_keys.json data/
cp data/backup_json/usage.json data/

# Revert client manager import
# Change back to: from src.core.client_manager import ClientManager
```

## Performance Optimization

### Indexes Created Automatically:
- `idx_api_keys_client_id` - Fast client lookups
- `idx_api_keys_api_key` - Fast API key validation
- `idx_usage_stats_client_id` - Fast usage queries
- `idx_documents_client_id` - Fast document queries
- `idx_documents_client_doc` - Fast document lookups

### Database Maintenance:

```bash
# Optimize database
python -c "
from src.core.database import Database
from src.core.config import settings
db = Database(settings.DATABASE_PATH)
with db.db_manager.get_connection() as conn:
    conn.execute('VACUUM')
    conn.execute('ANALYZE')
print('Database optimized!')
"
```

## Monitoring

### Database Size:
```bash
ls -lh data/chatbot_saas.db
```

### Query Performance:
```bash
# Enable query logging
export SQLITE_LOG=1
python main.py
```

### Backup Schedule:
```bash
# Add to crontab for daily backups
0 2 * * * cd /path/to/chatbot && python -c "from src.core.database import Database; Database().backup_database('./data/backup_$(date +%Y%m%d).db')"
```

## Next Steps

1. **Test thoroughly** with your existing data
2. **Monitor performance** for the first few days
3. **Set up automated backups**
4. **Consider database maintenance schedule**
5. **Update documentation** for your team

The migration to SQLite will significantly improve your application's reliability and performance! 🚀
