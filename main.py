from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import asyncio
import logging
import mimetypes
import json
from typing import Optional
from pathlib import Path
import time

from crewai import Crew, Process
from agents import comprehensive_analyst
from task import comprehensive_blood_analysis

# Configure logging first (before database imports)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blood_test_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database imports (with error handling for development)
try:
    from database import (
        get_db, create_analysis_result, get_analysis_by_job_id, 
        get_recent_analyses, get_system_stats, extract_blood_markers,
        create_user, get_user_by_email, init_database, AnalysisResult
    )
    from sqlalchemy.orm import Session
    DATABASE_ENABLED = True
    logger.info("Database functionality enabled")
except ImportError as e:
    logger.warning(f"Database not available, running without persistence: {e}")
    DATABASE_ENABLED = False

# Initialize database if available
if DATABASE_ENABLED:
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        DATABASE_ENABLED = False

# Import queue worker system
try:
    from queue_worker import enqueue_analysis, get_analysis_status, get_queue_stats, start_background_worker
    QUEUE_ENABLED = True
    logger.info("Queue worker system available")
except ImportError as e:
    logger.warning(f"Queue system not available: {e}")
    QUEUE_ENABLED = False

app = FastAPI(
    title="Professional Blood Test Report Analyser",
    description="Professional medical analysis system with concurrent processing",
    version="2.2.0"
)

# Configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf'}
DATA_DIR = "data"

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass

def validate_uploaded_file(file: UploadFile) -> None:
    """Validate uploaded file format and size"""
    logger.info(f"Validating uploaded file: {file.filename}")
    
    # Check if file exists
    if not file.filename:
        raise ValidationError("No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Invalid file type. Only PDF files are allowed. Got: {file_ext}")
    
    # Check MIME type if available
    if file.content_type and not file.content_type.startswith('application/pdf'):
        logger.warning(f"Unexpected MIME type: {file.content_type} for file: {file.filename}")
    
    # Check file size (this is approximate since we haven't read the content yet)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    logger.info(f"File validation passed for: {file.filename}")

def validate_file_content(content: bytes, filename: str) -> None:
    """Validate file content after reading"""
    logger.info(f"Validating file content for: {filename}")
    
    # Check actual file size
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    # Check for basic PDF structure
    if not content.startswith(b'%PDF-'):
        raise ValidationError("Invalid PDF file format. File does not contain PDF header.")
    
    # Check minimum file size (empty or corrupted PDFs)
    if len(content) < 100:
        raise ValidationError("File appears to be corrupted or empty")
    
    logger.info(f"File content validation passed for: {filename}")

def safe_file_cleanup(file_path: str) -> None:
    """Safely clean up uploaded file with comprehensive error handling"""
    if not file_path or not os.path.exists(file_path):
        return
    
    try:
        os.remove(file_path)
        logger.info(f"Successfully cleaned up file: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied when trying to delete file: {file_path}")
    except OSError as e:
        logger.error(f"OS error when trying to delete file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error when trying to delete file {file_path}: {e}")

def run_comprehensive_analysis(query: str, file_path: str = "data/sample.pdf") -> str:
    """Run comprehensive blood test analysis with single professional call and error handling"""
    logger.info(f"Starting comprehensive analysis for query: {query[:50]}...")
    
    try:
        medical_crew = Crew(
            agents=[comprehensive_analyst],
            tasks=[comprehensive_blood_analysis],
            process=Process.sequential,
            verbose=True
        )
        
        start_time = time.time()
        result = medical_crew.kickoff({'query': query})
        processing_time = time.time() - start_time
        
        logger.info(f"Analysis completed successfully in {processing_time:.2f} seconds")
        return str(result)
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise ProcessingError(f"Analysis failed: {str(e)}")

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle validation errors with proper HTTP responses"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "type": "validation_error",
            "timestamp": time.time()
        }
    )

