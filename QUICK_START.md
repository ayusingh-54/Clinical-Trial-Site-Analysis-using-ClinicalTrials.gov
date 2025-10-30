# 🚀 Quick Start Guide - Clinical Trial Site Evaluation System

## ⚡ TL;DR - Get Started in 3 Steps

### Step 1: Activate Virtual Environment

```powershell
cd c:\Users\ayusi\Desktop\assiment
.\.venv\Scripts\Activate.ps1
```

### Step 2: Run Full Pipeline (Extract Data)

```powershell
python main.py pipeline --condition "cancer" --phase "Phase 3" --max-pages 3
```

### Step 3: Launch Dashboard

```powershell
streamlit run src/dashboard/app.py
```

Open browser: http://localhost:8501

---

## 📋 Common Commands Reference

### Virtual Environment

```powershell
# Activate
.\.venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Data Pipeline Commands

**Full Pipeline** (Recommended for first use)

```powershell
python main.py pipeline --condition "cancer" --max-pages 3
```

**Extract Data Only**

```powershell
# Cancer trials
python main.py extract --condition "cancer" --max-pages 5

# Diabetes trials
python main.py extract --condition "diabetes" --max-pages 5

# With phase filter
python main.py extract --condition "cancer" --phase "Phase 3" --max-pages 3
```

**Process Data**

```powershell
# Aggregate sites
python main.py aggregate

# Calculate metrics
python main.py metrics

# Cluster sites
python main.py cluster --n-clusters 5
```

**Database**

```powershell
# Initialize/Reset database
python main.py init
```

**Dashboard**

```powershell
# Launch dashboard
streamlit run src/dashboard/app.py

# Or use main.py
python main.py dashboard
```

---

## 🎯 Use Cases

### Use Case 1: Evaluate Cancer Trial Sites

```powershell
# Extract cancer trials
python main.py pipeline --condition "cancer" --phase "Phase 3" --max-pages 5

# Launch dashboard
streamlit run src/dashboard/app.py

# In dashboard:
# 1. Go to "Leaderboard" tab
# 2. Sort by completion rate
# 3. View top performers
```

### Use Case 2: Find Best Sites for New Study

```powershell
# Make sure data is loaded
python main.py pipeline --condition "cancer" --max-pages 3

# Launch dashboard
streamlit run src/dashboard/app.py

# In dashboard sidebar:
# 1. Enter Target Condition: "cancer"
# 2. Select Target Phase: "Phase 3"
# 3. Choose Target Country: "United States"
# 4. Click "Find Best Sites"
# 5. View top 10 recommendations
```

### Use Case 3: Analyze Global Site Distribution

```powershell
# Extract diverse data
python main.py extract --condition "cancer" --max-pages 5

# Process data
python main.py aggregate
python main.py metrics

# Launch dashboard
streamlit run src/dashboard/app.py

# In dashboard:
# 1. Go to "Global Map" tab
# 2. Explore site distribution
# 3. Use filters to focus on regions
```

### Use Case 4: Compare Therapeutic Areas

```powershell
# Extract multiple conditions
python main.py extract --condition "cancer" --max-pages 3
python main.py extract --condition "diabetes" --max-pages 3

# Aggregate and calculate
python main.py aggregate
python main.py metrics

# View in dashboard
streamlit run src/dashboard/app.py

# Use "Therapeutic Area" filter in sidebar
```

---

## 🔧 Troubleshooting Quick Fixes

### Problem: Dashboard shows "No data available"

**Solution:**

```powershell
# Run pipeline first
python main.py pipeline --condition "cancer" --max-pages 3
```

### Problem: Import errors

**Solution:**

```powershell
# Reactivate environment
.\.venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

### Problem: Database errors

**Solution:**

```powershell
# Reset database
rm data/clinical_trials.db
python main.py init
python main.py pipeline --condition "cancer" --max-pages 3
```

### Problem: Dashboard won't start

**Solution:**

```powershell
# Check if port is in use, try:
streamlit run src/dashboard/app.py --server.port 8502
```

### Problem: Slow data extraction

**Solution:**

```powershell
# Reduce number of pages
python main.py extract --condition "cancer" --max-pages 2
```

---

## 📊 Dashboard Navigation Guide

### Tab 1: Overview 📊

- View summary statistics
- See country distribution
- Analyze study status
- Compare completion rates

### Tab 2: Global Map 🗺️

- Interactive world map
- Site density by country
- Hover for details

### Tab 3: Leaderboard 🏆

- Top 20 performing sites
- Sortable table
- Performance charts

### Tab 4: Analytics 📈

- Data quality distribution
- Experience analysis
- Correlation heatmap

