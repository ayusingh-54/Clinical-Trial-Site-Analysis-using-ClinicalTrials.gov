"""
Enhanced debug script to show comprehensive statistics
"""
from src.database.models import get_session, ClinicalTrial, TrialLocation, SiteMaster

session = get_session()

print("=" * 80)
print("COMPREHENSIVE SYSTEM ANALYSIS")
print("=" * 80)

# Trial statuses
print("\n📊 TRIAL STATUS BREAKDOWN")
print("-" * 80)
statuses = session.query(ClinicalTrial.status).distinct().all()
for s in statuses:
    if s[0]:
        count = session.query(ClinicalTrial).filter_by(status=s[0]).count()
        pct = (count / 300) * 100
        print(f"  {s[0]:30s}: {count:3d} trials ({pct:5.1f}%)")

# Site statistics
print("\n📊 SITE COMPLETION STATISTICS")
print("-" * 80)

sites_with_completed = session.query(SiteMaster).filter(
    SiteMaster.completed_studies > 0
).count()
print(f"Sites with completed studies: {sites_with_completed}")

sites_with_ongoing = session.query(SiteMaster).filter(
    SiteMaster.ongoing_studies > 0
).count()
print(f"Sites with ongoing studies: {sites_with_ongoing}")

sites_with_terminated = session.query(SiteMaster).filter(
    SiteMaster.terminated_studies > 0
).count()
print(f"Sites with terminated studies: {sites_with_terminated}")

# Completion ratio distribution
print("\n📊 COMPLETION RATIO DISTRIBUTION")
print("-" * 80)

high_performers = session.query(SiteMaster).filter(
    SiteMaster.completion_ratio >= 0.8
).count()
print(f"High performers (≥80% completion): {high_performers}")

good_performers = session.query(SiteMaster).filter(
    SiteMaster.completion_ratio >= 0.5,
    SiteMaster.completion_ratio < 0.8
).count()
print(f"Good performers (50-79% completion): {good_performers}")

poor_performers = session.query(SiteMaster).filter(
    SiteMaster.completion_ratio > 0,
    SiteMaster.completion_ratio < 0.5
).count()
print(f"Poor performers (1-49% completion): {poor_performers}")

no_completed = session.query(SiteMaster).filter(
    SiteMaster.completion_ratio == 0
).count()
print(f"No completed studies: {no_completed}")

# Top performing sites
print("\n🏆 TOP 20 SITES BY COMPLETION RATE")
print("-" * 80)

top_sites = session.query(SiteMaster).filter(
    SiteMaster.total_studies >= 2,  # At least 2 studies for meaningful data
    SiteMaster.completion_ratio > 0
).order_by(
    SiteMaster.completion_ratio.desc(),
    SiteMaster.total_studies.desc()
).limit(20).all()

for i, site in enumerate(top_sites, 1):
    print(f"\n{i}. {site.site_name[:50]}")
    print(f"   Country: {site.country}")
    print(f"   Total: {site.total_studies} | Completed: {site.completed_studies} | "
          f"Ongoing: {site.ongoing_studies} | Terminated: {site.terminated_studies}")
    print(f"   Completion Rate: {site.completion_ratio * 100:.1f}%")

# Sites by experience
print("\n\n📈 SITES BY EXPERIENCE LEVEL")
print("-" * 80)

high_exp = session.query(SiteMaster).filter(
    SiteMaster.total_studies >= 10
).count()
print(f"High experience (≥10 studies): {high_exp}")

medium_exp = session.query(SiteMaster).filter(
    SiteMaster.total_studies >= 5,
    SiteMaster.total_studies < 10
).count()
print(f"Medium experience (5-9 studies): {medium_exp}")

low_exp = session.query(SiteMaster).filter(
    SiteMaster.total_studies >= 2,
    SiteMaster.total_studies < 5
).count()
print(f"Low experience (2-4 studies): {low_exp}")

single_study = session.query(SiteMaster).filter(
    SiteMaster.total_studies == 1
).count()
print(f"Single study sites: {single_study}")

# Country distribution
print("\n\n🌍 TOP 20 COUNTRIES BY NUMBER OF SITES")
print("-" * 80)

from sqlalchemy import func
country_stats = session.query(
    SiteMaster.country,
    func.count(SiteMaster.id).label('site_count'),
    func.sum(SiteMaster.total_studies).label('total_studies'),
    func.sum(SiteMaster.completed_studies).label('completed_studies')
).group_by(
    SiteMaster.country
).order_by(
    func.count(SiteMaster.id).desc()
).limit(20).all()

for country, sites, total, completed in country_stats:
    completion_rate = (completed / total * 100) if total > 0 else 0
    print(f"  {country:30s}: {sites:4d} sites, {total:4d} studies, "
          f"{completed:4d} completed ({completion_rate:5.1f}%)")

session.close()

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
