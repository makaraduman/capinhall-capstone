# Child Welfare Capstone Project
## Child Welfare Data Analysis & Predictive Modeling
---
> **Author**: Ali Karaduman (Mike)
> **Project Duration**: 11/1/2025 - 11/11/2025
---

## Project Overview

This capstone project analyzes synthetic child welfare data to identify patterns in out-of-home care, with a focus on delivering actionable insights through data science. The project addresses key challenges in child protective services by focusing on:

- **Length of stay** in foster care
- **Demographic disparities** across race and geography
- **Placement stability** and movement patterns
- **Predictive modeling** for long-stay risk
- **Natural language processing** of case notes

### Key Research Questions
1. What factors predict extended stays (3+ years) in foster care?
2. Are there racial or geographic disparities in length of stay?
3. How does placement stability impact outcomes?
4. Can we identify early indicators of long-stay risk?

---

## System Architecture and Design Rationale

**Data Flow and Component Boundaries**
1. **Data Ingestion (ETL Layer):** Raw synthetic data is processed by the Python-based ETL pipeline (`src/etl/load_raw.py`) and loaded into the PostgreSQL database.

2. **Persistence Layer:** PostgreSQL serves as the single source of truth, managing relational data integrity via schemas defined in `sql/`.

3. **Analysis Layer:** Python scripts and Jupyter notebooks (`src/analysis/`) consume data directly from the processed views in the database to execute complex statistical and machine learning models.

4. **Presentation Layer:** The Power BI Dashboard connects to aggregated database views (`analysis_master`) to ensure visualizations reflect the most current state of the processed data.

### Key Design Decisions
A crucial aspect of this design was the selection of **PostgreSQL** as the database backend. This choice was made to support:

- **Transactional Integrity:** Essential for managing complex, time-series data related to child episodes and placements.

- **Advanced SQL Features:** Leveraging capabilities for defining complex, reusable analysis views (`analysis_master`) directly in the persistence layer, which streamlines downstream analysis in Python and Power BI.   

---

## Project Structure

```
child-welfare-capstone/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├──.gitignore
├── generate_sample_data.py      # Synthetic data generator
│
├── data/
│   ├── raw/                     # Original CSV files
│   ├── interim/                 # Intermediate processing
│   └── processed/               # Analysis-ready datasets
│
├── sql/
│   ├── 00_core_schema.sql       # Database schema
│   └── 02_transformations.sql   # Analysis views
│
├── src/
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── config.py            # Database configuration
│   │   └── load_raw.py          # ETL pipeline
│   │
│   ├── analysis/
│   │   ├── eda_child_episodes.ipynb       # Exploratory analysis
│   │   ├── multilevel_longstay.ipynb      # Multilevel modeling
│   │   └── causal_policy_sim.ipynb        # Policy simulations
│   │
│   ├── viz/
│   │   └── powerbi_dataset_notes.md       # Power BI documentation
│   │
│   └── nlp/
│       ├── notes_preprocess.py            # Text preprocessing
│       └── topics_keywords_demo.ipynb     # Topic modeling
│
├── tests/
│   ├── test_data_quality.py     # Data validation tests
│   └── test_metrics_consistency.py
│
└── docs/
    ├── erd.md                   # Entity relationship diagram
    ├── methods_brief.md         # Technical methods
    ├── dashboard_guide.md       # Dashboard documentation
    └── design_decisions.md      # Rationale for architectural choices ```

---

## 🚀 Quick Start

