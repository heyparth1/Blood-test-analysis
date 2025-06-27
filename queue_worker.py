"""
Minimal Queue Worker System for Blood Test Analysis
Handles concurrent requests using Redis queue
"""

import json
import time
import uuid
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class QueueManager:
    """Minimal Redis-based queue manager"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fallback to in-memory storage for development
            self.redis_client = None
            self._in_memory_queue = []
            self._in_memory_jobs = {}
            logger.warning("Using in-memory queue (Redis not available)")
    
    def enqueue_job(self, job_data: Dict[str, Any]) -> str:
        """Add job to queue and return job ID"""
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "data": job_data,
            "status": JobStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            if self.redis_client:
                # Redis implementation
                self.redis_client.lpush("blood_analysis_queue", json.dumps(job))
                self.redis_client.setex(f"job:{job_id}", timedelta(hours=24), json.dumps(job))
            else:
                # In-memory fallback
                self._in_memory_queue.append(job)
                self._in_memory_jobs[job_id] = job
            
            logger.info(f"Job {job_id} enqueued successfully")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            raise
    
    def dequeue_job(self) -> Optional[Dict[str, Any]]:
        """Get next job from queue"""
        try:
            if self.redis_client:
                # Redis implementation
                result = self.redis_client.brpop("blood_analysis_queue", timeout=1)
                if result:
                    job = json.loads(result[1])
                    return job
            else:
                # In-memory fallback
                if self._in_memory_queue:
                    return self._in_memory_queue.pop(0)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None
    
    def update_job_status(self, job_id: str, status: JobStatus, result: Optional[str] = None, error: Optional[str] = None):
        """Update job status and result"""
        try:
            job_data = {
                "status": status.value,
                "updated_at": datetime.now().isoformat()
            }
            
            if result:
                job_data["result"] = result
            if error:
                job_data["error"] = error
            
            if self.redis_client:
                # Redis implementation
                existing_job = self.redis_client.get(f"job:{job_id}")
                if existing_job:
                    job = json.loads(existing_job)
                    job.update(job_data)
                    self.redis_client.setex(f"job:{job_id}", timedelta(hours=24), json.dumps(job))
            else:
                # In-memory fallback
                if job_id in self._in_memory_jobs:
                    self._in_memory_jobs[job_id].update(job_data)
            
            logger.info(f"Job {job_id} status updated to {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        try:
            if self.redis_client:
                # Redis implementation
                job_data = self.redis_client.get(f"job:{job_id}")
                if job_data:
                    return json.loads(job_data)
            else:
                # In-memory fallback
                return self._in_memory_jobs.get(job_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None

class BloodTestWorker:
    """Worker process for handling blood test analysis jobs"""
    
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.running = False
    
    async def process_job(self, job: Dict[str, Any]) -> str:
        """Process a single blood test analysis job"""
        job_id = job["id"]
        job_data = job["data"]
        
        logger.info(f"Processing job {job_id}")
        
        try:
            # Update status to processing
            self.queue_manager.update_job_status(job_id, JobStatus.PROCESSING)
            
            # Import here to avoid circular imports
            from main import run_comprehensive_analysis
            
            # Extract job parameters
            query = job_data.get("query", "Please provide a comprehensive analysis of my blood test results")
            file_path = job_data.get("file_path", "data/sample.pdf")
            
            # Run the analysis
            start_time = time.time()
            result = run_comprehensive_analysis(query, file_path)
            processing_time = time.time() - start_time
            
            # Save to database if available
            analysis_id = None
            try:
                from database import get_db, create_analysis_result, extract_blood_markers
                db = get_db()
                markers = extract_blood_markers(result)
                analysis_record = create_analysis_result(
                    db=db,
                    filename=job_data.get("filename", "unknown"),
                    query=query,
                    analysis_result=result,
                    job_id=job_id,
                    processing_time=processing_time,
                    file_size=job_data.get("file_size"),
                    markers=markers
                )
                analysis_id = analysis_record.id
                db.close()
                logger.info(f"Async analysis saved to database with ID: {analysis_id}")
            except Exception as e:
                logger.warning(f"Failed to save async analysis to database: {e}")
            
            # Prepare response
            response = {
                "status": "success",
                "query": query,
                "analysis": result,
                "file_processed": job_data.get("filename", "unknown"),
                "processing_time": processing_time,
                "analysis_type": "comprehensive_medical_review",
                "specialists_consulted": [
                    "Medical Laboratory Analyst",
                    "Document Verification Specialist", 
                    "Clinical Nutritionist",
                    "Exercise Physiologist"
                ],
                "disclaimer": "This analysis is for educational purposes only. Always consult with qualified healthcare professionals for medical decisions."
            }
            
            # Add analysis_id if saved to database
            if analysis_id:
                response["analysis_id"] = analysis_id
            
            # Update job with success
            self.queue_manager.update_job_status(job_id, JobStatus.COMPLETED, result=json.dumps(response))
            
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s")
            return json.dumps(response)
            
        except Exception as e:
            error_msg = f"Job processing failed: {str(e)}"
            logger.error(f"Job {job_id} failed: {error_msg}")
            
            # Update job with error
            self.queue_manager.update_job_status(job_id, JobStatus.FAILED, error=error_msg)
            
            raise
    
    async def run(self):
        """Main worker loop"""
        self.running = True
        logger.info("Blood test worker started")
        
        while self.running:
            try:
                # Get next job from queue
                job = self.queue_manager.dequeue_job()
                
                if job:
                    # Process the job
                    await self.process_job(job)
                else:
                    # No job available, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        logger.info("Blood test worker stopped")

# Global queue manager instance
queue_manager = QueueManager()

def start_background_worker():
    """Start background worker process"""
    async def worker_task():
        worker = BloodTestWorker(queue_manager)
        await worker.run()
    
    # Start worker in background
    import threading
    
    def run_worker():
        asyncio.run(worker_task())
    
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    logger.info("Background worker started")

def enqueue_analysis(file_path: str, query: str, filename: str, file_size: Optional[int] = None) -> str:
    """Enqueue blood test analysis job"""
    job_data = {
        "file_path": file_path,
        "query": query,
        "filename": filename,
        "file_size": file_size
    }
    
    return queue_manager.enqueue_job(job_data)

def get_analysis_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis job status"""
    return queue_manager.get_job_status(job_id)

# Utility functions for checking queue health
def get_queue_stats() -> Dict[str, Any]:
    """Get queue statistics"""
    try:
        if queue_manager.redis_client:
            queue_length = queue_manager.redis_client.llen("blood_analysis_queue")
            return {
                "queue_length": queue_length,
                "backend": "redis",
                "status": "healthy"
            }
        else:
            return {
                "queue_length": len(queue_manager._in_memory_queue),
                "backend": "in_memory",
                "status": "healthy"
            }
    except Exception as e:
        return {
            "queue_length": 0,
            "backend": "unknown",
            "status": "error",
            "error": str(e)
        } 