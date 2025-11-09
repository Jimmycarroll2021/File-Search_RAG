# Google Gemini File Search RAG Application

A powerful Retrieval Augmented Generation (RAG) system built with Google's Gemini AI, designed specifically for sales/tender document management with advanced features for document search, analysis, and professional response generation.

## 🚀 Features

### ✅ Implemented (Phase 1 & 2)

#### Core Infrastructure
- **Modular Flask Architecture** - Blueprint-based design with service layer separation
- **SQLite Database** - SQLAlchemy ORM with models for stores, documents, prompts, queries, and settings
- **RESTful API** - Clean API endpoints with backward compatibility

#### Document Management
- **File Upload** - Single file upload with category detection
- **Multiple Format Support** - PDF, DOCX, TXT, MD, JSON, CSV, XLS, XLSX
- **File Search Stores** - Organized document storage with Gemini File Search API

#### User Interface
- **Modern Responsive Design** - Clean gradient UI with mobile/tablet/desktop support
- **Base Template System** - Reusable template architecture with CSS variables
- **Dark Mode** - Smooth theme toggle with localStorage persistence and system preference detection
- **Markdown Rendering** - Full GFM support with syntax highlighting via marked.js and highlight.js
- **Code Block Features** - Copy-to-clipboard buttons, language labels, responsive tables

#### AI Query Features
- **Response Modes** (5 modes tailored for sales/tender):
  - 📋 **Tender Response** - Formal, polished responses for submissions
  - ⚡ **Quick Answer** - Brief, bullet-point answers
  - 🔍 **Deep Analysis** - Detailed insights with citations
  - 🎯 **Strategy Advisor** - Recommendations and next steps
  - ✅ **Compliance Checklist** - Action items and requirements
- **System Prompts** - Mode-specific prompts with temperature control
- **Query History** - Track all queries for analytics

### 🚧 In Development (Phase 3 & 4)

#### Category Filtering System
- **9 Document Categories**:
  - 🛡️ Compliance (Security, PSPF, E8)
  - 📄 Contracts (Legal agreements)
  - 📊 Proposals (Tender responses)
  - 💰 Pricing (Quotes, budgets)
  - 📋 Requirements (RFPs, SOWs)
  - ⚙️ Technical (Technical docs)
  - 👤 CVs/Resumes (Team capabilities)
  - 📚 Policies (Internal policies)
  - 📁 Other (Miscellaneous)
- Multi-select category filtering
- Category-based document organization
- Auto-detection from file paths

#### Smart Prompts Library
- Pre-built prompts for common tender tasks
- CRUD operations for custom prompts
- Usage tracking and analytics
- One-click prompt application
- Categories: Tender Response, Pricing, Team Matching, Compliance, Strategy

#### Bulk Upload
- Directory scanning with recursive walk
- Auto-categorization from folder structure
- Batch processing (10 files at a time)
- Progress tracking
- Duplicate detection
- Target: 492 sales pipeline documents

#### Export Capabilities
- PDF generation with WeasyPrint
- DOCX generation with python-docx
- Markdown to formatted document conversion
- Professional styling with headers/footers
- Metadata inclusion (date, title, question)

#### Analytics Dashboard
- Document distribution by category
- Query activity trends
- Response mode usage statistics
- Category popularity metrics
- Performance tracking

## 📁 Project Structure

