"""
Site clustering and recommendation engine
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from src.database.models import SiteMaster, get_session


class SiteClusterer:
    """Cluster similar sites using KMeans"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.session = get_session()
        self.scaler = StandardScaler()
        self.kmeans = None
    
    def cluster_sites(self) -> Dict[int, List[str]]:
        """
        Cluster sites based on their characteristics
        
        Returns:
            Dictionary mapping cluster ID to list of site names
        """
        print(f"🔬 Clustering sites into {self.n_clusters} groups...")
        
        # Load site data
        sites = self.session.query(SiteMaster).all()
        
        if len(sites) < self.n_clusters:
            print(f"⚠️ Not enough sites for clustering (need at least {self.n_clusters})")
            return {}
        
        # Prepare features
        features = []
        site_names = []
        
        for site in sites:
            feature_vector = [
                site.total_studies or 0,
                site.completed_studies or 0,
                site.ongoing_studies or 0,
                site.terminated_studies or 0,
                site.avg_phase or 0,
                site.avg_enrollment or 0,
                site.completion_ratio or 0,
                site.data_quality_score or 0,
                site.experience_index or 0
            ]
            features.append(feature_vector)
            site_names.append(site.site_name)
        
        # Normalize features
        X = self.scaler.fit_transform(features)
        
        # Perform clustering
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X)
        
        # Group sites by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(site_names[idx])
        
        # Print cluster summary
        print("\n📊 Cluster Summary:")
        for cluster_id, sites_in_cluster in clusters.items():
            print(f"  Cluster {cluster_id}: {len(sites_in_cluster)} sites")
        
        print("✅ Clustering completed")
        return clusters
    
    def get_cluster_characteristics(self, cluster_id: int) -> Dict:
        """
        Get characteristic features of a cluster
        """
        sites = self.session.query(SiteMaster).all()
        
        # Get features for all sites
        features = []
        for site in sites:
            feature_vector = [
                site.total_studies or 0,
                site.completed_studies or 0,
                site.ongoing_studies or 0,
                site.terminated_studies or 0,
                site.avg_phase or 0,
                site.avg_enrollment or 0,
                site.completion_ratio or 0,
                site.data_quality_score or 0,
                site.experience_index or 0
            ]
            features.append(feature_vector)
        
        X = self.scaler.transform(features)
        labels = self.kmeans.predict(X)
        
        # Get sites in this cluster
        cluster_features = X[labels == cluster_id]
        
        if len(cluster_features) == 0:
            return {}
        
        # Calculate mean characteristics
        mean_features = cluster_features.mean(axis=0)
        
        feature_names = [
            "Total Studies",
            "Completed Studies",
            "Ongoing Studies",
            "Terminated Studies",
            "Avg Phase",
            "Avg Enrollment",
            "Completion Ratio",
            "Data Quality Score",
            "Experience Index"
        ]
        
        return {name: round(float(value), 2) for name, value in zip(feature_names, mean_features)}
    
    def close(self):
        """Close database session"""
        self.session.close()


class SiteRecommender:
    """Recommend top sites for a new study"""
    
    def __init__(self):
        self.session = get_session()
    
    def recommend_sites(
        self,
        target_conditions: List[str],
        target_phase: str,
        target_country: str = None,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Recommend top sites for a new study
        
        Args:
            target_conditions: List of therapeutic areas
            target_phase: Study phase
            target_country: Optional country filter
            top_n: Number of recommendations
        
        Returns:
            List of (site_name, score) tuples
        """
        print(f"🎯 Finding top {top_n} sites for your study...")
        
        from src.metrics.calculator import MetricsCalculator
        calculator = MetricsCalculator()
        
        # Get all sites
        query = self.session.query(SiteMaster)
        if target_country:
            query = query.filter(SiteMaster.country == target_country)
        
        sites = query.all()
        
        # Calculate scores
        site_scores = []
        for site in sites:
            # Calculate match score
            match_score = calculator.calculate_match_score(
                site=site,
                target_conditions=target_conditions,
                target_phase=target_phase,
                target_interventions=[],  # Can be enhanced
                target_region=target_country or site.country
            )
            
            # Bonus for high completion ratio and data quality
            performance_bonus = (
                (site.completion_ratio or 0) * 0.2 +
                (site.data_quality_score or 0) * 0.1
            )
            
            total_score = match_score + performance_bonus
            site_scores.append((site.site_name, site.country, round(total_score, 2)))
        
        # Sort by score
        site_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Return top N
        recommendations = [(f"{name} ({country})", score) 
                          for name, country, score in site_scores[:top_n]]
        
        calculator.close()
        return recommendations
    
    def close(self):
        """Close database session"""
        self.session.close()
