# Database Integration Documentation

## Overview

The Blood Test Analyzer now includes SQLite database integration for persistent storage of analysis results and user data. This implementation uses minimal code changes and provides optional database functionality that gracefully degrades when not available.

## Features

### Core Database Features
- ✅ **Persistent Analysis Storage** - All blood test analyses are automatically saved
- ✅ **User Management** - Optional user association with analyses
- ✅ **Analysis History** - Retrieve past analyses and results
- ✅ **System Statistics** - Track usage patterns and success rates
- ✅ **Blood Marker Extraction** - Automatic extraction of key markers for quick search
- ✅ **Graceful Degradation** - System works normally even if database is unavailable

### Database Models

#### 1. User Model
```python
class User(Base):
    id: String (UUID primary key)
    email: String (unique, optional)
    name: String (optional)
    created_at: DateTime
    last_analysis: DateTime
    total_analyses: Integer
    is_active: Boolean
```

#### 2. AnalysisResult Model
```python
class AnalysisResult(Base):
    id: String (UUID primary key)
    user_id: String (optional)
    job_id: String (for async processing)
    filename: String
    file_size: Integer
    query: Text
    analysis_result: Text (full analysis)
    summary: Text (brief summary)
    processing_time: Float
    status: String
    created_at: DateTime
    completed_at: DateTime
    markers_json: Text (extracted blood markers)
```

#### 3. SystemStats Model
```python
class SystemStats(Base):
    id: String (UUID primary key)
    date: DateTime
    total_analyses: Integer
    successful_analyses: Integer
    failed_analyses: Integer
    avg_processing_time: Float
    active_users: Integer
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install sqlalchemy==2.0.23 alembic==1.13.1
```

### 2. Database Initialization
The database is automatically initialized when the application starts. The SQLite database file (`blood_test_analyzer.db`) will be created in the application root directory.

### 3. File Structure
After setup, your project structure will include:
```
blood-test-analyser-debug/
├── main.py                    # Main FastAPI application (updated)
├── database.py                # Database models and operations (new)
├── database.md                # This documentation (new)
├── blood_test_analyzer.db     # SQLite database file (auto-created)
├── requirements.txt           # Updated with database dependencies
└── ... (other existing files)
```

## API Endpoints

### Analysis Endpoints (Enhanced)
All existing endpoints now automatically save results to the database:

- `POST /analyze` - Enhanced with database storage
- `POST /analyze-async` - Enhanced with database storage

**Enhanced Response Example:**
```json
{
    "status": "success",
    "request_id": "uuid-here",
    "analysis_id": "database-record-id",  // NEW: Database record ID
    "query": "user query",
    "analysis": "full analysis result",
    "processing_info": {
        "processing_time_seconds": 2.34,    // NEW: Actual processing time
        "file_size_bytes": 1024,
        "timestamp": 1640995200.0
    }
}
```

### New Database Endpoints

#### 1. Get Recent Analyses
```
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
            "summary": "Brief summary of analysis...",
            "created_at": "2024-01-01T12:00:00",
            "processing_time": 2.34,
            "status": "completed"
        }
    ]
}
```

#### 2. Get System Statistics
```
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
        "total_users": 25,
        "active_users": 20,
        "avg_processing_time": 2.45
    },
    "timestamp": 1640995200.0
}
```

#### 3. Enhanced Health Check
```
GET /health
```

Now includes database status:
```json
{
    "status": "healthy",
    "system_status": {
        "database": "operational",           // NEW: Database status
        "total_analyses": 150,              // NEW: Quick stat
        "queue_system": "available",
        "file_system": "accessible"
    }
}
```

## Database Operations

### Automatic Operations
- **Analysis Storage**: Every successful analysis is automatically saved
- **Marker Extraction**: Blood markers are extracted and stored for quick search
- **Statistics Tracking**: Usage statistics are automatically updated

### Manual Operations (via database.py)
```python
from database import get_db, create_user, get_recent_analyses, get_system_stats

# Get database session
db = get_db()

# Create a user (optional)
user = create_user(db, email="user@example.com", name="John Doe")

# Get recent analyses
analyses = get_recent_analyses(db, limit=10)

# Get system statistics
stats = get_system_stats(db)

# Always close the session
db.close()
```

## Blood Marker Extraction

The system automatically extracts common blood markers from analysis results:

