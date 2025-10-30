"""
Site aggregation and fuzzy matching
"""
from typing import List, Dict, Tuple
from collections import defaultdict
from fuzzywuzzy import fuzz
from datetime import datetime
from sqlalchemy import func
from src.database.models import (
    ClinicalTrial, TrialLocation, SiteMaster, get_session
)
import config


class SiteAggregator:
    """Aggregate trial data by unique sites"""
    
    def __init__(self):
        self.session = get_session()
        self.fuzzy_threshold = config.FUZZY_MATCH_THRESHOLD
    
    def aggregate_sites(self):
        """
        Aggregate all trial locations into site master table
        """
        print("🔄 Aggregating sites from trial locations...")
        
        # Get all locations
        locations = self.session.query(TrialLocation).all()
        
        if not locations:
            print("❌ No locations found in database")
            return
        
        # Group locations by normalized site name
        site_groups = self._group_sites_fuzzy(locations)
        
        print(f"✅ Found {len(site_groups)} unique sites")
        print("\n💾 Calculating site metrics...")
        
        # Process each site group
        for site_name, location_ids in site_groups.items():
            self._process_site(site_name, location_ids)
        
        self.session.commit()
        print("✅ Site aggregation completed")
    
    def _group_sites_fuzzy(self, locations: List[TrialLocation]) -> Dict[str, List[int]]:
        """
        Group similar site names using fuzzy matching
        
        Returns:
            Dictionary mapping normalized site name to list of location IDs
        """
        site_groups = defaultdict(list)
        processed_sites = {}
        
        for location in locations:
            # Create site identifier
            facility = (location.facility or "").strip()
            city = (location.city or "").strip()
            country = (location.country or "").strip()
            
            if not facility or not country:
                continue
            
            site_key = f"{facility}, {city}, {country}"
            
            # Check for fuzzy matches with existing sites
            matched = False
            for existing_key, existing_locations in processed_sites.items():
                similarity = fuzz.ratio(site_key.lower(), existing_key.lower())
                
                if similarity >= self.fuzzy_threshold:
                    # Match found - add to existing group
                    site_groups[existing_key].append(location.id)
                    matched = True
                    break
            
            if not matched:
                # New unique site
                site_groups[site_key].append(location.id)
                processed_sites[site_key] = [location.id]
        
        return dict(site_groups)
    
    def _process_site(self, site_name: str, location_ids: List[int]):
        """
        Calculate metrics for a single site
        """
        # Parse site components
        parts = site_name.split(", ")
        facility = parts[0] if len(parts) > 0 else ""
        city = parts[1] if len(parts) > 1 else ""
        country = parts[2] if len(parts) > 2 else ""
        
        # Get all trials for this site
        trials = self.session.query(ClinicalTrial).join(
            TrialLocation
        ).filter(
            TrialLocation.id.in_(location_ids)
        ).distinct().all()
        
        if not trials:
            return
        
        # Calculate statistics
        total_studies = len(trials)
        
        # Status values are stored in UPPERCASE in database
        completed = sum(1 for t in trials if t.status and t.status.upper() == "COMPLETED")
        ongoing = sum(1 for t in trials if t.status and t.status.upper() in [
            "RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION", "NOT_YET_RECRUITING"
        ])
        terminated = sum(1 for t in trials if t.status and t.status.upper() == "TERMINATED")
        withdrawn = sum(1 for t in trials if t.status and t.status.upper() == "WITHDRAWN")
        
        # Therapeutic areas
        all_conditions = set()
        for trial in trials:
            if trial.conditions:
                conditions = [c.strip() for c in trial.conditions.split(",")]
                all_conditions.update(conditions)
        
        # Investigators
        investigators = set()
        for loc_id in location_ids:
            location = self.session.query(TrialLocation).get(loc_id)
            if location and location.investigator:
                invs = [i.strip() for i in location.investigator.split(",")]
                investigators.update(invs)
        
        # Average phase
        phases = []
        for trial in trials:
            if trial.phase:
                phase_num = self._extract_phase_number(trial.phase)
                if phase_num:
                    phases.append(phase_num)
        avg_phase = sum(phases) / len(phases) if phases else None
        
        # Average enrollment
        enrollments = [t.enrollment for t in trials if t.enrollment]
        avg_enrollment = sum(enrollments) / len(enrollments) if enrollments else None
        
        # Last active date
        dates = [t.last_update_date for t in trials if t.last_update_date]
        last_active = max(dates) if dates else None
        
        # Check if site exists
        existing = self.session.query(SiteMaster).filter_by(
            site_name=facility,
            city=city,
            country=country
        ).first()
        
        if existing:
            # Update existing
            existing.total_studies = total_studies
            existing.completed_studies = completed
            existing.ongoing_studies = ongoing
            existing.terminated_studies = terminated
            existing.withdrawn_studies = withdrawn
            existing.therapeutic_areas = ", ".join(sorted(all_conditions)[:50])  # Limit length
            existing.investigators = ", ".join(sorted(investigators)[:50])
            existing.avg_phase = avg_phase
            existing.avg_enrollment = avg_enrollment
            existing.last_active_date = last_active
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            site = SiteMaster(
                site_name=facility,
                city=city,
                country=country,
                total_studies=total_studies,
                completed_studies=completed,
                ongoing_studies=ongoing,
                terminated_studies=terminated,
                withdrawn_studies=withdrawn,
                therapeutic_areas=", ".join(sorted(all_conditions)[:50]),
                investigators=", ".join(sorted(investigators)[:50]),
                avg_phase=avg_phase,
                avg_enrollment=avg_enrollment,
                last_active_date=last_active
            )
            self.session.add(site)
    
    def _extract_phase_number(self, phase_str: str) -> float:
        """
        Extract numeric phase value from phase string
        """
        phase_map = {
            "Early Phase 1": 0.5,
            "Phase 1": 1.0,
            "Phase 1/Phase 2": 1.5,
            "Phase 2": 2.0,
            "Phase 2/Phase 3": 2.5,
            "Phase 3": 3.0,
            "Phase 4": 4.0
        }
        
        for key, value in phase_map.items():
            if key in phase_str:
                return value
        
        return None
    
    def close(self):
        """Close database session"""
        self.session.close()
