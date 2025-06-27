# Blood Test Analyzer - Professional Medical Analysis System

A professional FastAPI application that provides evidence-based blood test analysis using AI agents with comprehensive error handling, database persistence, and concurrent processing capabilities.

## 🚀 Project Overview

This system provides professional blood test report analysis through multiple specialized AI agents:
- **Medical Laboratory Analyst** - Evidence-based blood test interpretation
- **Document Verification Specialist** - Medical document validation
- **Clinical Nutritionist** - Science-based nutritional guidance  
- **Exercise Physiologist** - Safe, progressive exercise recommendations

**Key Features:**
- ✅ Professional medical analysis with appropriate disclaimers
- ✅ Synchronous and asynchronous processing
- ✅ SQLite database for analysis persistence
- ✅ Redis-based queue system for concurrent requests
- ✅ Comprehensive error handling and validation
- ✅ File upload security (PDF-only, 10MB limit)
- ✅ Blood marker extraction and storage

---

## 🐛 Major Bug Fixes & Issues Resolved

### 1. **Python Version Compatibility**
- **Issue**: Dependencies incompatible with Python 3.13
- **Fix**: Switched to Python 3.10 with proper virtual environment setup

### 2. **Dependency Conflicts**
- **Issue**: Complex version conflicts in `requirements.txt`
- **Fix**: Created simplified `requirements_simple.txt` with essential packages

### 3. **Import Errors**
- **Issue**: Incorrect CrewAI tool imports (`SerperDevTool`, `@tool` decorator)
- **Fix**: Corrected import paths and tool definitions

### 4. **Agent Configuration Issues**
- **Issue**: Undefined LLM variables and inappropriate medical advice configurations
- **Fix**: Professional agent redesign with Google Gemini integration and evidence-based practices

### 5. **Tool Validation Errors**
- **Issue**: Pydantic validation failures with improperly defined tools
- **Fix**: Converted class-based tools to proper `@tool` decorated functions

### 6. **Performance & Rate Limiting**
- **Issue**: Severe API slowdowns due to `max_rpm=1` rate limiting
- **Fix**: Removed artificial rate limits, improved response times from 60+ seconds to 5-15 seconds

### 7. **Security & Error Handling**
- **Issue**: No file validation, poor error handling, potential crashes
- **Fix**: Comprehensive validation system, structured error responses, request tracking

### 8. **Medical Safety Compliance**
- **Issue**: Inappropriate and potentially harmful medical advice in original agents
- **Fix**: Complete replacement with professional medical standards and safety protocols

### 9. **Database Integration Issues**
- **Issue**: Async analyses not saving to database
- **Fix**: Enhanced queue worker with database integration for both sync and async processing

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+ (recommended for compatibility)
- Google API Key (for Gemini AI)
- Redis (optional, for queue system)

### Quick Start

1. **Clone and Navigate:**
   ```bash
   cd blood-test-analyser-debug
   ```

2. **Create Virtual Environment (Python 3.10):**
   ```bash
   # Create virtual environment with Python 3.10
   python3.10 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install python-multipart  # For file uploads
   
   # Optional: For queue system
   pip install redis==5.0.1
   
   # Optional: For database (auto-installs if missing)
   pip install sqlalchemy==2.0.23 alembic==1.13.1
   ```

4. **Configure Environment:**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
   ```

5. **Start Application:**
   ```bash
   python main.py
   ```

### Optional: Redis Queue System

For production workloads with concurrent processing:

```bash
# Install and start Redis
sudo apt install redis-server
sudo systemctl start redis-server

# Application will automatically detect and use Redis
python main.py
```

---

## 🏗️ System Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - RESTful API endpoints
   - File upload handling
   - Error management
   - Request validation

2. **AI Agent System** (`agents.py`, `task.py`)
   - Professional medical analysis agents
   - Evidence-based recommendations
   - Comprehensive disclaimers

3. **Database Layer** (`database.py`)
   - SQLite for analysis persistence
   - Blood marker extraction
   - User management (optional)
   - System statistics

4. **Queue System** (`queue_worker.py`)
   - Redis-based job processing
   - Async analysis handling
   - Fallback to in-memory queue

5. **Tools & Utilities** (`tools.py`)
   - PDF processing tools
   - Analysis utilities
   - Error handling

### Data Flow

```
Upload PDF → Validation → Analysis → Database Storage → Response
     ↓
[Sync] Direct processing → Immediate response
[Async] Queue job → Background processing → Status polling
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
- Google API key required in environment variables
- No user authentication (can be added for production)

### Endpoints

#### **Health Check**
```http
GET /
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Professional Blood Test Analyser",
  "version": "2.2.0",
  "system_status": {
    "database": "operational",
    "queue_system": "available",
    "file_system": "accessible"
  }
}
```

