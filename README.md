# 🩸 Blood Test Analyzer - Professional Medical Analysis System

A professional system that provides evidence-based blood test analysis using an optimized AI agent, with a FastAPI backend and a user-friendly Streamlit frontend.

## 🚀 Project Overview

This system provides professional blood test analysis through a single, optimized AI agent. It uses CrewAI for orchestration, FastAPI for the backend API, and Streamlit for the user interface.

**Key Features:**
- ✅ **Optimized AI Agent:** A single, comprehensive agent for efficient and fast analysis.
- ✅ **FastAPI Backend:** A robust API for handling file uploads, analysis, and data persistence.
- ✅ **Streamlit Frontend:** An interactive and user-friendly web interface for seamless user interaction.
- ✅ **Database Persistence:** SQLite database for storing analysis results and system statistics.
- ✅ **Secure & Validated:** Comprehensive error handling, file validation, and security protocols.
- ✅ **Asynchronous Support:** Redis-based queue system for handling concurrent, long-running tasks.

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
- Python 3.10+
- Google API Key (for Gemini AI)
- Redis (optional, for the async queue)

### Quick Start

1.  **Clone and Navigate:**
    ```bash
    cd blood-test-analyser-debug
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3.10 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file and add your Google API key:
    ```bash
    echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
    ```

5.  **Start the Backend Server:**
    ```bash
    python main.py
    ```
    The API will be available at `http://localhost:8000`.

6.  **Start the Streamlit Frontend:**
    In a **new terminal**, run the frontend application:
    ```bash
    streamlit run streamlit_app.py
    ```
    The web interface will be available at `http://localhost:8501`.

---

## ✨ Streamlit Frontend

The project includes an interactive web interface built with Streamlit, providing a seamless user experience.

**Frontend Features:**
-   **File Upload:** Easily upload your PDF blood test reports.
-   **Text-Based Analysis:** Get medical insights without needing to upload a file.
-   **Live System Status:** A sidebar shows the real-time health of the backend API.
-   **Recent Analyses:** View a list of recently completed analyses.
-   **Professionally Formatted Output:** Analysis results are displayed in a clean, readable format.

See `STREAMLIT_README.md` for more details on the frontend.

---

## 🏗️ System Architecture

### Core Components

1.  **FastAPI Backend** (`main.py`):
    -   Manages RESTful API endpoints, file uploads, and request validation.
2.  **AI Agent System** (`agents.py`, `task.py`):
    -   Powered by CrewAI, orchestrates the comprehensive analysis task.
3.  **Streamlit Frontend** (`streamlit_app.py`):
    -   Provides the user interface for interacting with the system.
4.  **Database Layer** (`database.py`):
    -   Uses SQLite for persisting analysis results and system stats.
5.  **Queue System** (`queue_worker.py`):
    -   Optional Redis-based queue for asynchronous processing of tasks.

---

## 📚 API Documentation

The full API documentation is automatically generated by FastAPI and is available at:

-   **Swagger UI:** `http://localhost:8000/docs`
-   **ReDoc:** `http://localhost:8000/redoc`

### Key API Endpoints
- `GET /health`: Checks the health of the API.
- `POST /analyze`: Submits a blood test PDF for synchronous analysis.
- `POST /analyze-async`: Submits a blood test PDF for asynchronous analysis.
- `POST /analyze-text`: Submits a text query for analysis.
- `GET /analyses/recent`: Retrieves a list of recent analyses.
- `GET /status/{job_id}`: Checks the status of an asynchronous job.

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

*This project has been significantly refactored and optimized for performance, security, and professional-grade output.*
