"""
Database models and operations for Blood Test Analyzer
Minimal SQLite implementation for storing analysis results and user data
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///./blood_test_analyzer.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model for storing basic user information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_analysis = Column(DateTime, nullable=True)
    total_analyses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class AnalysisResult(Base):
    """Model for storing blood test analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)  # Optional user association
    job_id = Column(String, nullable=True, index=True)  # For async processing
    
    # File information
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String, nullable=True)  # For duplicate detection
    
    # Analysis data
    query = Column(Text, nullable=False)
    analysis_result = Column(Text, nullable=False)  # Full analysis text
    summary = Column(Text, nullable=True)  # Brief summary
    
    # Metadata
    processing_time = Column(Float, nullable=True)
    analysis_type = Column(String, default="comprehensive")  # comprehensive, nutrition, exercise
    status = Column(String, default="completed")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Blood test markers (extracted for quick queries)
    markers_json = Column(Text, nullable=True)  # JSON string of key markers

class SystemStats(Base):
    """Model for storing system statistics"""
    __tablename__ = "system_stats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, default=datetime.utcnow)
    total_analyses = Column(Integer, default=0)
    successful_analyses = Column(Integer, default=0)
    failed_analyses = Column(Integer, default=0)
    avg_processing_time = Column(Float, nullable=True)
    active_users = Column(Integer, default=0)

# Database operations
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.close()
        raise

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def create_user(db: Session, email: Optional[str] = None, name: Optional[str] = None) -> User:
    """Create a new user"""
    try:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created user: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def create_analysis_result(
    db: Session,
    filename: str,
    query: str,
    analysis_result: str,
    user_id: Optional[str] = None,
    job_id: Optional[str] = None,
    processing_time: Optional[float] = None,
    file_size: Optional[int] = None,
    markers: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """Create a new analysis result"""
    try:
        analysis = AnalysisResult(
            user_id=user_id,
            job_id=job_id,
            filename=filename,
            file_size=file_size,
            query=query,
            analysis_result=analysis_result,
            processing_time=processing_time,
            completed_at=datetime.utcnow(),
            markers_json=json.dumps(markers) if markers else None
        )
        
        # Generate summary from analysis result (first 200 characters)
        analysis.summary = analysis_result[:200] + "..." if len(analysis_result) > 200 else analysis_result
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Update user statistics
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_analysis = datetime.utcnow()
                user.total_analyses += 1
                db.commit()
        
        logger.info(f"Created analysis result: {analysis.id}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error creating analysis result: {e}")
        db.rollback()
        raise

def get_analysis_by_job_id(db: Session, job_id: str) -> Optional[AnalysisResult]:
    """Get analysis result by job ID"""
    try:
        return db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).first()
    except Exception as e:
        logger.error(f"Error getting analysis by job ID: {e}")
        return None

def get_user_analyses(db: Session, user_id: str, limit: int = 10) -> List[AnalysisResult]:
    """Get recent analyses for a user"""
    try:
        return db.query(AnalysisResult)\
            .filter(AnalysisResult.user_id == user_id)\
            .order_by(AnalysisResult.created_at.desc())\
            .limit(limit)\
            .all()
    except Exception as e:
        logger.error(f"Error getting user analyses: {e}")
        return []

def get_recent_analyses(db: Session, limit: int = 10) -> List[AnalysisResult]:
    """Get recent analyses (for admin/stats)"""
    try:
        return db.query(AnalysisResult)\
            .order_by(AnalysisResult.created_at.desc())\
            .limit(limit)\
            .all()
    except Exception as e:
        logger.error(f"Error getting recent analyses: {e}")
        return []

def update_analysis_status(db: Session, analysis_id: str, status: str, error_message: Optional[str] = None):
    """Update analysis status"""
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if analysis:
            analysis.status = status
            if error_message:
                analysis.error_message = error_message
            if status == "completed":
                analysis.completed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated analysis {analysis_id} status to {status}")
    except Exception as e:
        logger.error(f"Error updating analysis status: {e}")
        db.rollback()

def get_system_stats(db: Session) -> Dict[str, Any]:
    """Get system statistics"""
    try:
        total_analyses = db.query(AnalysisResult).count()
        successful_analyses = db.query(AnalysisResult).filter(AnalysisResult.status == "completed").count()
        failed_analyses = db.query(AnalysisResult).filter(AnalysisResult.status == "failed").count()
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Average processing time
        avg_time_result = db.query(AnalysisResult.processing_time)\
            .filter(AnalysisResult.processing_time.isnot(None))\
            .all()
        avg_processing_time = sum(r[0] for r in avg_time_result) / len(avg_time_result) if avg_time_result else 0
        
        return {
            "total_analyses": total_analyses,
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "success_rate": (successful_analyses / total_analyses * 100) if total_analyses > 0 else 0,
            "total_users": total_users,
            "active_users": active_users,
            "avg_processing_time": round(avg_processing_time, 2)
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {}

# Utility functions
def extract_blood_markers(analysis_text: str) -> Dict[str, Any]:
    """Extract key blood markers from analysis text for quick search"""
    markers = {}
    try:
        # Simple pattern matching for common markers
        import re
        
        # Look for common patterns like "Glucose: 95 mg/dL"
        patterns = {
            'glucose': r'glucose[:\s]+(\d+\.?\d*)\s*mg/dl',
            'cholesterol': r'cholesterol[:\s]+(\d+\.?\d*)\s*mg/dl',
            'ldl': r'ldl[:\s]+(\d+\.?\d*)\s*mg/dl',
            'hdl': r'hdl[:\s]+(\d+\.?\d*)\s*mg/dl',
            'triglycerides': r'triglycerides[:\s]+(\d+\.?\d*)\s*mg/dl',
            'hemoglobin': r'hemoglobin[:\s]+(\d+\.?\d*)\s*g/dl'
        }
        
        for marker, pattern in patterns.items():
            match = re.search(pattern, analysis_text.lower())
            if match:
                markers[marker] = float(match.group(1))
                
    except Exception as e:
        logger.warning(f"Error extracting blood markers: {e}")
    
    return markers

# Initialize database on import
if __name__ != "__main__":
    init_database() 