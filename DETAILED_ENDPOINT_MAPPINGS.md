# Detailed API Endpoint Mappings - Google Gemini File Search

## Complete Endpoint Verification

### 1. Query Endpoint

**Backend Definition:**
```python
# app/routes/query.py
query_bp = Blueprint('query', __name__, url_prefix='/api/query')

@query_bp.route('/query', methods=['POST'])
def query():
    # Query implementation
```

**Frontend Usage:**
```javascript
// static/js/main.js - Line 158
const response = await fetch('/api/query/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        question: question,
        store_name: storeName.value,
        mode: window.selectedMode || 'quick'
    })
});
```

**Full Endpoint Path:** `/api/query/query`  
**HTTP Method:** POST  
**Status:** ✓ CORRECT

---

### 2. Single File Upload Endpoint

**Backend Definition:**
```python
# app/routes/files.py
files_bp = Blueprint('files', __name__, url_prefix='/api/files')

@files_bp.route('/upload_file', methods=['POST'])
def upload_file():
    # Upload implementation
```

**Frontend Usage:**
```javascript
// static/js/main.js - Line 109
const response = await fetch('/api/files/upload_file', {
    method: 'POST',
    body: formData  // FormData with file and store_name
});
```

**Full Endpoint Path:** `/api/files/upload_file`  
**HTTP Method:** POST  
**Request Body:** FormData with 'file' and 'store_name'  
**Status:** ✓ CORRECT

---

### 3. Bulk Upload Endpoint

**Backend Definition:**
```python
# app/routes/files.py
files_bp = Blueprint('files', __name__, url_prefix='/api/files')

@files_bp.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    # Bulk upload implementation
```

**Frontend Usage (Scan):**
```javascript
// static/js/bulk-upload.js - Line 81
const response = await fetch('/api/files/bulk_upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        source_directory: sourceDirectory,
        auto_categorize: autoCategorize,
        scan_only: true
    })
});
```

**Frontend Usage (Upload):**
```javascript
// static/js/bulk-upload.js - Line 201
const response = await fetch('/api/files/bulk_upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        source_directory: sourceDirectory,
        store_name: storeName,
        auto_categorize: autoCategorize,
        batch_size: batchSize
    })
});
```

**Full Endpoint Path:** `/api/files/bulk_upload`  
**HTTP Method:** POST  
**Request Body:** JSON with source_directory, store_name, auto_categorize, batch_size, scan_only  
**Status:** ✓ CORRECT

---

### 4. List Stores Endpoint

**Backend Definition:**
```python
# app/routes/files.py
files_bp = Blueprint('files', __name__, url_prefix='/api/files')

@files_bp.route('/list_stores', methods=['GET'])
def list_stores():
    # List stores implementation
```

**Frontend Usage:**
```javascript
// static/js/bulk-upload.js - Line 361
const response = await fetch('/api/files/list_stores');
```

**Full Endpoint Path:** `/api/files/list_stores`  
**HTTP Method:** GET  
**Query Parameters:** None  
**Status:** ✓ CORRECT

---

### 5. List Categories Endpoint

**Backend Definition:**
```python
# app/routes/categories.py
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('/', methods=['GET'])
def list_categories():
    # List categories implementation
```

**Frontend Usage:**
```javascript
// static/js/category-filter.js - Line 55
const response = await fetch('/api/categories');
```

**Full Endpoint Path:** `/api/categories`  
**HTTP Method:** GET  
**Status:** ✓ CORRECT

---

### 6. Category Statistics Endpoint

**Backend Definition:**
```python
# app/routes/categories.py
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('/stats', methods=['GET'])
def category_statistics():
    # Category stats implementation
```

**Frontend Usage:**
```javascript
// static/js/category-filter.js - Line 75
const response = await fetch('/api/categories/stats');
```

**Full Endpoint Path:** `/api/categories/stats`  
**HTTP Method:** GET  
**Status:** ✓ CORRECT

---

## Summary Table

