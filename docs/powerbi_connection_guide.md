# Power BI Connection Guide
## Connecting to PostgreSQL for Chapin Hall Capstone

---

## Prerequisites

1. Power BI Desktop installed
2. PostgreSQL running with chapinhall_capstone database
3. Data loaded into the database

---

## Step 1: Get PostgreSQL ODBC Driver

### Option A: Use built-in PostgreSQL connector (Recommended)
Power BI has a native PostgreSQL connector. No additional drivers needed!

### Option B: Install ODBC driver (if needed)
Download from: https://www.postgresql.org/ftp/odbc/versions/msi/

---

## Step 2: Connect Power BI to PostgreSQL

1. **Open Power BI Desktop**

2. **Get Data**
   - Click "Get Data" on the Home ribbon
   - Search for "PostgreSQL"
   - Select "PostgreSQL database"
   - Click "Connect"

3. **Enter Connection Details**
   ```
   Server: localhost
   Database: chapinhall_capstone
   ```
   - Click "OK"

4. **Authentication**
   - Select "Database" authentication
   - Username: `postgres`
   - Password: ''
   - Click "Connect"

5. **Navigator Window**
   - You'll see a list of all tables and views
   - **Select these views** (recommended):
     - ✅ `child_episode`
     - ✅ `analysis_master`
     - ✅ `metrics_summary`
     - ✅ `disparities_race_county`
     - ✅ `monthly_trends`
   
6. **Load Options**
   - Choose "Load" to import data directly
   - Or choose "Transform Data" to clean/modify in Power Query

---

## Step 3: Recommended Data Model Setup

### Relationships (if loading multiple views)
- Usually not needed since views are pre-joined
- If using raw tables, create relationships:
  - `episodes[child_id]` → `children[child_id]`
  - `placements[episode_id]` → `episodes[episode_id]`

### Data Refresh
- Set up scheduled refresh if data changes frequently
- For static analysis, one-time load is sufficient

---

## Step 4: Key Measures to Create

Once data is loaded, create these DAX measures:

### 1. Total Children
```dax
Total Children = DISTINCTCOUNT(child_episode[child_id])
```

### 2. Active Episodes
```dax
Active Episodes = CALCULATE(
    COUNT(child_episode[episode_id]),
    child_episode[is_active] = TRUE
)
```

### 3. Long Stay Rate
```dax
Long Stay Rate = 
DIVIDE(
    COUNTROWS(FILTER(child_episode, child_episode[long_stay_3yr] = TRUE)),
    COUNTROWS(child_episode),
    0
) * 100
```

### 4. Average Episode Length
```dax
Avg Episode Length (Days) = AVERAGE(child_episode[episode_length_days])
```

### 5. Median Episode Length
```dax
Median Episode Length = 
PERCENTILE.INC(child_episode[episode_length_days], 0.5)
```

---

## Step 5: Recommended Visualizations

### Dashboard Page 1: Executive Overview

**KPI Cards:**
- Total Children
- Active Episodes
- Average Episode Length
- Long Stay Rate

**Charts:**
- Line chart: Monthly entries (use `monthly_trends`)
- Bar chart: Episodes by county (use `analysis_master`)
- Pie chart: Current episode status

### Dashboard Page 2: Length of Stay

**Charts:**
- Histogram: Distribution of episode length
- Box plot: Episode length by race
- Table: Summary statistics by demographic group
- Scatter plot: Age at entry vs. episode length

### Dashboard Page 3: Disparities

**Charts:**
- Clustered bar: Long stay rate by race and county
- Heat map: County x Race matrix
- Table: `disparities_race_county` view
- Tree map: Caseload by county and race

### Dashboard Page 4: Trends

**Charts:**
- Line chart: Entries over time (monthly)
- Area chart: Stacked race composition over time
- Column chart: Long stay rate by entry year
- Slicer: Date range selector

---

