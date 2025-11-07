# Chapin Hall Capstone Project
## Child Welfare Data Analysis & Predictive Modeling

**Author**: Ali Karaduman (Mike) 
**Organization**: Chapin Hall at the University of Chicago  
**Project Duration**: [Start Date] - [End Date]

---

## 📋 Project Overview

This capstone project analyzes child welfare data to identify patterns in out-of-home care, with a focus on:
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

## 🗂️ Project Structure

```
chapinhall-capstone/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore
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
    └── dashboard_guide.md       # Dashboard documentation
```

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

## 📊 Database Schema

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

## 📈 Key Metrics

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

## 🔬 Analysis Methods

### 1. Exploratory Data Analysis (EDA)
- Descriptive statistics
- Distribution analysis
- Correlation exploration
- Visualization of key patterns

**Notebook**: `src/analysis/eda_child_episodes.ipynb`

### 2. Multilevel Modeling
- Hierarchical structure (children nested in counties)
- Random effects for county-level variation
- Fixed effects for individual predictors
- Intraclass correlation analysis

**Notebook**: `src/analysis/multilevel_longstay.ipynb`

### 3. Survival Analysis
- Cox proportional hazards models
- Time-to-exit predictions
- Kaplan-Meier curves by demographics

### 4. Natural Language Processing
- Case note preprocessing
- Topic modeling with LDA
- Keyword extraction
- Sentiment analysis (if applicable)

**Notebook**: `src/nlp/topics_keywords_demo.ipynb`

### 5. Policy Simulations
- "What-if" scenarios for interventions
- Cost-benefit analysis framework
- Monte Carlo simulations

---

## 📊 Power BI Dashboard

The interactive dashboard includes:

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

## 🧪 Testing & Data Quality

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

## 📝 Deliverables

- ✅ Database schema
- ✅ ETL pipeline
- ✅ Sample data generation
- ✅ EDA notebook
- □ Multilevel models
- □ Methods documentation
- □ Power BI dashboard
- □ Dashboard guide
- □ Final presentation
- □ Final report
- □ Code documentation
- □ Presentation deck

---

## 🛠️ Tech Stack

- **Database**: PostgreSQL 16
- **ETL**: Python (pandas, psycopg2, SQLAlchemy)
- **Analysis**: Python (numpy, pandas, scipy, statsmodels)
- **Visualization**: matplotlib, seaborn, Power BI
- **NLP**: scikit-learn, spacy (optional)
- **Testing**: pytest
- **Version Control**: Git/GitHub

---

## 📚 References

1. Chapin Hall. (2023). *Child Welfare Data Guidelines*
2. U.S. DHHS. (2023). *AFCARS Data Standards*
3. []
4. []

---

## 🤝 Contributing

This is an academic capstone project. For questions or collaboration:
- Email: makaraduman@gmail.com
- LinkedIn: /makaraduman

---

## 📄 License

This project is for academic purposes. Data is synthetic and does not represent real individuals.

---

## 🙏 Acknowledgments

- Chapin Hall at the University of Chicago

---

**Last Updated**: November 2025