### Tab 5: Site Details 📋

- Select any site
- View detailed metrics
- See strengths/weaknesses

### Sidebar: Filters & Recommender 🎯

- Filter by country
- Filter by study count
- Filter by therapeutic area
- **Site Recommender**: Find best sites for your study

---

## 💡 Pro Tips

### Tip 1: Fetch More Data

```powershell
# Default is 5 pages (~500 trials)
python main.py pipeline --condition "cancer" --max-pages 10

# Each page = ~100 trials
```

### Tip 2: Multiple Conditions

```powershell
# Extract different conditions
python main.py extract --condition "cancer" --max-pages 5
python main.py extract --condition "diabetes" --max-pages 5
python main.py extract --condition "alzheimer" --max-pages 5

# Then aggregate
python main.py aggregate
python main.py metrics
```

### Tip 3: Customize Clustering

```powershell
# More clusters for finer grouping
python main.py cluster --n-clusters 10

# Fewer clusters for broader groups
python main.py cluster --n-clusters 3
```

### Tip 4: Focus on Specific Phase

```powershell
# Only Phase 3 trials
python main.py extract --condition "cancer" --phase "Phase 3" --max-pages 5

# Only Phase 2 trials
python main.py extract --condition "diabetes" --phase "Phase 2" --max-pages 5
```

### Tip 5: Export Data from Dashboard

In the dashboard:

1. View any table
2. Click the download icon (top right)
3. Export to CSV

---

## 📦 Package Management

### Install New Package

```powershell
.\.venv\Scripts\Activate.ps1
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

### Update Packages

```powershell
pip install --upgrade package-name
```

### List Installed Packages

```powershell
pip list
```

---

## 🎓 Understanding the Data

### Site Metrics Explained

**Total Studies**: Number of trials at this site
**Completed**: Successfully finished trials
**Ongoing**: Currently active trials
**Terminated**: Stopped early
**Completion %**: Success rate = Completed / (Completed + Terminated + Withdrawn)
**Data Quality**: Score based on completeness and recency (0-1)
**Experience Index**: Total number of studies (expertise measure)

### Match Score Formula

```
Match Score =
  0.4 × Therapeutic Area Match +
  0.2 × Phase Similarity +
  0.2 × Intervention Match +
  0.2 × Regional Proximity
```

### Cluster Groups

- **Cluster 0**: Low activity sites
- **Cluster 1**: Medium activity, high quality
- **Cluster 2**: High experience sites
- **Cluster 3**: Medium activity, lower quality
- **Cluster 4**: Low activity, high quality

---

## 🔄 Typical Workflow

### Initial Setup (One Time)

```powershell
cd c:\Users\ayusi\Desktop\assiment
.\.venv\Scripts\Activate.ps1
python main.py init
```

### Daily Use

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Update data (optional)
python main.py extract --condition "cancer" --max-pages 5

# Launch dashboard
streamlit run src/dashboard/app.py
```

### Weekly/Monthly Updates

```powershell
# Full refresh
python main.py pipeline --condition "cancer" --max-pages 10

# Or update specific conditions
python main.py extract --condition "diabetes" --max-pages 5
python main.py aggregate
python main.py metrics
```

---

## 📱 Keyboard Shortcuts (Dashboard)

- `Ctrl + R`: Refresh dashboard
- `Ctrl + Shift + R`: Clear cache and refresh
- `Ctrl + C` (in terminal): Stop dashboard

---

## 🎯 Performance Tips

### Faster Data Loading

- Reduce `--max-pages` parameter
- Use specific phase filters
- Focus on one condition at a time

### Faster Dashboard

- Use filters to reduce displayed data
- Clear cache: Settings → Clear cache

### Database Performance

- Regularly clean old data
- Consider PostgreSQL for >10,000 sites

---

## 📞 Quick Reference

**Project Location**: `c:\Users\ayusi\Desktop\assiment`
**Dashboard URL**: http://localhost:8501
**Database Location**: `data/clinical_trials.db`
**Virtual Environment**: `.venv/`

**Main Commands**:

- Pipeline: `python main.py pipeline`
- Dashboard: `streamlit run src/dashboard/app.py`
- Help: `python main.py --help`

---

## ✅ Pre-Flight Checklist

Before starting:

- [ ] Virtual environment activated
- [ ] Database initialized
- [ ] Data extracted (at least once)
- [ ] Dashboard accessible at localhost:8501

If any checkbox is unchecked:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py pipeline --condition "cancer" --max-pages 3
streamlit run src/dashboard/app.py
```

---

**Ready to use! 🚀 Happy analyzing!**
