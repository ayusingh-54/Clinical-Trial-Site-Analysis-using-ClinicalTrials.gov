"""
Debug script to check trial statuses and completion data
"""
from src.database.models import get_session, ClinicalTrial, TrialLocation, SiteMaster

session = get_session()

# Check trial statuses
print("=" * 80)
print("TRIAL STATUS ANALYSIS")
print("=" * 80)

statuses = session.query(ClinicalTrial.status).distinct().all()
print(f"\nUnique status values ({len(statuses)}):")
for s in statuses:
    if s[0]:
        count = session.query(ClinicalTrial).filter_by(status=s[0]).count()
        print(f"  {s[0]}: {count} trials")

# Check total trials
total_trials = session.query(ClinicalTrial).count()
print(f"\n Total trials in database: {total_trials}")

# Check locations
total_locations = session.query(TrialLocation).count()
print(f"Total locations in database: {total_locations}")

# Check sites
total_sites = session.query(SiteMaster).count()
print(f"Total sites in site_master: {total_sites}")

# Sample some sites with their stats
print("\n" + "=" * 80)
print("SAMPLE SITE STATISTICS")
print("=" * 80)

sites = session.query(SiteMaster).limit(10).all()
for site in sites:
    print(f"\nSite: {site.site_name}")
    print(f"  Country: {site.country}")
    print(f"  Total Studies: {site.total_studies}")
    print(f"  Completed: {site.completed_studies}")
    print(f"  Ongoing: {site.ongoing_studies}")
    print(f"  Terminated: {site.terminated_studies}")
    print(f"  Completion Ratio: {site.completion_ratio}")

session.close()
