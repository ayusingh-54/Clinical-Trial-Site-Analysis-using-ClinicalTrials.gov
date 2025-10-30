"""
Database models for clinical trial data
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class ClinicalTrial(Base):
    """Clinical Trial model"""
    __tablename__ = 'clinical_trials'
    
    id = Column(Integer, primary_key=True)
    nct_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text)
    status = Column(String(100))
    study_type = Column(String(100))
    phase = Column(String(50))
    start_date = Column(Date)
    completion_date = Column(Date)
    primary_completion_date = Column(Date)
    enrollment = Column(Integer)
    sponsor = Column(String(500))
    
    # Conditions and interventions (stored as comma-separated)
    conditions = Column(Text)
    interventions = Column(Text)
    
    # Dates
    last_update_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    locations = relationship("TrialLocation", back_populates="trial", cascade="all, delete-orphan")


class TrialLocation(Base):
    """Trial location model"""
    __tablename__ = 'trial_locations'
    
    id = Column(Integer, primary_key=True)
    trial_id = Column(Integer, ForeignKey('clinical_trials.id'), nullable=False)
    facility = Column(String(500))
    city = Column(String(200))
    state = Column(String(200))
    country = Column(String(100), index=True)
    zip_code = Column(String(20))
    investigator = Column(String(300))
    
    # Relationship
    trial = relationship("ClinicalTrial", back_populates="locations")


class SiteMaster(Base):
    """Aggregated site master table"""
    __tablename__ = 'site_master'
    
    id = Column(Integer, primary_key=True)
    site_name = Column(String(500), index=True)
    city = Column(String(200))
    country = Column(String(100), index=True)
    
    # Aggregated metrics
    total_studies = Column(Integer, default=0)
    completed_studies = Column(Integer, default=0)
    ongoing_studies = Column(Integer, default=0)
    terminated_studies = Column(Integer, default=0)
    withdrawn_studies = Column(Integer, default=0)
    
    # Additional info
    therapeutic_areas = Column(Text)  # Comma-separated
    investigators = Column(Text)  # Comma-separated
    avg_phase = Column(Float)
    avg_enrollment = Column(Float)
    last_active_date = Column(Date)
    
    # Calculated scores
    match_score = Column(Float)
    data_quality_score = Column(Float)
    completion_ratio = Column(Float)
    experience_index = Column(Integer)
    
    # Enrichment data
    publications_count = Column(Integer, default=0)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SitePerformance(Base):
    """Site performance metrics"""
    __tablename__ = 'site_performance'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('site_master.id'), nullable=False)
    
    # Performance indicators
    completion_ratio = Column(Float)
    recruitment_efficiency = Column(Float)
    experience_index = Column(Integer)
    
    # Strengths and weaknesses (JSON stored as text)
    strengths = Column(Text)
    weaknesses = Column(Text)
    
    # AI-generated summary
    ai_summary = Column(Text)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database engine and session
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully")


def get_session():
    """Get database session"""
    return SessionLocal()