@app.exception_handler(ProcessingError)
async def processing_exception_handler(request, exc: ProcessingError):
    """Handle processing errors with proper HTTP responses"""
    logger.error(f"Processing error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Processing Error",
            "message": str(exc),
            "type": "processing_error",
            "timestamp": time.time()
        }
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    features = [
        "Single comprehensive medical analysis (optimized performance)",
        "Evidence-based blood test interpretation",
        "Professional nutritional guidance", 
        "Safe exercise recommendations",
        "Document verification and quality assessment",
        "Medical disclaimers and safety protocols",
        "Comprehensive error handling and validation"
    ]
    
    if QUEUE_ENABLED:
        features.append("Concurrent request processing")
        features.append("Queue-based analysis")
    
    return {
        "message": "Professional Blood Test Report Analyser API is running",
        "version": "2.2.0 - Concurrent Processing",
        "features": features,
        "processing_modes": {
            "synchronous": "/analyze",
            "asynchronous": "/analyze-async" if QUEUE_ENABLED else "not_available"
        },
        "upload_limits": {
            "max_file_size_mb": MAX_FILE_SIZE / (1024*1024),
            "allowed_formats": list(ALLOWED_EXTENSIONS)
        }
    }

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Please provide a comprehensive analysis of my blood test results")
):
    """Analyze blood test report with comprehensive error handling and validation"""
    
    file_path = None
    request_id = str(uuid.uuid4())
    logger.info(f"Analysis request {request_id} started for file: {file.filename}")
    
    try:
        # Step 1: Validate uploaded file
        validate_uploaded_file(file)
        
        # Step 2: Read and validate file content
        content = await file.read()
        validate_file_content(content, file.filename)
        
        # Step 3: Setup file storage
        os.makedirs(DATA_DIR, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = f"{DATA_DIR}/blood_test_report_{file_id}.pdf"
        
        # Step 4: Save file securely
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logger.info(f"File saved successfully: {file_path}")
        except OSError as e:
            raise ProcessingError(f"Failed to save uploaded file: {e}")
        
        # Step 5: Validate and clean query
        if not query or query.strip() == "":
            query = "Please provide a comprehensive analysis of my blood test results"
        query = query.strip()
        
        if len(query) > 1000:
            raise ValidationError("Query too long. Maximum 1000 characters allowed.")
        
        # Step 6: Process the blood report
        start_time = time.time()
        try:
            response = run_comprehensive_analysis(query=query, file_path=file_path)
        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            raise ProcessingError(f"Analysis service error: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Step 7: Save analysis to database if enabled
        analysis_id = None
        if DATABASE_ENABLED:
            try:
                db = get_db()
                markers = extract_blood_markers(response)
                analysis_record = create_analysis_result(
                    db=db,
                    filename=file.filename,
                    query=query,
                    analysis_result=response,
                    processing_time=processing_time,
                    file_size=len(content),
                    markers=markers
                )
                analysis_id = analysis_record.id
                db.close()
                logger.info(f"Analysis saved to database with ID: {analysis_id}")
            except Exception as e:
                logger.error(f"Failed to save analysis to database: {e}")
        
        logger.info(f"Analysis request {request_id} completed successfully")
        
        response_data = {
            "status": "success",
            "request_id": request_id,
            "query": query,
            "analysis": response,
            "file_processed": file.filename,
            "analysis_type": "comprehensive_medical_review",
            "analysis_approach": "Single comprehensive professional analysis (optimized)",
            "specialties_covered": [
                "Medical Laboratory Analysis",
                "Document Verification & Quality Assessment", 
                "Evidence-Based Clinical Nutrition",
                "Exercise Physiology & Safety"
            ],
            "processing_info": {
                "file_size_bytes": len(content),
                "processing_time_seconds": processing_time,
                "timestamp": time.time()
            },
            "disclaimer": "This analysis is for educational purposes only. Always consult with qualified healthcare professionals for medical decisions."
        }
        
        if analysis_id:
            response_data["analysis_id"] = analysis_id
            
        return response_data
        
    except ValidationError:
        # ValidationError is handled by the exception handler
        raise
    except ProcessingError:
        # ProcessingError is handled by the exception handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_blood_report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request",
                "request_id": request_id,
                "timestamp": time.time()
            }
        )
    
    finally:
        # Step 7: Always clean up uploaded file
        if file_path:
            safe_file_cleanup(file_path)

