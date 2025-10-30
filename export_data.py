"""
Export SQLite data to PostgreSQL or CSV for deployment
"""
import pandas as pd
from sqlalchemy import create_engine, inspect
from src.database.models import get_session, Base, ClinicalTrial, TrialLocation, SiteMaster, SitePerformance
import sys

def export_to_csv():
    """Export all tables to CSV files for backup"""
    print("📤 Exporting database to CSV files...")
    
    session = get_session()
    
    # Export Clinical Trials
    print("  → Exporting clinical_trials...")
    trials = session.query(ClinicalTrial).all()
    trials_data = [{
        'nct_id': t.nct_id,
        'title': t.title,
        'status': t.status,
        'study_type': t.study_type,
        'phase': t.phase,
        'start_date': t.start_date,
        'completion_date': t.completion_date,
        'enrollment': t.enrollment,
        'sponsor': t.sponsor,
        'conditions': t.conditions,
        'interventions': t.interventions,
        'last_update_date': t.last_update_date
    } for t in trials]
    pd.DataFrame(trials_data).to_csv('data/export_trials.csv', index=False)
    print(f"    ✅ {len(trials_data)} trials exported")
    
    # Export Trial Locations
    print("  → Exporting trial_locations...")
    locations = session.query(TrialLocation).all()
    locations_data = [{
        'trial_nct_id': session.query(ClinicalTrial).get(loc.trial_id).nct_id,
        'facility': loc.facility,
        'city': loc.city,
        'state': loc.state,
        'country': loc.country,
        'zip_code': loc.zip_code,
        'investigator': loc.investigator
    } for loc in locations]
    pd.DataFrame(locations_data).to_csv('data/export_locations.csv', index=False)
    print(f"    ✅ {len(locations_data)} locations exported")
    
    # Export Site Master
    print("  → Exporting site_master...")
    sites = session.query(SiteMaster).all()
    sites_data = [{
        'site_name': s.site_name,
        'city': s.city,
        'country': s.country,
        'total_studies': s.total_studies,
        'completed_studies': s.completed_studies,
        'ongoing_studies': s.ongoing_studies,
        'terminated_studies': s.terminated_studies,
        'withdrawn_studies': s.withdrawn_studies,
        'completion_ratio': s.completion_ratio,
        'data_quality_score': s.data_quality_score,
        'experience_index': s.experience_index,
        'avg_phase': s.avg_phase,
        'therapeutic_areas': s.therapeutic_areas,
        'primary_investigator': s.primary_investigator,
        'last_trial_date': s.last_trial_date,
        'strengths': s.strengths,
        'weaknesses': s.weaknesses
    } for s in sites]
    pd.DataFrame(sites_data).to_csv('data/export_sites.csv', index=False)
    print(f"    ✅ {len(sites_data)} sites exported")
    
    # Export Site Performance
    print("  → Exporting site_performance...")
    perf = session.query(SitePerformance).all()
    perf_data = [{
        'site_name': p.site_name,
        'match_score': p.match_score,
        'data_quality_score': p.data_quality_score,
        'completion_ratio': p.completion_ratio,
        'experience_index': p.experience_index
    } for p in perf]
    pd.DataFrame(perf_data).to_csv('data/export_performance.csv', index=False)
    print(f"    ✅ {len(perf_data)} performance records exported")
    
    session.close()
    print("\n✅ Export complete! Files saved in data/ directory")


def export_to_postgres(postgres_url: str):
    """Export SQLite data to PostgreSQL database"""
    print(f"📤 Exporting to PostgreSQL...")
    
    # Create PostgreSQL engine
    pg_engine = create_engine(postgres_url)
    
    # Create tables
    print("  → Creating tables...")
    Base.metadata.create_all(pg_engine)
    
    # Get SQLite session
    session = get_session()
    
    # Export each table
    tables = [
        (ClinicalTrial, 'clinical_trials'),
        (TrialLocation, 'trial_locations'),
        (SiteMaster, 'site_master'),
        (SitePerformance, 'site_performance')
    ]
    
    for model, table_name in tables:
        print(f"  → Migrating {table_name}...")
        
        # Read from SQLite
        data = session.query(model).all()
        
        if not data:
            print(f"    ⚠️ No data in {table_name}")
            continue
        
        # Convert to DataFrame
        df = pd.read_sql(session.query(model).statement, session.bind)
        
        # Write to PostgreSQL
        df.to_sql(table_name, pg_engine, if_exists='replace', index=False)
        print(f"    ✅ {len(df)} records migrated")
    
    session.close()
    print("\n✅ PostgreSQL migration complete!")


def check_database_size():
    """Check size of database file"""
    import os
    db_path = "data/clinical_trials.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    size_bytes = os.path.getsize(db_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print(f"\n📊 Database Statistics:")
    print(f"  File: {db_path}")
    print(f"  Size: {size_mb:.2f} MB")
    
    if size_mb < 100:
        print(f"  ✅ Safe to commit to GitHub (under 100 MB)")
    else:
        print(f"  ⚠️ Too large for GitHub (over 100 MB)")
        print(f"  💡 Consider using Git LFS or PostgreSQL")
    
    # Count records
    session = get_session()
    trials = session.query(ClinicalTrial).count()
    locations = session.query(TrialLocation).count()
    sites = session.query(SiteMaster).count()
    
    print(f"\n  Records:")
    print(f"    Trials: {trials:,}")
    print(f"    Locations: {locations:,}")
    print(f"    Sites: {sites:,}")
    
    session.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python export_data.py check          # Check database size")
        print("  python export_data.py csv            # Export to CSV files")
        print("  python export_data.py postgres <url> # Export to PostgreSQL")
        print("\nExample:")
        print("  python export_data.py postgres 'postgresql://user:pass@host:5432/db'")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "check":
        check_database_size()
    elif command == "csv":
        export_to_csv()
    elif command == "postgres":
        if len(sys.argv) < 3:
            print("❌ Error: PostgreSQL URL required")
            print("Example: python export_data.py postgres 'postgresql://user:pass@host:5432/db'")
            sys.exit(1)
        export_to_postgres(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
