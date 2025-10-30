"""
ClinicalTrials.gov API v2 data extraction
"""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
import config


class ClinicalTrialsAPI:
    """Wrapper for ClinicalTrials.gov API v2"""
    
    def __init__(self):
        self.base_url = config.CLINICALTRIALS_API_BASE_URL
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
    
    def fetch_studies(
        self, 
        condition: Optional[str] = None,
        phase: Optional[str] = None,
        status: Optional[str] = None,
        country: Optional[str] = None,
        page_size: int = 100,
        max_pages: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch studies from ClinicalTrials.gov API
        
        Args:
            condition: Disease or condition (e.g., "cancer")
            phase: Study phase (e.g., "Phase 3")
            status: Study status (e.g., "Completed")
            country: Country code or name
            page_size: Number of results per page
            max_pages: Maximum number of pages to fetch
        
        Returns:
            List of study records
        """
        all_studies = []
        page_token = None
        page_count = 0
        
        while True:
            if max_pages and page_count >= max_pages:
                break
            
            # Build query parameters
            params = {
                "format": "json",
                "pageSize": page_size
            }
            
            # Add filters
            query_parts = []
            if condition:
                query_parts.append(f"AREA[Condition]{condition}")
            if phase:
                query_parts.append(f"AREA[Phase]{phase}")
            if status:
                query_parts.append(f"AREA[OverallStatus]{status}")
            if country:
                query_parts.append(f"AREA[LocationCountry]{country}")
            
            if query_parts:
                params["query.cond"] = " AND ".join(query_parts)
            
            if page_token:
                params["pageToken"] = page_token
            
            # Make request with retry logic
            url = f"{self.base_url}/studies"
            studies_data = self._make_request(url, params)
            
            if not studies_data or "studies" not in studies_data:
                break
            
            studies = studies_data.get("studies", [])
            all_studies.extend(studies)
            
            print(f"📥 Fetched page {page_count + 1}: {len(studies)} studies")
            
            # Check for next page
            page_token = studies_data.get("nextPageToken")
            page_count += 1
            
            if not page_token:
                break
        
        print(f"✅ Total studies fetched: {len(all_studies)}")
        return all_studies
    
    def fetch_study_details(self, nct_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific study
        
        Args:
            nct_id: NCT identifier (e.g., "NCT01234567")
        
        Returns:
            Study details dictionary
        """
        url = f"{self.base_url}/studies/{nct_id}"
        return self._make_request(url, {"format": "json"})
    
    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """
        Make HTTP request with retry logic
        
        Args:
            url: API endpoint URL
            params: Query parameters
        
        Returns:
            JSON response data
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    print(f"❌ Failed to fetch data after {self.max_retries} attempts")
                    return None
    
    def parse_study(self, study_data: Dict) -> Dict:
        """
        Parse and normalize study data
        
        Args:
            study_data: Raw study data from API
        
        Returns:
            Normalized study dictionary
        """
        protocol = study_data.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        conditions = protocol.get("conditionsModule", {})
        interventions = protocol.get("armsInterventionsModule", {})
        sponsor = protocol.get("sponsorCollaboratorsModule", {})
        contacts = protocol.get("contactsLocationsModule", {})
        
        # Parse dates
        start_date = self._parse_date(status.get("startDateStruct"))
        completion_date = self._parse_date(status.get("completionDateStruct"))
        primary_completion_date = self._parse_date(status.get("primaryCompletionDateStruct"))
        last_update_date = self._parse_date(status.get("lastUpdatePostDateStruct"))
        
        # Parse enrollment
        enrollment = status.get("enrollmentInfo", {}).get("count")
        
        # Parse conditions
        condition_list = conditions.get("conditions", [])
        condition_str = ", ".join(condition_list) if condition_list else ""
        
        # Parse interventions
        intervention_list = interventions.get("interventions", [])
        intervention_str = ", ".join([
            f"{i.get('type', '')}: {i.get('name', '')}" 
            for i in intervention_list
        ]) if intervention_list else ""
        
        # Parse sponsor
        lead_sponsor = sponsor.get("leadSponsor", {})
        sponsor_name = lead_sponsor.get("name", "")
        
        # Parse locations
        locations = []
        location_list = contacts.get("locations", [])
        for loc in location_list:
            facility = loc.get("facility", "")
            city = loc.get("city", "")
            state = loc.get("state", "")
            country = loc.get("country", "")
            zip_code = loc.get("zip", "")
            
            # Parse contacts/investigators
            investigators = []
            for contact in loc.get("contacts", []):
                name = contact.get("name", "")
                if name:
                    investigators.append(name)
            
            locations.append({
                "facility": facility,
                "city": city,
                "state": state,
                "country": country,
                "zip_code": zip_code,
                "investigator": ", ".join(investigators) if investigators else ""
            })
        
        return {
            "nct_id": identification.get("nctId", ""),
            "title": identification.get("briefTitle", ""),
            "status": status.get("overallStatus", ""),
            "study_type": design.get("studyType", ""),
            "phase": ", ".join(design.get("phases", [])),
            "start_date": start_date,
            "completion_date": completion_date,
            "primary_completion_date": primary_completion_date,
            "enrollment": enrollment,
            "sponsor": sponsor_name,
            "conditions": condition_str,
            "interventions": intervention_str,
            "last_update_date": last_update_date,
            "locations": locations
        }
    
    def _parse_date(self, date_struct: Optional[Dict]) -> Optional[str]:
        """Parse date structure from API"""
        if not date_struct:
            return None
        
        year = date_struct.get("year")
        month = date_struct.get("month", 1)
        day = date_struct.get("day", 1)
        
        if year:
            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                return None
        return None
