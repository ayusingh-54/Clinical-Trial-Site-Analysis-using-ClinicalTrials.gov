# 🚀 Deployment Guide - Streamlit Cloud

## The Problem

Your app is deployed on Streamlit Cloud but the SQLite database (`clinical_trials.db`) doesn't exist there, causing the error:

```
cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: site_master
```

## 💡 Solutions (Choose One)

### Option 1: Upload Database to GitHub (Simplest - 5 minutes)

**Best for**: Demo/prototype with existing data

#### Steps:

1. **Check database file size** (must be < 100MB for GitHub):

   ```powershell
   (Get-Item "data\clinical_trials.db").Length / 1MB
   ```

2. **If < 100MB, commit and push**:

   ```powershell
   git add data/clinical_trials.db
   git commit -m "Add database file for deployment"
   git push origin main
   ```

3. **If > 100MB, use Git LFS**:

   ```powershell
   git lfs install
   git lfs track "*.db"
   git add .gitattributes data/clinical_trials.db
   git commit -m "Add database with Git LFS"
   git push origin main
   ```

4. **Redeploy on Streamlit Cloud** - it will automatically pick up the changes

**Pros**:
✅ Quick setup  
✅ Works immediately  
✅ No additional services needed

**Cons**:
❌ Data is static (no updates without redeployment)  
❌ File size limited  
❌ All data is public on GitHub

---

### Option 2: PostgreSQL Cloud Database (Recommended for Production)

**Best for**: Production app with live data

#### A. Create PostgreSQL Database (Choose One Service):

**Supabase (Easiest - Free Tier)**:

1. Go to https://supabase.com/
2. Create account and new project
3. Copy the connection string (Settings → Database → Connection String → URI)
4. Format: `postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres`

**Railway (Simple - Free Tier)**:

1. Go to https://railway.app/
2. Create account and new project
3. Add PostgreSQL database
4. Copy connection string from Variables tab

**Heroku (Classic - Free tier discontinued but reliable)**:

1. Go to https://www.heroku.com/postgres
2. Create Heroku Postgres database
3. Copy DATABASE_URL from settings

#### B. Update Your App:

1. **Install PostgreSQL driver**:
   Add to `requirements.txt`:

   ```
   psycopg2-binary>=2.9.0
   ```

2. **Set Environment Variable in Streamlit Cloud**:

   - Go to your app settings on Streamlit Cloud
   - Click "Secrets" (or Advanced Settings → Secrets)
   - Add:
     ```toml
     DATABASE_URL = "postgresql://user:password@host:port/database"
     ```

3. **Update config.py** (already supports this):

   ```python
   DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/clinical_trials.db")
   ```

4. **Migrate Data** (Run locally):

   ```powershell
   # Export from SQLite
   python -c "
   from src.database.models import get_session, SiteMaster
   import pandas as pd
   session = get_session()
   sites = session.query(SiteMaster).all()
   # Export logic here
   "

   # Or use a migration tool
   pip install pgloader  # If needed
   ```

**Pros**:
✅ Production-ready  
✅ Scalable  
✅ Can update data live  
✅ Keeps data private

**Cons**:
❌ More setup required  
❌ Need to migrate data  
❌ May need paid plan for larger datasets

---

### Option 3: Generate Data on Startup (Self-Contained)

**Best for**: Demo app that regenerates data each time

#### Create `init_data.py`:

```python
"""Initialize database with sample data on startup"""
import os
from src.database.models import init_db, get_session
from src.data_extraction.data_loader import ClinicalTrialsDataLoader
from src.data_processing.site_aggregator import SiteAggregator
from src.metrics.calculator import MetricsCalculator
from pathlib import Path

def initialize_system():
    """Initialize database and load minimal data"""
    db_path = Path("data/clinical_trials.db")

    # Skip if database already exists
    if db_path.exists():
        print("✅ Database already exists")
        return

    print("🔄 Initializing database...")
    init_db()

    print("🔄 Loading sample data (50 trials)...")
    loader = ClinicalTrialsDataLoader()
    loader.load_trials(
        condition="cancer",
        phase="PHASE3",
        max_pages=1  # Just 50 trials for demo
    )

    print("🔄 Aggregating sites...")
    aggregator = SiteAggregator()
    aggregator.aggregate_all_sites()

    print("🔄 Calculating metrics...")
    calculator = MetricsCalculator()
    calculator.calculate_all_metrics()

    print("✅ Initialization complete!")

if __name__ == "__main__":
    initialize_system()
```

#### Update `app.py` to auto-initialize:

Add at the top of `main()`:

```python
def main():
    # Initialize database on first run
    from pathlib import Path
    if not Path("data/clinical_trials.db").exists():
        with st.spinner("⏳ Initializing database (first run only)..."):
            try:
                from init_data import initialize_system
                initialize_system()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to initialize: {e}")
                st.info("Please check logs and try redeploying")
                return

    # ... rest of your code ...
```

**Pros**:
✅ Self-contained  
✅ No external dependencies  
✅ Always up-to-date data

**Cons**:
❌ Slow first load (2-5 minutes)  
❌ Limited to small datasets  
❌ Uses Streamlit Cloud compute time

---

## 🎯 Quick Fix (Immediate)

For **right now** to stop the error, I've updated the app to handle missing database gracefully. It will show:

```
⚠️ No data available. Please run data extraction first.
```

Instead of crashing. But you still need to choose one of the options above to actually display data.

---

## 📋 Recommended Approach (Step-by-Step)

### For Demo/Testing: Option 1 (GitHub Upload)

```powershell
# 1. Check size
(Get-Item "data\clinical_trials.db").Length / 1MB

# 2. If under 100MB:
git add data/clinical_trials.db
git commit -m "Add database for Streamlit Cloud deployment"
git push origin main

# 3. Done! Streamlit Cloud will auto-redeploy
```

### For Production: Option 2 (PostgreSQL)

```powershell
# 1. Create Supabase account & project
# 2. Copy connection string

# 3. Add to Streamlit Cloud Secrets:
DATABASE_URL = "postgresql://postgres:yourpassword@db.xxx.supabase.co:5432/postgres"

# 4. Update requirements.txt:
echo "psycopg2-binary>=2.9.0" >> requirements.txt

# 5. Export and import data:
python export_to_postgres.py  # Create this script

# 6. Push changes:
git add requirements.txt
git commit -m "Add PostgreSQL support"
git push origin main
```

---

## 🔍 Current Status

✅ **App code fixed** - Won't crash on missing database  
⚠️ **Need to add database** - Choose option above  
✅ **All dependencies correct** - requirements.txt is good  
✅ **Code is deployment-ready** - Just needs data

---

## 📞 Support

**If you see this error**:

```
no such table: site_master
```

→ Database file missing, follow Option 1 or 2 above

**If deployment is slow**:
→ Normal for first Streamlit Cloud deploy (1-2 minutes)

**If you want to test locally first**:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run src/dashboard/app.py
```

---

## 🎬 Next Steps

1. **Choose your option** (I recommend Option 1 for demo, Option 2 for production)
2. **Follow the steps** above
3. **Commit and push** changes
4. **Streamlit Cloud auto-redeploys**
5. **Test your app** at your Streamlit URL

Need help? Let me know which option you want to use! 🚀
