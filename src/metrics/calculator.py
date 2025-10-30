"""
Calculate match scores, data quality, and performance metrics
"""
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from src.database.models import SiteMaster, ClinicalTrial, TrialLocation, get_session
import config


class MetricsCalculator:
    """Calculate various metrics for sites"""
    
    def __init__(self):
        self.session = get_session()
        self.weights = config.MATCH_SCORE_WEIGHTS
    
    def calculate_all_metrics(self):
        """Calculate all metrics for all sites"""
        print("📊 Calculating metrics for all sites...")
        
        sites = self.session.query(SiteMaster).all()
        
        for site in sites:
            try:
                # Calculate completion ratio
                site.completion_ratio = self._calculate_completion_ratio(site)
                
                # Calculate experience index
                site.experience_index = site.total_studies
                
                # Calculate data quality score
                site.data_quality_score = self._calculate_data_quality(site)
                
            except Exception as e:
                print(f"⚠️ Error calculating metrics for {site.site_name}: {e}")
        
        self.session.commit()
        print("✅ Metrics calculation completed")
    
    def calculate_match_score(
        self,
        site: SiteMaster,
        target_conditions: List[str],
        target_phase: str,
        target_interventions: List[str],
        target_region: str
    ) -> float:
        """
        Calculate match score for a site against target study criteria
        
        Args:
            site: SiteMaster instance
            target_conditions: List of target therapeutic areas
            target_phase: Target study phase
            target_interventions: List of target intervention types
            target_region: Target region/country
        
        Returns:
            Match score between 0 and 1
        """
        # Therapeutic area match
        site_conditions = set(site.therapeutic_areas.split(", ")) if site.therapeutic_areas else set()
        target_conditions_set = set(target_conditions)
        
        if len(site_conditions) > 0 and len(target_conditions_set) > 0:
            therapeutic_match = len(site_conditions & target_conditions_set) / len(target_conditions_set)
        else:
            therapeutic_match = 0
        
        # Phase match
        target_phase_num = self._extract_phase_number(target_phase)
        if site.avg_phase and target_phase_num:
            phase_diff = abs(site.avg_phase - target_phase_num)
            phase_match = max(0, 1 - (phase_diff / 4))  # Normalize by max phase difference
        else:
            phase_match = 0
        
        # Intervention match (simplified - can be enhanced)
        intervention_match = 0.5  # Default score
        
        # Region match
        if target_region.lower() == site.country.lower():
            region_match = 1.0
        else:
            region_match = 0.3  # Partial score for different region
        
        # Calculate weighted match score
        match_score = (
            self.weights["therapeutic"] * therapeutic_match +
            self.weights["phase"] * phase_match +
            self.weights["intervention"] * intervention_match +
            self.weights["region"] * region_match
        )
        
        return round(match_score, 2)
    
    def _calculate_completion_ratio(self, site: SiteMaster) -> float:
        """
        Calculate completion ratio
        
        Formula: Completed / (Completed + Terminated + Withdrawn)
        
        Returns:
            Ratio between 0.0 and 1.0, or 0.0 if no concluded studies
        """
        total_concluded = site.completed_studies + site.terminated_studies + site.withdrawn_studies
        
        if total_concluded == 0:
            # No concluded studies yet - return 0 (neutral)
            # Note: Sites with only ongoing studies will have 0 ratio until studies conclude
            return 0.0
        
        ratio = site.completed_studies / total_concluded
        return round(min(ratio, 1.0), 2)  # Ensure ratio never exceeds 1.0
    
    def _calculate_data_quality(self, site: SiteMaster) -> float:
        """
        Calculate data quality score based on completeness and recency
        
        Formula: (FieldsFilled / TotalFields) * RecencyWeight
        """
        # Count filled fields
        total_fields = 10
        filled_fields = 0
        
        if site.site_name:
            filled_fields += 1
        if site.city:
            filled_fields += 1
        if site.country:
            filled_fields += 1
        if site.therapeutic_areas:
            filled_fields += 1
        if site.investigators:
            filled_fields += 1
        if site.avg_phase is not None:
            filled_fields += 1
        if site.avg_enrollment is not None:
            filled_fields += 1
        if site.last_active_date:
            filled_fields += 1
        if site.total_studies > 0:
            filled_fields += 1
        if site.completed_studies > 0:
            filled_fields += 1
        
        completeness = filled_fields / total_fields
        
        # Calculate recency weight
        recency_weight = 1.0
        if site.last_active_date:
            months_old = (datetime.now().date() - site.last_active_date).days / 30
            
            if months_old <= config.DATA_QUALITY_RECENCY_MONTHS:
                recency_weight = 1.0
            elif months_old <= 24:
                recency_weight = 0.8
            elif months_old <= 36:
                recency_weight = 0.6
            else:
                recency_weight = 0.4
        
        data_quality = completeness * recency_weight
        return round(data_quality, 2)
    
    def generate_strengths_weaknesses(self, site: SiteMaster) -> Dict[str, List[str]]:
        """
        Generate comprehensive strengths and weaknesses for a site
        
        Returns:
            Dictionary with 'strengths' and 'weaknesses' lists
        """
        strengths = []
        weaknesses = []
        
        # Completion ratio analysis
        if site.completion_ratio and site.completion_ratio >= 0.9:
            strengths.append(f"✅ Exceptional completion rate ({site.completion_ratio*100:.0f}%) - outstanding operational discipline")
        elif site.completion_ratio and site.completion_ratio >= 0.8:
            strengths.append(f"✅ High completion rate ({site.completion_ratio*100:.0f}%) - strong operational discipline")
        elif site.completion_ratio and site.completion_ratio >= 0.6:
            strengths.append(f"✅ Good completion rate ({site.completion_ratio*100:.0f}%)")
        elif site.completion_ratio and 0 < site.completion_ratio < 0.5:
            weaknesses.append(f"⚠️ Low completion rate ({site.completion_ratio*100:.0f}%) - possible operational issues")
        
        # Experience level
        if site.total_studies >= 50:
            strengths.append(f"✅ Extensive trial experience ({site.total_studies} studies) - highly experienced site")
        elif site.total_studies >= 20:
            strengths.append(f"✅ Solid experience ({site.total_studies} studies)")
        elif site.total_studies >= 10:
            strengths.append(f"✅ Moderate experience ({site.total_studies} studies)")
        elif site.total_studies < 3:
            weaknesses.append(f"⚠️ Limited trial experience ({site.total_studies} study/studies)")
        
        # Active studies analysis
        if site.ongoing_studies >= 5:
            strengths.append(f"✅ Currently active with {site.ongoing_studies} ongoing studies")
        elif site.total_studies > 0 and site.ongoing_studies == 0:
            if site.completed_studies > 0:
                weaknesses.append("⚠️ No currently active studies")
        
        # Therapeutic expertise
        if site.therapeutic_areas:
            areas = [a.strip() for a in site.therapeutic_areas.split(",") if a.strip()]
            area_count = len(areas)
            if area_count >= 15:
                strengths.append(f"✅ Highly diverse therapeutic portfolio ({area_count} areas)")
            elif area_count >= 10:
                strengths.append(f"✅ Diverse therapeutic portfolio ({area_count} areas)")
            elif area_count >= 5:
                strengths.append(f"✅ Moderate therapeutic diversity ({area_count} areas)")
            elif area_count <= 2 and site.total_studies >= 5:
                strengths.append(f"✅ Specialized expertise in {area_count} therapeutic area(s)")
        
        # Data quality assessment
        if site.data_quality_score:
            if site.data_quality_score >= 0.9:
                strengths.append(f"✅ Excellent data quality ({site.data_quality_score:.2f}) - comprehensive reporting")
            elif site.data_quality_score >= 0.8:
                strengths.append(f"✅ High data quality ({site.data_quality_score:.2f})")
            elif site.data_quality_score >= 0.6:
                strengths.append(f"✅ Good data quality ({site.data_quality_score:.2f})")
            elif site.data_quality_score < 0.5:
                weaknesses.append(f"⚠️ Low data quality ({site.data_quality_score:.2f}) - incomplete reporting")
        
        # Recency analysis
        if site.last_active_date:
            months_old = (datetime.now().date() - site.last_active_date).days / 30
            if months_old <= 6:
                strengths.append("✅ Very recently active (within 6 months)")
            elif months_old <= 12:
                strengths.append("✅ Recently active (within 12 months)")
            elif months_old <= 24:
                pass  # Neutral - not mentioned
            elif months_old <= 36:
                weaknesses.append("⚠️ Last activity over 2 years ago")
            else:
                weaknesses.append("⚠️ No recent trial activity (3+ years)")
        
        # Termination/withdrawal analysis
        if site.total_studies > 0:
            termination_rate = (site.terminated_studies + site.withdrawn_studies) / site.total_studies
            if termination_rate > 0.4:
                weaknesses.append(f"⚠️ High termination rate ({termination_rate*100:.0f}%) - significant operational concerns")
            elif termination_rate > 0.25:
                weaknesses.append(f"⚠️ Elevated termination rate ({termination_rate*100:.0f}%)")
            elif termination_rate == 0 and site.completed_studies > 5:
                strengths.append("✅ Zero termination rate - excellent track record")
        
        # Success indicators
        if site.completed_studies >= 20:
            strengths.append(f"✅ Strong track record with {site.completed_studies} completed studies")
        elif site.completed_studies >= 10:
            strengths.append(f"✅ Good track record with {site.completed_studies} completed studies")
        
        # Phase expertise
        if site.avg_phase:
            if site.avg_phase >= 2.5:
                strengths.append(f"✅ Experience with advanced phase trials (avg Phase {site.avg_phase:.1f})")
            elif site.avg_phase >= 2.0:
                strengths.append(f"✅ Phase 2-3 expertise (avg Phase {site.avg_phase:.1f})")
        
        # Enrollment capacity
        if site.avg_enrollment and site.avg_enrollment >= 100:
            strengths.append(f"✅ Large enrollment capacity (avg {site.avg_enrollment:.0f} patients)")
        elif site.avg_enrollment and site.avg_enrollment >= 50:
            strengths.append(f"✅ Good enrollment capacity (avg {site.avg_enrollment:.0f} patients)")
        
        # If no specific strengths found, add a neutral one
        if not strengths and site.total_studies > 0:
            strengths.append("✅ Active clinical research site")
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def _extract_phase_number(self, phase_str: str) -> Optional[float]:
        """Extract numeric phase value"""
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
