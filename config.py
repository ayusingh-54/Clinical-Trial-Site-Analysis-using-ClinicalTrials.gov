"""
Configuration settings for Clinical Trial Site Evaluation System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/clinical_trials.db")

# API configuration
CLINICALTRIALS_API_BASE_URL = os.getenv(
    "CLINICALTRIALS_API_BASE_URL", 
    "https://clinicaltrials.gov/api/v2"
)
PUBMED_API_BASE_URL = os.getenv(
    "PUBMED_API_BASE_URL",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
)

# OpenAI configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Retry configuration
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", 3))
API_RETRY_DELAY = int(os.getenv("API_RETRY_DELAY", 2))

# Scoring weights
MATCH_SCORE_WEIGHTS = {
    "therapeutic": 0.4,
    "phase": 0.2,
    "intervention": 0.2,
    "region": 0.2
}

# Fuzzy matching threshold
FUZZY_MATCH_THRESHOLD = 85

# Data quality parameters
DATA_QUALITY_RECENCY_MONTHS = 12
