# 🚀 QUICK FIX - Deploy to Streamlit Cloud in 2 Minutes

## Your Issue

Your Streamlit Cloud app can't find the database because it's not in your GitHub repo.

## The Solution

Your database is only **5 MB** - perfect for GitHub! Just commit it.

## Steps (Copy & Paste)

### 1. Check Git Status

```powershell
git status
```

### 2. Add Database File

```powershell
git add data/clinical_trials.db
```

### 3. Commit Changes

```powershell
git commit -m "Add database file for Streamlit Cloud deployment"
```

### 4. Push to GitHub

```powershell
git push origin main
```

### 5. Wait for Streamlit Cloud

- Go to your Streamlit Cloud dashboard
- Wait 1-2 minutes for automatic redeployment
- Refresh your app URL

## Done! 🎉

Your app will now work on Streamlit Cloud with all 6,960 sites and 300 trials.

---

## Verify It Worked

After deploying, your app should show:

- **Overview Tab**: Summary statistics
- **Leaderboard Tab**: Top 20 sites with completion rates
- **Global Map**: Sites across 60+ countries
- **Analytics**: Charts and distributions

---

## If You Get Merge Conflicts

```powershell
git pull origin main --rebase
git push origin main
```

---

## Alternative: Use .gitignore (If You Don't Want Database in Repo)

If you'd rather not commit the database (for privacy/size), use PostgreSQL:

1. **Create Supabase account** (free): https://supabase.com
2. **Get connection string** from Settings → Database
3. **Add to Streamlit Secrets**:
   ```toml
   DATABASE_URL = "your-postgres-url-here"
   ```
4. **Migrate data**:
   ```powershell
   pip install psycopg2-binary
   python export_data.py postgres "your-postgres-url-here"
   ```

But for a demo/prototype, **just commit the database** - it's only 5 MB!
