"""
Main application entry point
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.database.models import init_db
from src.data_extraction.data_loader import DataLoader
from src.data_processing.site_aggregator import SiteAggregator
from src.metrics.calculator import MetricsCalculator
from src.ml.clustering import SiteClusterer


def extract_data(condition: str = "cancer", phase: str = None, max_pages: int = 5):
    """
    Extract clinical trial data from ClinicalTrials.gov
    
    Args:
        condition: Disease condition to search
        phase: Study phase filter
        max_pages: Maximum pages to fetch
    """
    print("\n" + "="*80)
    print("STEP 1: DATA EXTRACTION")
    print("="*80 + "\n")
    
    loader = DataLoader()
    try:
        loader.load_studies(
            condition=condition,
            phase=phase,
            max_pages=max_pages
        )
    finally:
        loader.close()


def aggregate_sites():
    """
    Aggregate trial data by unique sites
    """
    print("\n" + "="*80)
    print("STEP 2: SITE AGGREGATION")
    print("="*80 + "\n")
    
    aggregator = SiteAggregator()
    try:
        aggregator.aggregate_sites()
    finally:
        aggregator.close()


def calculate_metrics():
    """
    Calculate metrics for all sites
    """
    print("\n" + "="*80)
    print("STEP 3: METRICS CALCULATION")
    print("="*80 + "\n")
    
    calculator = MetricsCalculator()
    try:
        calculator.calculate_all_metrics()
    finally:
        calculator.close()


def cluster_sites(n_clusters: int = 5):
    """
    Cluster similar sites
    
    Args:
        n_clusters: Number of clusters
    """
    print("\n" + "="*80)
    print("STEP 4: SITE CLUSTERING")
    print("="*80 + "\n")
    
    clusterer = SiteClusterer(n_clusters=n_clusters)
    try:
        clusters = clusterer.cluster_sites()
        
        # Print cluster details
        print("\n📊 Detailed Cluster Information:")
        for cluster_id, sites in clusters.items():
            print(f"\n--- Cluster {cluster_id} ---")
            print(f"Sites: {len(sites)}")
            characteristics = clusterer.get_cluster_characteristics(cluster_id)
            for key, value in characteristics.items():
                print(f"  {key}: {value}")
    finally:
        clusterer.close()


def run_full_pipeline(
    condition: str = "cancer",
    phase: str = None,
    max_pages: int = 5,
    n_clusters: int = 5
):
    """
    Run complete pipeline
    
    Args:
        condition: Disease condition to search
        phase: Study phase filter
        max_pages: Maximum pages to fetch
        n_clusters: Number of clusters
    """
    print("\n" + "="*80)
    print("🚀 CLINICAL TRIAL SITE EVALUATION SYSTEM")
    print("="*80)
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    
    # Run pipeline
    extract_data(condition, phase, max_pages)
    aggregate_sites()
    calculate_metrics()
    cluster_sites(n_clusters)
    
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\n💡 Next steps:")
    print("  1. Run the dashboard: streamlit run src/dashboard/app.py")
    print("  2. View the results in your web browser")
    print("\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Clinical Trial Site Evaluation System"
    )
    
    parser.add_argument(
        "command",
        choices=["init", "extract", "aggregate", "metrics", "cluster", "pipeline", "dashboard"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--condition",
        default="cancer",
        help="Disease condition to search (default: cancer)"
    )
    
    parser.add_argument(
        "--phase",
        help="Study phase filter (e.g., 'Phase 3')"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum pages to fetch from API (default: 5)"
    )
    
    parser.add_argument(
        "--n-clusters",
        type=int,
        default=5,
        help="Number of clusters for site grouping (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == "init":
        print("📦 Initializing database...")
        init_db()
    
    elif args.command == "extract":
        init_db()
        extract_data(args.condition, args.phase, args.max_pages)
    
    elif args.command == "aggregate":
        aggregate_sites()
    
    elif args.command == "metrics":
        calculate_metrics()
    
    elif args.command == "cluster":
        cluster_sites(args.n_clusters)
    
    elif args.command == "pipeline":
        run_full_pipeline(args.condition, args.phase, args.max_pages, args.n_clusters)
    
    elif args.command == "dashboard":
        import os
        os.system("streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    main()