### Supported Markers
- Glucose (mg/dL)
- Total Cholesterol (mg/dL)
- LDL Cholesterol (mg/dL)
- HDL Cholesterol (mg/dL)
- Triglycerides (mg/dL)
- Hemoglobin (g/dL)

### Storage Format
Markers are stored as JSON in the `markers_json` field:
```json
{
    "glucose": 95.0,
    "cholesterol": 185.0,
    "ldl": 110.0,
    "hdl": 55.0,
    "triglycerides": 120.0,
    "hemoglobin": 14.2
}
```

## Configuration

### Database URL
Default: `sqlite:///./blood_test_analyzer.db`

To use a different database, modify the `DATABASE_URL` in `database.py`:
```python
# For PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/blood_test_db"

# For MySQL
DATABASE_URL = "mysql://user:password@localhost/blood_test_db"
```

### Environment Variables
```bash
# Optional: Custom database URL
DATABASE_URL="sqlite:///./custom_path.db"
```

## Error Handling

### Graceful Degradation
- If database dependencies are missing, the system operates without persistence
- Database errors don't affect core analysis functionality
- All database operations include comprehensive error handling

### Error Scenarios
1. **Database Unavailable**: System logs warning and continues without persistence
2. **Connection Errors**: Individual operations fail gracefully with proper HTTP responses
3. **Validation Errors**: Invalid data is logged and skipped

## Performance Considerations

### SQLite Advantages
- **No Server Required**: File-based database, perfect for single-instance deployments
- **ACID Compliance**: Reliable data integrity
- **Low Overhead**: Minimal resource usage
- **Backup Friendly**: Single file can be easily backed up

### Optimization Tips
1. **Connection Management**: Database connections are properly opened and closed
2. **Index Usage**: Key fields are indexed for fast queries
3. **Batch Operations**: Consider batching for bulk operations
4. **Regular Cleanup**: Consider implementing data retention policies

## Migration & Backup

### Backup
```bash
# Simple file copy
cp blood_test_analyzer.db backup_$(date +%Y%m%d).db

# Using SQLite command
sqlite3 blood_test_analyzer.db ".backup backup.db"
```

### Data Export
```python
# Export to JSON
import json
from database import get_db, get_recent_analyses

db = get_db()
analyses = get_recent_analyses(db, limit=1000)
data = [{"id": a.id, "filename": a.filename, "created_at": a.created_at.isoformat()} for a in analyses]

with open("export.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Security Considerations

### Data Protection
- User emails and personal data are optional
- Analysis results are stored locally (not in cloud)
- No authentication system implemented (add as needed)

### Recommendations
1. **File Permissions**: Ensure database file has appropriate permissions
2. **Backup Encryption**: Encrypt backups if they contain sensitive data
3. **Access Control**: Consider adding authentication for production use
4. **Data Retention**: Implement policies for data cleanup

## Troubleshooting

### Common Issues

#### 1. Database Not Available
**Symptom**: `Database not available` errors
**Solution**: Install required dependencies:
```bash
pip install sqlalchemy==2.0.23 alembic==1.13.1
```

#### 2. Permission Errors
**Symptom**: Can't create database file
**Solution**: Check directory permissions:
```bash
chmod 755 ./blood-test-analyser-debug/
```

#### 3. Database Locked
**Symptom**: `database is locked` errors
**Solution**: Ensure all database connections are properly closed

#### 4. Missing Columns
**Symptom**: Column errors after updates
**Solution**: Delete existing database to recreate with new schema:
```bash
rm blood_test_analyzer.db
# Restart application to recreate
```

## Development & Testing

### Reset Database
```bash
rm blood_test_analyzer.db
python -c "from database import init_database; init_database()"
```

### Add Test Data
```python
from database import get_db, create_analysis_result