#### **Synchronous Analysis**
```http
POST /analyze
Content-Type: multipart/form-data

file: [PDF file, max 10MB]
query: "Please analyze my blood test results" [optional]
```

**Response:**
```json
{
  "status": "success",
  "request_id": "uuid-here",
  "analysis_id": "database-record-id",
  "query": "Please analyze my blood test results",
  "analysis": "Comprehensive medical analysis...",
  "processing_info": {
    "processing_time_seconds": 8.45,
    "file_size_bytes": 256000,
    "timestamp": 1640995200.0
  },
  "specialists_consulted": [
    "Medical Laboratory Analyst",
    "Document Verification Specialist", 
    "Clinical Nutritionist",
    "Exercise Physiologist"
  ],
  "disclaimer": "This analysis is for educational purposes only..."
}
```

#### **Asynchronous Analysis**
```http
POST /analyze-async
Content-Type: multipart/form-data

file: [PDF file, max 10MB]  
query: "Please analyze my blood test results" [optional]
```

**Response:**
```json
{
  "status": "queued",
  "job_id": "job-uuid-here",
  "request_id": "request-uuid-here",
  "message": "Analysis has been queued for processing",
  "status_url": "/status/job-uuid-here",
  "estimated_processing_time": "1-3 minutes"
}
```

#### **Job Status**
```http
GET /status/{job_id}
```

**Response (Completed):**
```json
{
  "job_id": "job-uuid-here",
  "status": "completed",
  "result": {
    "status": "success",
    "analysis_id": "database-record-id",
    "analysis": "Comprehensive medical analysis...",
    "processing_time": 12.34
  }
}
```

#### **Recent Analyses**
```http
GET /analyses/recent?limit=10
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "analyses": [
    {
      "id": "analysis-uuid",
      "filename": "blood_report.pdf",
      "query": "Analyze my blood test...",
      "summary": "Brief summary...",
      "created_at": "2024-01-01T12:00:00",
      "processing_time": 8.45,
      "status": "completed"
    }
  ]
}
```

#### **System Statistics**
```http
GET /stats
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_analyses": 150,
    "successful_analyses": 147,
    "failed_analyses": 3,
    "success_rate": 98.0,
    "avg_processing_time": 9.23
  }
}
```

#### **Queue Statistics**
```http
GET /queue/stats
```

**Response:**
```json
{
  "queue_enabled": true,
  "queue_length": 3,
  "backend": "redis",
  "status": "healthy"
}
```

### Error Responses

All errors return structured JSON with appropriate HTTP status codes:

```json
{
  "error": "Validation Error",
  "message": "File too large. Maximum size is 10.0MB",
  "type": "validation_error",
  "timestamp": 1640995200.0
}
```

**Common Error Codes:**
- `400` - Validation errors (file type, size, format)
- `500` - Processing errors (AI model, analysis failures)
- `503` - Service unavailable (database/queue system down)

---

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/

# API documentation
curl http://localhost:8000/docs

# Test file upload (sync)
curl -X POST -F "file=@data/sample.pdf" -F "query=Analyze this report" \
  http://localhost:8000/analyze

# Test file upload (async)
curl -X POST -F "file=@data/sample.pdf" -F "query=Analyze this report" \
  http://localhost:8000/analyze-async

# Check recent analyses
curl http://localhost:8000/analyses/recent

# System statistics
curl http://localhost:8000/stats
```

### Validation Tests
```bash
# Test invalid file type
curl -X POST -F "file=@invalid.txt" http://localhost:8000/analyze

# Test oversized file (should return 400 error)
curl -X POST -F "file=@large_file.pdf" http://localhost:8000/analyze
```

### Performance Testing
- **Expected Response Time**: 5-15 seconds for sync analysis
- **Concurrent Requests**: Supported via async endpoint + Redis queue
- **File Size Limit**: 10MB per upload
- **Database**: Auto-created SQLite file for persistence

---

## 📖 Documentation References

- **Database Integration**: See [database.md](database.md) for complete database features
- **Queue System Setup**: See [QUEUE_SETUP.md](QUEUE_SETUP.md) for production deployment
- **Bug Fix History**: See [fix.md](fix.md) for detailed bug resolution documentation

---

## 🛠️ Technical Specifications

- **Framework**: FastAPI 0.110.3
- **AI**: CrewAI 0.130.0 with Google Gemini 1.5 Flash
- **Database**: SQLite with SQLAlchemy 2.0.23
- **Queue**: Redis 5.0.1 (optional)
- **Python**: 3.10+
- **File Support**: PDF only, 10MB max
- **Response Format**: JSON
- **Error Handling**: Comprehensive validation and logging

---

*Professional Blood Test Report Analyser v2.2.0 - Enhanced with Database Integration and Concurrent Processing*
