"""
Data loader for storing extracted data into database
"""
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm
from src.database.models import ClinicalTrial, TrialLocation, get_session
from src.data_extraction.clinical_trials_api import ClinicalTrialsAPI


class DataLoader:
    """Load clinical trial data into database"""
    
    def __init__(self):
        self.api = ClinicalTrialsAPI()
        self.session = get_session()
    
    def load_studies(
        self,
        condition: str = "cancer",
        phase: str = None,
        status: str = None,
        country: str = None,
        max_pages: int = 5
    ):
        """
        Fetch and load studies into database
        
        Args:
            condition: Disease condition to search
            phase: Study phase filter
            status: Study status filter
            country: Country filter
            max_pages: Maximum pages to fetch
        """
        print(f"🔍 Fetching studies for: {condition}")
        
        # Fetch studies from API
        studies = self.api.fetch_studies(
            condition=condition,
            phase=phase,
            status=status,
            country=country,
            max_pages=max_pages
        )
        
        if not studies:
            print("❌ No studies found")
            return
        
        print(f"\n💾 Loading {len(studies)} studies into database...")
        
        # Process and store each study
        loaded_count = 0
        updated_count = 0
        
        for study_data in tqdm(studies, desc="Processing studies"):
            try:
                parsed_study = self.api.parse_study(study_data)
                
                if self._store_study(parsed_study):
                    loaded_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                print(f"\n⚠️ Error processing study: {e}")
                continue
        
        self.session.commit()
        print(f"\n✅ Loaded: {loaded_count} new studies")
        print(f"✅ Updated: {updated_count} existing studies")
    
    def _store_study(self, study: Dict) -> bool:
        """
        Store a single study in database
        
        Returns:
            True if new study, False if updated existing
        """
        # Check if study already exists
        existing = self.session.query(ClinicalTrial).filter_by(
            nct_id=study["nct_id"]
        ).first()
        
        if existing:
            # Update existing study
            for key, value in study.items():
                if key != "locations":
                    setattr(existing, key, value)
            
            # Update locations
            self.session.query(TrialLocation).filter_by(
                trial_id=existing.id
            ).delete()
            
            for loc in study.get("locations", []):
                location = TrialLocation(
                    trial_id=existing.id,
                    **loc
                )
                self.session.add(location)
            
            return False
        else:
            # Create new study
            trial = ClinicalTrial(
                nct_id=study["nct_id"],
                title=study["title"],
                status=study["status"],
                study_type=study["study_type"],
                phase=study["phase"],
                start_date=study["start_date"],
                completion_date=study["completion_date"],
                primary_completion_date=study["primary_completion_date"],
                enrollment=study["enrollment"],
                sponsor=study["sponsor"],
                conditions=study["conditions"],
                interventions=study["interventions"],
                last_update_date=study["last_update_date"]
            )
            self.session.add(trial)
            self.session.flush()  # Get the trial ID
            
            # Add locations
            for loc in study.get("locations", []):
                location = TrialLocation(
                    trial_id=trial.id,
                    **loc
                )
                self.session.add(location)
            
            return True
    
    def close(self):
        """Close database session"""
        self.session.close()