db = get_db()
create_analysis_result(
    db=db,
    filename="test.pdf",
    query="Test analysis",
    analysis_result="Test result",
    processing_time=1.0,
    file_size=1024
)
db.close()
```

## Future Enhancements

### Planned Features
1. **User Authentication**: JWT-based user system
2. **Advanced Search**: Search by markers, date ranges, etc.
3. **Data Visualization**: Charts for marker trends
4. **Export Features**: PDF reports, CSV exports
5. **Multi-tenancy**: Support for multiple organizations
6. **API Rate Limiting**: Usage controls per user
7. **Data Encryption**: Encrypt sensitive analysis data

### Migration Path
The current implementation is designed to be easily extensible. Future database schema changes can be managed using Alembic migrations.

---

## Async Analysis Integration

### Issue Resolution: Async Analyses Not Storing

**Problem**: Initially, async analyses (`POST /analyze-async`) were not being saved to the database, only synchronous analyses were stored.

**Root Cause**: The queue worker system (`queue_worker.py`) was processing async jobs but not integrating with the database storage.

**Solution**: Enhanced the queue worker with database integration:

#### Changes Made:

1. **Updated Queue Worker (`queue_worker.py`)**:
   ```python
   # Added database saving in process_job method
   try:
       from database import get_db, create_analysis_result, extract_blood_markers
       db = get_db()
       markers = extract_blood_markers(result)
       analysis_record = create_analysis_result(
           db=db,
           filename=job_data.get("filename", "unknown"),
           query=query,
           analysis_result=result,
           job_id=job_id,  # Links async job to database record
           processing_time=processing_time,
           file_size=job_data.get("file_size"),
           markers=markers
       )
       analysis_id = analysis_record.id
   except Exception as e:
       logger.warning(f"Failed to save async analysis to database: {e}")
   ```

2. **Enhanced `enqueue_analysis()` Function**:
   ```python
   def enqueue_analysis(file_path: str, query: str, filename: str, file_size: Optional[int] = None) -> str:
       job_data = {
           "file_path": file_path,
           "query": query,
           "filename": filename,
           "file_size": file_size  # NEW: Pass file size to worker
       }
   ```

3. **Updated Async Endpoint (`main.py`)**:
   ```python
   # Pass file size to queue worker
   job_id = enqueue_analysis(file_path, query, file.filename, len(content))
   ```

#### Async vs Sync Analysis Storage:

| Feature | Sync Analysis (`/analyze`) | Async Analysis (`/analyze-async`) |
|---------|---------------------------|-----------------------------------|
| **Database Storage** | ✅ Immediate | ✅ After processing completion |
| **Job ID Tracking** | ❌ Not applicable | ✅ `job_id` field populated |
| **Blood Marker Extraction** | ✅ Yes | ✅ Yes |
| **Processing Time** | ✅ Tracked | ✅ Tracked |
| **Analysis ID in Response** | ✅ Immediate | ✅ In job result |

#### Testing Async Database Integration:

1. **Submit Async Analysis**:
   ```bash
   curl -X POST \
     -F "file=@data/sample.pdf" \
     -F "query=Analyze my blood test" \
     http://localhost:8000/analyze-async
   ```

2. **Check Job Status**:
   ```bash
   curl http://localhost:8000/status/{job_id}
   ```

3. **Verify Database Storage**:
   ```bash
   curl http://localhost:8000/analyses/recent
   ```

#### Expected Async Response:
```json
{
  "status": "success",
  "query": "Analyze my blood test",
  "analysis": "Full analysis result...",
  "analysis_id": "database-record-uuid",  // NEW: Database record ID
  "processing_time": 2.34,
  "file_processed": "sample.pdf"
}
```

#### Database Record for Async Analysis:
```json
{
  "id": "analysis-uuid",
  "job_id": "queue-job-uuid",     // Links to async job
  "filename": "sample.pdf",
  "query": "Analyze my blood test",
  "status": "completed",
  "processing_time": 2.34,
  "created_at": "2024-01-01T12:00:00",
  "markers": {
    "glucose": 95.0,
    "cholesterol": 185.0
  }
}
```

### Benefits of Async Database Integration:

1. **Complete Analysis History**: Both sync and async analyses are now stored
2. **Job Tracking**: Async analyses can be linked back to their queue jobs
3. **Consistent Data**: Same marker extraction and storage for all analyses
4. **Performance Metrics**: Processing times tracked for both modes
5. **Graceful Degradation**: If database fails, async processing continues

## Quick Start Checklist

- [ ] Install database dependencies: `pip install sqlalchemy==2.0.23 alembic==1.13.1`
- [ ] Restart the application to initialize database
- [ ] Test with a synchronous blood test analysis: `POST /analyze`
- [ ] Test with an asynchronous blood test analysis: `POST /analyze-async`
- [ ] Check database status: `GET /health`
- [ ] View recent analyses (should show both sync and async): `GET /analyses/recent`
- [ ] Check system statistics: `GET /stats`

The database integration is now ready to use! All analyses (both synchronous and asynchronous) will be automatically saved and can be retrieved through the new API endpoints. 