| Feature | Frontend Endpoint | Backend Route | Method | Status |
|---------|------------------|---------------|--------|--------|
| Query Question | `/api/query/query` | `/api/query` + `/query` | POST | ✓ |
| Upload Single File | `/api/files/upload_file` | `/api/files` + `/upload_file` | POST | ✓ |
| Bulk Upload | `/api/files/bulk_upload` | `/api/files` + `/bulk_upload` | POST | ✓ |
| List Stores | `/api/files/list_stores` | `/api/files` + `/list_stores` | GET | ✓ |
| Get Categories | `/api/categories` | `/api/categories` + `/` | GET | ✓ |
| Category Stats | `/api/categories/stats` | `/api/categories` + `/stats` | GET | ✓ |

## Route Registration Verification

Flask application registers all blueprints in `app/__init__.py`:

```python
from app.routes.files import files_bp, load_stores_from_database
from app.routes.query import query_bp
from app.routes.categories import categories_bp
from app.routes.prompts import prompts_bp
from app.routes.export import export_bp

app.register_blueprint(files_bp)      # /api/files
app.register_blueprint(query_bp)      # /api/query
app.register_blueprint(categories_bp) # /api/categories
app.register_blueprint(prompts_bp)    # /api/prompts
app.register_blueprint(export_bp)     # /api/export
```

## Request/Response Examples

### Query Endpoint

**Request:**
```json
POST /api/query/query HTTP/1.1
Content-Type: application/json

{
  "question": "What are the key compliance requirements?",
  "store_name": "my-file-search-store",
  "mode": "quick"
}
```

**Response (Success):**
```json
{
  "success": true,
  "answer": "...",
  "question": "What are the key compliance requirements?",
  "mode": "quick",
  "mode_name": "Quick Answer",
  "mode_icon": "⚡"
}
```

### Upload File Endpoint

**Request:**
```
POST /api/files/upload_file HTTP/1.1
Content-Type: multipart/form-data

[Binary file data]
file: [file contents]
store_name: my-file-search-store
```

**Response (Success):**
```json
{
  "success": true,
  "message": "File \"document.pdf\" uploaded and indexed successfully",
  "store_name": "my-file-search-store",
  "category": "document",
  "document_id": 1
}
```

### Bulk Upload Endpoint (Scan)

**Request:**
```json
POST /api/files/bulk_upload HTTP/1.1
Content-Type: application/json

{
  "source_directory": "/path/to/documents",
  "auto_categorize": true,
  "scan_only": true
}
```

**Response (Success):**
```json
{
  "success": true,
  "total": 15,
  "files": [...],
  "category_distribution": {
    "document": 10,
    "image": 5
  }
}
```

### Bulk Upload Endpoint (Upload)

**Request:**
```json
POST /api/files/bulk_upload HTTP/1.1
Content-Type: application/json

{
  "source_directory": "/path/to/documents",
  "store_name": "my-file-search-store",
  "auto_categorize": true,
  "batch_size": 10
}
```

**Response (Success):**
```json
{
  "success": true,
  "total": 15,
  "success_count": 14,
  "failed_count": 1,
  "skipped_count": 0,
  "files": [...],
  "category_distribution": {...},
  "message": "Uploaded 14 files successfully"
}
```

### List Stores Endpoint

**Request:**
```
GET /api/files/list_stores HTTP/1.1
```

**Response (Success):**
```json
{
  "success": true,
  "stores": [
    {
      "id": 1,
      "name": "my-file-search-store",
      "gemini_store_id": "fs_...",
      "display_name": "My File Search Store",
      "created_at": "2025-11-14T10:00:00"
    }
  ]
}
```

## Conclusion

All API endpoints are correctly implemented and referenced:
- Backend routes properly defined with correct URL prefixes
- Frontend fetch calls use correct full endpoint paths
- All HTTP methods match (GET/POST)
- Request/response formats are compatible
- Error handling is implemented on both sides

**No endpoint URL modifications are required.**

---

**Last Updated:** 2025-11-14  
**Status:** ✓ All Endpoints Verified and Correct