```
File-Search_RAG/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── database.py              # SQLAlchemy initialization
│   ├── models.py                # Database models
│   ├── routes/                  # API blueprints
│   │   ├── files.py            # Upload, store management
│   │   ├── query.py            # Query with response modes
│   │   ├── categories.py       # Category management
│   │   ├── prompts.py          # Smart prompts CRUD
│   │   └── export.py           # PDF/DOCX export
│   └── services/                # Business logic
│       ├── gemini_service.py   # Gemini API wrapper
│       ├── response_modes.py   # Mode configurations
│       ├── category_service.py # Category management
│       ├── prompt_service.py   # Prompt operations
│       ├── bulk_upload_service.py
│       └── export_service.py
├── templates/
│   ├── base.html               # Base template with theme support
│   ├── index.html              # Main application interface
│   └── components/             # Reusable UI components
│       ├── response_modes.html
│       ├── category_filter.html
│       ├── smart_prompts.html
│       └── bulk_upload.html
├── static/
│   ├── css/
│   │   ├── variables.css       # CSS variables (light/dark themes)
│   │   ├── dark-mode.css       # Dark theme overrides
│   │   └── components/         # Component-specific styles
│   ├── js/
│   │   ├── main.js             # Core application logic
│   │   ├── markdown-renderer.js # Markdown rendering
│   │   ├── theme-manager.js    # Dark mode toggle
│   │   ├── response-modes.js   # Mode selection
│   │   └── category-filter.js  # Category filtering
│   └── lib/                    # Third-party libraries
│       ├── marked.min.js       # Markdown parser
│       └── highlight.min.js    # Syntax highlighting
├── tests/                       # Test suite
│   ├── test_models.py          # Database model tests
│   ├── test_database.py        # Database initialization tests
│   ├── test_files_routes.py    # File routes tests
│   └── test_query_routes.py    # Query routes tests
├── instance/                    # SQLite database
├── uploads/                     # Temporary file storage
├── wsgi.py                      # Application entry point
├── config.py                    # Configuration management
├── init_db.py                   # Database initialization CLI
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not in repo)
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google AI API Key ([Get one here](https://aistudio.google.com/apikey))

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Jimmycarroll2021/File-Search_RAG.git
cd File-Search_RAG
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your-api-key-here
```

5. **Initialize database**
```bash
python init_db.py
```

6. **Run the application**
```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

## 🎯 Usage

### Upload Documents
1. Enter a store name (or use default)
2. Click or drag-and-drop files to upload
3. Wait for indexing to complete

### Ask Questions
1. Select a response mode (Tender, Quick, Analysis, Strategy, or Checklist)
2. Type your question in the text area
3. Click "Ask Question"
4. View the AI-generated response with markdown formatting

### Switch Theme
- Click the theme toggle button (☀️/🌙) in the header
- Your preference is saved automatically

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_query_routes.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

**Current Test Status:**
- ✅ Database Models: 18/18 passing
- ✅ Database Initialization: 8/8 passing
- ✅ Files Routes: 5/5 passing
- ✅ Query Routes (with modes): 8/8 passing
- **Total: 39 tests passing**

## 🔑 API Endpoints

### Files Management
```
POST   /api/files/create_store      # Create new file search store
POST   /api/files/upload_file       # Upload single file
GET    /api/files/list_stores       # List all stores
POST   /api/files/bulk_upload       # Bulk upload from directory
```

### Query
```
POST   /api/query/query             # Query with response mode
  Payload: {
    "question": "Your question here",
    "mode": "tender|quick|analysis|strategy|checklist",
    "store_name": "my-store"
  }