## Step 6: Filters and Slicers

Add these slicers for interactivity:

1. **County Slicer**
   - Field: `child_episode[initial_county]`
   - Type: Dropdown or List

2. **Race Slicer**
   - Field: `child_episode[race]`
   - Type: Dropdown or List

3. **Entry Year Slicer**
   - Field: `child_episode[entry_year]`
   - Type: Slider

4. **Age Group Slicer**
   - Create calculated column first:
   ```dax
   Age Group = 
   SWITCH(
       TRUE(),
       child_episode[age_at_entry_years] < 1, "Infant",
       child_episode[age_at_entry_years] < 6, "Young Child",
       child_episode[age_at_entry_years] < 13, "School Age",
       "Teen"
   )
   ```

5. **Episode Status**
   - Field: `child_episode[episode_status]`
   - Type: Button or List

---

## Step 7: Color Schemes (Equity-Focused)

Use colorblind-friendly palettes:

### Race/Ethnicity
- Black: `#1f77b4` (blue)
- White: `#ff7f0e` (orange)
- Hispanic: `#2ca02c` (green)
- Asian: `#d62728` (red)
- Other: `#9467bd` (purple)

### Status Indicators
- Active: `#2ca02c` (green)
- Closed: `#d62728` (red)
- Long Stay: `#ff7f0e` (orange)

---

## Step 8: Performance Optimization

### For Large Datasets
1. **Import vs. DirectQuery**
   - Use Import mode for <1M rows
   - Use DirectQuery for larger datasets

2. **Aggregations**
   - Pre-aggregate in SQL views (already done!)
   - Use `metrics_summary` view for high-level KPIs

3. **Relationships**
   - Minimize relationship complexity
   - Use star schema if possible

---

## Step 9: Publishing & Sharing

### Option 1: Share .pbix file
- Save your Power BI file
- Share via email or cloud storage
- Recipients need Power BI Desktop to view

### Option 2: Publish to Power BI Service
- Click "Publish" in Power BI Desktop
- Sign in with organizational account
- Select workspace
- Share via web link (requires Power BI Pro)

### Option 3: Export to PDF/PowerPoint
- File → Export → PDF or PowerPoint
- Static version for presentations

---

## Troubleshooting

### Connection Issues

**Error: "Could not connect to server"**
- Check PostgreSQL is running: `sudo service postgresql status`
- Verify database exists: `psql -U postgres -l`
- Check firewall settings

**Error: "Authentication failed"**
- Verify username/password
- Check `pg_hba.conf` allows connections
- Try empty password if using trust auth

### Data Issues

**No data appearing**
- Check views have data: `SELECT COUNT(*) FROM child_episode;`
- Verify ETL ran successfully
- Check filters aren't excluding all data

**Performance Issues**
- Reduce number of visuals per page
- Use aggregated views instead of raw tables
- Enable query folding in Power Query

---

## Quick Reference: SQL Views for Power BI

### Best Views to Use

| View Name | Purpose | Row Count |
|-----------|---------|-----------|
| `child_episode` | Main analysis view | ~400 |
| `analysis_master` | Comprehensive data | ~400 |
| `metrics_summary` | KPIs | 1 |
| `disparities_race_county` | Equity analysis | ~25 |
| `monthly_trends` | Time series | ~36 |

### When to Use Each

- **Quick KPIs**: `metrics_summary`
- **Demographic analysis**: `child_episode`
- **Detailed exploration**: `analysis_master`
- **Equity focus**: `disparities_race_county`
- **Time trends**: `monthly_trends`

---

## Sample Power BI Report Template

Coming soon: Download a pre-built template at:
`viz/chapinhall_template.pbix`

---

## Resources

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Guide](https://dax.guide/)
- [PostgreSQL Connector](https://docs.microsoft.com/power-bi/connect-data/desktop-connect-postgres)

---

**Questions?** Check the main README or contact the project team.