@app.post("/analyze-async")
async def analyze_blood_report_async(
    file: UploadFile = File(...),
    query: str = Form(default="Please provide a comprehensive analysis of my blood test results")
):
    """Queue blood test analysis for asynchronous processing"""
    
    if not QUEUE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Queue system not available. Use /analyze for synchronous processing."
        )
    
    file_path = None
    request_id = str(uuid.uuid4())
    logger.info(f"Async analysis request {request_id} started for file: {file.filename}")
    
    try:
        # Step 1: Validate uploaded file
        validate_uploaded_file(file)
        
        # Step 2: Read and validate file content
        content = await file.read()
        validate_file_content(content, file.filename)
        
        # Step 3: Setup file storage
        os.makedirs(DATA_DIR, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = f"{DATA_DIR}/blood_test_report_{file_id}.pdf"
        
        # Step 4: Save file securely
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logger.info(f"File saved successfully: {file_path}")
        except OSError as e:
            raise ProcessingError(f"Failed to save uploaded file: {e}")
        
        # Step 5: Validate query
        if not query or query.strip() == "":
            query = "Please provide a comprehensive analysis of my blood test results"
        query = query.strip()
        
        if len(query) > 1000:
            raise ValidationError("Query too long. Maximum 1000 characters allowed.")
        
        # Step 6: Enqueue for processing
        job_id = enqueue_analysis(file_path, query, file.filename, len(content))
        
        logger.info(f"Analysis job {job_id} enqueued for request {request_id}")
        
        return {
            "status": "queued",
            "job_id": job_id,
            "request_id": request_id,
            "message": "Comprehensive analysis has been queued for processing (optimized single-call approach)",
            "status_url": f"/status/{job_id}",
            "estimated_processing_time": "30 seconds - 2 minutes (optimized)",
            "file_processed": file.filename,
            "processing_info": {
                "file_size_bytes": len(content),
                "timestamp": time.time(),
                "mode": "asynchronous_optimized"
            }
        }
        
    except ValidationError:
        # Clean up file if validation fails
        if file_path and os.path.exists(file_path):
            safe_file_cleanup(file_path)
        raise
    except ProcessingError:
        # Clean up file if processing setup fails
        if file_path and os.path.exists(file_path):
            safe_file_cleanup(file_path)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_blood_report_async: {e}")
        # Clean up file on unexpected error
        if file_path and os.path.exists(file_path):
            safe_file_cleanup(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while queuing your request",
                "request_id": request_id,
                "timestamp": time.time()
            }
        )

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of queued analysis job"""
    
    if not QUEUE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Queue system not available"
        )
    
    try:
        job_status = get_analysis_status(job_id)
        
        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        response = {
            "job_id": job_id,
            "status": job_status.get("status", "unknown"),
            "created_at": job_status.get("created_at"),
            "updated_at": job_status.get("updated_at")
        }
        
        # Add result if completed
        if job_status.get("status") == "completed" and job_status.get("result"):
            response["result"] = json.loads(job_status["result"])
        
        # Add error if failed
        if job_status.get("status") == "failed" and job_status.get("error"):
            response["error"] = job_status["error"]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job status: {str(e)}"
        )

@app.get("/queue/stats")
async def get_queue_statistics():
    """Get queue system statistics"""
    
    if not QUEUE_ENABLED:
        return {
            "queue_enabled": False,
            "message": "Queue system not available"
        }
    
    try:
        stats = get_queue_stats()
        stats["queue_enabled"] = True
        return stats
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        return {
            "queue_enabled": True,
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Extended health check with system status"""
    logger.info("Extended health check accessed")
    
    try:
        # Check data directory
        data_dir_status = "accessible" if os.path.exists(DATA_DIR) and os.access(DATA_DIR, os.W_OK) else "inaccessible"
        
        # Check log file
        log_file_status = "active" if os.path.exists("blood_test_analyzer.log") else "not_found"
        
        system_status = {
            "data_directory": data_dir_status,
            "logging": log_file_status,
            "error_handling": "comprehensive",
            "file_validation": "active"
        }
        
        # Add database status if available
        if DATABASE_ENABLED:
            try:
                db = get_db()
                stats = get_system_stats(db)
                db.close()
                system_status["database"] = "operational"
                system_status["total_analyses"] = stats.get("total_analyses", 0)
            except:
                system_status["database"] = "error"
        else:
            system_status["database"] = "disabled"
        
        # Add queue status if available
        if QUEUE_ENABLED:
            try:
                queue_stats = get_queue_stats()
                system_status["queue_system"] = queue_stats.get("status", "unknown")
                system_status["queue_backend"] = queue_stats.get("backend", "unknown")
                system_status["queue_length"] = queue_stats.get("queue_length", 0)
            except:
                system_status["queue_system"] = "error"
        else:
            system_status["queue_system"] = "disabled"
        
        return {
            "status": "healthy",
            "service": "Professional Blood Test Analyser",
            "version": "2.2.0",
            "medical_compliance": "Professional medical analysis with appropriate disclaimers",
            "agents_status": "Comprehensive medical professional (optimized single-agent approach)",
            "safety_protocols": "Active - Evidence-based analysis only",
            "processing_modes": {
                "synchronous": "available",
                "asynchronous": "available" if QUEUE_ENABLED else "disabled"
            },
            "system_status": system_status,
            "limits": {
                "max_file_size_mb": MAX_FILE_SIZE / (1024*1024),
                "allowed_formats": list(ALLOWED_EXTENSIONS)
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Database endpoints
@app.get("/analyses/recent")
async def get_recent_analyses_endpoint(limit: int = 10):
    """Get recent analysis results"""
    if not DATABASE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        db = get_db()
        analyses = get_recent_analyses(db, limit=limit)
        db.close()
        
        return {
            "status": "success",
            "count": len(analyses),
            "analyses": [
                {
                    "id": analysis.id,
                    "filename": analysis.filename,
                    "query": analysis.query[:100] + "..." if len(analysis.query) > 100 else analysis.query,
                    "summary": analysis.summary,
                    "created_at": analysis.created_at.isoformat(),
                    "processing_time": analysis.processing_time,
                    "status": analysis.status
                }
                for analysis in analyses
            ]
        }
    except Exception as e:
        logger.error(f"Error getting recent analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve analyses", "message": str(e)}
        )

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    if not DATABASE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        db = get_db()
        stats = get_system_stats(db)
        db.close()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve statistics", "message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Professional Blood Test Report Analyser...")
    print("🚀 Starting Professional Blood Test Report Analyser...")
    print("🏥 Professional Medical Analysis System v2.2.0")
    print("🛡️ Enhanced Error Handling & Validation Active")
    
    # Initialize queue worker if available
    if QUEUE_ENABLED:
        try:
            start_background_worker()
            print("⚡ Queue Worker System: ACTIVE")
            print("🔄 Concurrent Processing: ENABLED")
        except Exception as e:
            logger.error(f"Failed to start queue worker: {e}")
            print(f"⚠️  Queue Worker: FAILED ({e})")
    else:
        print("⚠️  Queue Worker: DISABLED (Redis not available)")
    
    print("📊 Server will be available at: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/")
    print("🩺 Extended Health Check: http://localhost:8000/health")
    
    if QUEUE_ENABLED:
        print("🚀 Synchronous Analysis: POST /analyze")
        print("⚡ Asynchronous Analysis: POST /analyze-async")
        print("📊 Queue Status: GET /status/{job_id}")
        print("📈 Queue Stats: GET /queue/stats")
    else:
        print("🚀 Synchronous Analysis: POST /analyze")
        print("⚠️  Asynchronous Analysis: NOT AVAILABLE")
    
    print("⚠️  All analysis includes appropriate medical disclaimers")
    print("📝 Logging to: blood_test_analyzer.log")
    
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")