```

### Categories (In Development)
```
GET    /api/categories              # List all categories
GET    /api/categories/stats        # Document counts per category
```

### Smart Prompts (In Development)
```
GET    /api/prompts                 # List prompts
POST   /api/prompts                 # Create prompt
PUT    /api/prompts/<id>            # Update prompt
DELETE /api/prompts/<id>            # Delete prompt
POST   /api/prompts/<id>/use        # Increment usage count
```

### Export (In Development)
```
POST   /api/export/pdf              # Export response to PDF
POST   /api/export/docx             # Export response to DOCX
```

## 📊 Database Schema

### Core Tables
- **stores** - File search store metadata
- **documents** - Uploaded document tracking with categories
- **smart_prompts** - Reusable query templates
- **query_history** - Query analytics and history
- **user_settings** - Application settings

## 🎨 Response Modes Explained

### 📋 Tender Response Mode
- **Purpose:** Generate formal, polished content for tender submissions
- **Temperature:** 0.3 (focused, consistent)
- **Use For:** Compliance matrices, executive summaries, methodology sections
- **Output Style:** Structured sections with evidence references

### ⚡ Quick Answer Mode
- **Purpose:** Get immediate, concise answers
- **Temperature:** 0.5 (balanced)
- **Use For:** Simple queries, fact checking, quick lookups
- **Output Style:** Bullet points, under 200 words

### 🔍 Deep Analysis Mode
- **Purpose:** Comprehensive analysis across documents
- **Temperature:** 0.4 (focused but exploratory)
- **Use For:** Gap analysis, document summaries, pattern identification
- **Output Style:** Detailed sections with cross-references

### 🎯 Strategy Advisor Mode
- **Purpose:** Business strategy and recommendations
- **Temperature:** 0.6 (creative, strategic)
- **Use For:** Win strategies, competitive analysis, next steps
- **Output Style:** Strategic recommendations with rationale

### ✅ Compliance Checklist Mode
- **Purpose:** Extract and organize requirements
- **Temperature:** 0.2 (highly focused)
- **Use For:** Requirement extraction, compliance checklists, action items
- **Output Style:** Structured checklists with priorities

## 🔐 Security Notes

- API keys stored in `.env` (never commit to git)
- File uploads validated for type and size
- SQL injection protected via SQLAlchemy ORM
- XSS protection via markdown sanitization
- CORS configured for production use

## 🚀 Deployment

### Production Considerations
1. Use PostgreSQL instead of SQLite for production
2. Set up proper WSGI server (Gunicorn, uWSGI)
3. Configure nginx as reverse proxy
4. Enable HTTPS with SSL certificates
5. Set up rate limiting and caching
6. Configure proper logging
7. Use environment-specific configurations

## 📝 Development Status

### Phase 1: Foundation ✅ COMPLETE
- [x] Database setup with SQLAlchemy
- [x] Modular Flask architecture
- [x] Base template system with CSS variables
- [x] Dark mode implementation
- [x] Markdown rendering with syntax highlighting

### Phase 2: Core Features ✅ COMPLETE
- [x] Response modes (5 modes)
- [x] Mode-specific system prompts
- [x] Temperature control per mode
- [x] Query history tracking

### Phase 3: Advanced Features 🚧 IN PROGRESS
- [x] Category service backend
- [x] Smart prompts backend
- [x] Bulk upload backend
- [x] Export service backend
- [ ] Category filtering UI
- [ ] Smart prompts library UI
- [ ] Bulk upload UI
- [ ] Export UI (PDF/DOCX)

### Phase 4: Analytics & Polish 📋 PLANNED
- [ ] Analytics dashboard
- [ ] Document statistics
- [ ] Query analytics
- [ ] Usage metrics
- [ ] Performance optimization

### Phase 5: Production 📋 PLANNED
- [ ] Production deployment guide
- [ ] API documentation
- [ ] User guide
- [ ] Admin interface
- [ ] Backup/restore scripts

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google Gemini AI** - Powerful AI model and File Search API
- **marked.js** - Markdown rendering
- **highlight.js** - Syntax highlighting
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Email: [Your contact email]
- Documentation: See `/docs` folder

## 🔄 Version History

### v0.9.0 (Current - 2025-11-09)
- ✅ Phase 1 & 2 Complete
- ✅ Response modes system
- ✅ Dark mode with smooth transitions
- ✅ Markdown rendering with code highlighting
- ✅ Database architecture
- ✅ Modular Flask application
- 🚧 Backend for Phase 3 features (categories, prompts, bulk upload, export)
- 📋 UI components pending for Phase 3

### v1.0.0 (Target)
- Complete implementation of all features
- Production-ready deployment
- Comprehensive documentation
- Full test coverage

---

**Built with ❤️ for sales and tender professionals**
