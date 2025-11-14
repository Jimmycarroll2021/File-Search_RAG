# Quick Start Guide - Google File Search Application

## Database Fix Status: ✅ COMPLETE

All database issues have been resolved. The application is ready to use!

## What Was Fixed

1. **Database Tables Initialized** - All 5 required tables created
2. **Auto-Initialization Added** - Tables auto-create on server startup
3. **Database Persistence** - Stores and documents now save to database
4. **Store Loading** - Existing stores load from database on startup

## Running the Application

### 1. Start the Server

```bash
python wsgi.py
```

The server will start at: http://127.0.0.1:5000

You should see:
```
[INFO] Database tables initialized
[INFO] Loaded X stores from database
```

### 2. Access the Web Interface

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## API Usage

### Create a Store

```bash
curl -X POST http://127.0.0.1:5000/api/files/create_store \
  -H "Content-Type: application/json" \
  -d '{"store_name": "my_documents", "display_name": "My Documents"}'
```

**Response:**
```json
{
  "success": true,
  "store_name": "fileSearchStores/mydocuments-xxxxx",
  "message": "File search store \"my_documents\" created successfully"
}
```

### List Stores

```bash
curl http://127.0.0.1:5000/api/files/list_stores
```

**Response:**
```json
{
  "success": true,
  "stores": [
    {
      "id": 1,
      "name": "my_documents",
      "display_name": "My Documents",
      "gemini_store_id": "fileSearchStores/mydocuments-xxxxx",
      "created_at": "2025-11-14T08:00:00.000000",
      "document_count": 0
    }
  ]
}
```

### Upload a File

```bash
curl -X POST http://127.0.0.1:5000/api/files/upload_file \
  -F "file=@/path/to/document.pdf" \
  -F "store_name=my_documents" \
  -F "category=finance"
```

**Response:**
```json
{
  "success": true,
  "message": "File \"document.pdf\" uploaded and indexed successfully",
  "store_name": "my_documents",
  "category": "finance",
  "document_id": 1
}
```

### Query Documents

```bash
curl -X POST http://127.0.0.1:5000/api/query/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main points in this document?",
    "store_name": "my_documents",
    "response_mode": "comprehensive"
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Based on the documents...",
  "sources": [...]
}
```

## Backward Compatible Routes

The following routes work without the `/api` prefix:

- `POST /create_store` → Same as `/api/files/create_store`
- `POST /upload_file` → Same as `/api/files/upload_file`
- `GET /list_stores` → Same as `/api/files/list_stores`
- `POST /query` → Same as `/api/query/query`

**Example:**
```bash
curl http://127.0.0.1:5000/list_stores
```

## Database Information

**Location:** `C:\ai tools\Google_File Search\instance\app.db`

**Tables:**
- `stores` - File search store metadata
- `documents` - Uploaded document tracking with categories
- `smart_prompts` - Reusable query templates
- `query_history` - Analytics and query history
- `user_settings` - Application settings

**View Database:**
```bash
sqlite3 instance/app.db
```

```sql
-- List all stores
SELECT * FROM stores;

-- List all documents
SELECT * FROM documents;

-- Get document count by category
SELECT category, COUNT(*) as count
FROM documents
GROUP BY category;
```

## Verification

To verify everything is working:

```bash
python verify_database_fix.py
```

This will check:
- ✅ Database file exists
- ✅ All tables exist
- ✅ Tables can be queried
- ✅ App initialization works
- ✅ API endpoints are functional

## Troubleshooting

### Issue: "no such table" errors

**Solution:** Run the initialization script:
```bash
python init_db.py
```

### Issue: Stores not persisting

**Solution:** The fix ensures stores are saved to database. If you created stores before the fix, they won't be in the database. Create them again:
```bash
curl -X POST http://127.0.0.1:5000/api/files/create_store \
  -H "Content-Type: application/json" \
  -d '{"store_name": "my_store", "display_name": "My Store"}'
```

### Issue: Server won't start

**Solution:** Check that all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Upload Your Documents**
   - Use the web interface at http://127.0.0.1:5000
   - Or use the API endpoints above

2. **Categorize Your Documents**
   - Categories auto-detect from file paths
   - Or manually specify with `category` parameter

3. **Query Your Documents**
   - Use natural language questions
   - Filter by category if needed
   - Choose response mode: `precise`, `comprehensive`, or `creative`

4. **Explore Advanced Features**
   - Smart Prompts for reusable queries
   - Query History for analytics
   - Bulk Upload for directories
   - Category Management

## Support Files

- `DATABASE_FIX_SUMMARY.md` - Detailed technical summary of fixes
- `verify_database_fix.py` - Verification script
- `test_database.py` - Database connectivity tests
- `init_db.py` - Manual database initialization script

## Configuration

**Environment Variables:**
- `GOOGLE_API_KEY` - Your Gemini API key (required)
- `DEV_DATABASE_URL` - Custom database URL (optional)

**Database Configuration:**
- Location: `config.py`
- Development: SQLite (`instance/app.db`)
- Production: Configurable via environment

## Summary

✅ Database initialized with all tables
✅ Auto-initialization on startup
✅ Stores persist to database
✅ Documents tracked in database
✅ API endpoints working
✅ Backward compatibility maintained

**The application is ready for production use!**