### Prerequisites
- PostgreSQL 16+
- Python 3.8+
- Jupyter Notebook
- Power BI Desktop (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/chapinhall-capstone.git
cd chapinhall-capstone
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**
```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
psql -U postgres -c "CREATE DATABASE chapinhall_capstone;"

# Load schema
psql -U postgres -d chapinhall_capstone -f sql/00_core_schema.sql
psql -U postgres -d chapinhall_capstone -f sql/02_transformations.sql
```

4. **Generate sample data** (if working with synthetic data)
```bash
python generate_sample_data.py
```

5. **Load data into database**
```bash
python src/etl/load_raw.py
```

6. **Launch Jupyter for analysis**
```bash
jupyter notebook src/analysis/eda_child_episodes.ipynb
```

---

## Database Schema

### Core Tables
- **children**: Demographic information (500 records)
- **cases**: Investigation/referral cases (300 records)
- **case_child**: Many-to-many relationship
- **episodes**: Out-of-home care episodes (400 records)
- **placements**: Living arrangements during episodes
- **allegations**: Maltreatment allegations
- **notes**: Case documentation and notes

### Analysis Views
- **child_episode**: Main analysis view combining demographics and episodes
- **episode_placements**: Placement summary per episode
- **analysis_master**: Comprehensive view for modeling
- **metrics_summary**: Aggregated KPIs
- **disparities_race_county**: Equity analysis
- **monthly_trends**: Time series data

See `docs/erd.md` for detailed schema documentation.

---

## Key Metrics

### Caseload Metrics
- Total children in system
- Active vs. closed episodes
- Monthly entry/exit rates

### Length of Stay
- Median and mean episode length
- Long-stay rates (2+ and 3+ years)
- Distribution by demographics

### Disparities
- Length of stay by race/ethnicity
- County-level variations
- Placement stability differences

### Placement Stability
- Average number of moves
- Current placement type
- Provider consistency

---

## Advanced Analysis and Modeling Methods

### 1. Exploratory Data Analysis (EDA)
- Descriptive statistics
- Distribution analysis
- Correlation exploration
- Visualization of key patterns

**Notebook**: `src/analysis/eda_child_episodes.ipynb`

### 2. Multilevel Modeling
- Hierarchical structure (children nested in counties) to account for non-independence of observations.
- Random effects for county-level variation and fixed effects for individual predictors.
- Intraclass correlation analysis.

**Notebook**: `src/analysis/multilevel_longstay.ipynb`

### 3. Survival Analysis
- Cox proportional hazards models for time-to-exit predictions.
- Kaplan-Meier curves stratified by key demographics to assess outcome disparities.

**Notebook**: `src/analysis/surival_analysis.ipynb`

### 4. Natural Language Processing
- Preprocessing of high-volume, unstructured case notes.
- Topic modeling (LDA) to identify underlying themes in case documentation.
- Keyword extraction and sentiment analysis (if applicable) for early risk detection.

**Notebook**: 'src/nlp/topics_keywords_demo.ipynb'

### 5. Policy Simulations
- "What-if" scenarios utilizing model outputs to simulate the impact of potential interventions (e.g., reducing placement moves).
- Cost-benefit analysis framework using Monte Carlo simulations.

**Notebook**: 'src/nlp/causal_policy_sim.ipynb'

---

## Power BI Dashboard (under construction)

The interactive dashboard will include:

### Page 1: Executive Summary
- Total caseload overview
- Entry/exit trends
- Key performance indicators

### Page 2: Length of Stay Analysis
- Distribution visualizations
- Long-stay breakdown
- Goal achievement tracking

### Page 3: Equity & Disparities
- Race-stratified metrics
- County comparison maps
- Disparity indicators

### Page 4: Placement Patterns
- Placement type distribution
- Stability metrics
- Provider analysis

**Access**: Connect Power BI to PostgreSQL using the `analysis_master` view.

See `docs/dashboard_guide.md` for detailed instructions.

---

##  Testing & Data Quality

Run data quality tests:
```bash
pytest tests/
```

Tests include:
- Null value checks
- Foreign key integrity
- Date logic validation
- Metric consistency
- Expected value ranges

---

## Project Status & Deliverables

| Deliverable           | Description                                                                               | Status          |
|-----------------------|-------------------------------------------------------------------------------------------|-----------------|
| Data & ETL            | "Database schema, ETL pipeline, and sample data generation"                               | ✅ Completed    |
| Exploratory Analysis  | EDA notebook and initial data visualizations                                              | ✅ Completed    |
| Modeling I            | Multilevel models and Survival Analysis implementation                                    | ✅ Completed    |
| Modeling II           | NLP Topic Modeling implementation                                                         | ✅ Completed    |
| Documentation         | Technical methods brief (methods_brief.md) and Design Decisions Log (design_decisions.md) | □ In Progress   |
| Visualization         | Power BI dashboard and accompanying guide (dashboard_guide.md)                            | □ In Progress   |
| Final Artifacts       | Final presentation deck and comprehensive technical report                                | □ To Be Started |
| Code Quality          | Comprehensive unit/integration tests and code documentation                               | □ In Progress   |
---

## Tech Stack

| Category                  | Technologies Used                                         |
|---------------------------|-----------------------------------------------------------|
| **Database**:             | PostgreSQL 16                                             |
| **ETL & Data Wrangling**  | Python (pandas, psycopg2, SQLAlchemy)                     |
| **Modeling & Analysis**   | Python (numpy, pandas, scipy, statsmodels, scikit-learn)  |
| **Visualization**         | matplotlib, seaborn, Power BI (optional)                  |
| **NLP**:                  | scikit-learn, spacy (optional)                            |
| **Testing**               | pytest                                                    |
| **Version Control**       | Git/GitHub                                                |

---

## References

1. Chapin Hall. (2023). *Child Welfare Data Guidelines*
2. U.S. DHHS. (2023). *AFCARS Data Standards*
3. []
4. []

---

## Contributing & Collaboration

This project is submitted as an academic capstone. While contributions are not actively solicited post-submission, the repository is structured for transparency, maintainability, and future extension.   
For academic inquiries, questions, or collaboration on potential extensions:
- Email: makaraduman@gmail.com
- LinkedIn: /makaraduman

---

## License

This project is licensed under the MIT License. All accompanying source code is open for modification and distribution under these terms. Data used is synthetic and does not represent real individuals.

A copy of the full license will be provided in the separate LICENSE.md file.


---

## Acknowledgments

- 

---

**Last Updated**: November 2025
