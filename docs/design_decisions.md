# Design Decisions & Architecture Rationale
## Child Welfare Capstone Project

**Author**: [Your Name]  
**Date**: November 2024  
**Version**: 1.0

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Technology Stack Decisions](#technology-stack-decisions)
3. [Database Architecture](#database-architecture)
4. [ETL Pipeline Design](#etl-pipeline-design)
5. [Analytical Framework](#analytical-framework)
6. [Code Organization](#code-organization)
7. [Testing Strategy](#testing-strategy)
8. [Future Enhancements](#future-enhancements)

---

## Executive Summary

This document outlines the key architectural and design decisions made during the development of the Child Welfare Data Analytics capstone project. Each decision was driven by specific requirements related to data integrity, analytical flexibility, performance, and maintainability.

**Core Design Principles**:
1. **Data Integrity First**: Ensure accuracy and consistency of child welfare data
2. **Analytical Flexibility**: Support diverse analytical methods (statistical, ML, NLP)
3. **Scalability**: Design for potential growth in data volume
4. **Reproducibility**: Enable exact replication of analyses
5. **Maintainability**: Clear documentation and modular code

---

## Technology Stack Decisions

### Database: PostgreSQL

**Decision**: Use PostgreSQL 16 as the primary data store

**Rationale**:
- ✅ **ACID Compliance**: Critical for sensitive child welfare data
- ✅ **Advanced SQL Features**: Window functions, CTEs, materialized views
- ✅ **JSON Support**: Flexible for semi-structured data (e.g., case notes)
- ✅ **Extensibility**: PostGIS for potential geographic analysis
- ✅ **Open Source**: No licensing costs
- ✅ **Industry Standard**: High adoption in data analytics

**Alternatives Considered**:
- ❌ **MySQL**: Less advanced analytical features
- ❌ **SQLite**: Limited for multi-user scenarios, no native date types
- ❌ **NoSQL (MongoDB)**: Less suitable for relational data with integrity constraints

**Trade-offs**:
- PostgreSQL requires more initial setup than SQLite
- Steeper learning curve than MySQL
- **Verdict**: Benefits outweigh costs for this use case

---

### Programming Language: Python

**Decision**: Python 3.8+ as primary analytical language

**Rationale**:
- ✅ **Rich Ecosystem**: pandas, scikit-learn, statsmodels, gensim
- ✅ **Jupyter Integration**: Interactive analysis and documentation
- ✅ **Community Support**: Extensive documentation and tutorials
- ✅ **Data Science Standard**: Industry-wide adoption
- ✅ **Interoperability**: Easy integration with SQL, visualizations

**Alternatives Considered**:
- ❌ **R**: Strong statistical packages but less general-purpose
- ❌ **Julia**: Emerging, but smaller ecosystem
- ❌ **Scala/Spark**: Overkill for dataset size (~500 children)

---

### Visualization: Matplotlib/Seaborn + Power BI

**Decision**: Dual approach for different audiences

**Rationale**:
- **Matplotlib/Seaborn** (Python):
  - ✅ Tight integration with analysis code
  - ✅ Publication-quality static graphics
  - ✅ Full programmatic control
  - Use case: Notebooks, reports, academic papers

- **Power BI**:
  - ✅ Interactive dashboards
  - ✅ Business user-friendly
  - ✅ Real-time data connections
  - Use case: Stakeholder presentations, policy briefs

**Alternatives Considered**:
- ❌ **Tableau**: More expensive, less Python integration
- ❌ **D3.js**: Requires extensive web development
- ❌ **Plotly Dash**: Good but requires hosting infrastructure

---

## Database Architecture

### Schema Design: Normalized (3NF)

**Decision**: Normalize to Third Normal Form (3NF)

**Rationale**:
1. **Data Integrity**: Reduce redundancy and update anomalies
2. **Referential Integrity**: Enforce foreign key constraints
3. **Atomic Updates**: Changes to child demographics propagate correctly
4. **Query Flexibility**: Support diverse analytical queries

**Schema Overview**:
```
children (child_id PK)
  ├─→ case_child (child_id FK, case_id FK)  [Many-to-Many]
  │     └─→ cases (case_id PK)
  │
  └─→ episodes (episode_id PK, child_id FK)
        ├─→ placements (placement_id PK, episode_id FK)
        └─→ notes (note_id PK, episode_id FK)

allegations (allegation_id PK, case_id FK)
```

**Key Design Decisions**:

1. **Separate Episodes Table**:
   - Children can have multiple care episodes (reentry)
   - Allows tracking historical vs. current episodes
   - Alternative: Denormalized single table (rejected due to redundancy)

2. **Case-Child Many-to-Many**:
   - Cases can involve multiple children (siblings)
   - Children can be involved in multiple investigations
   - Junction table enables flexible querying

3. **Placements as Child of Episodes**:
   - Placement sequence matters (temporal ordering)
   - Facilitates stability calculations
   - Alternative: Separate placement history table (more complex)

**Trade-offs**:
- More complex queries (requires joins)
- Slightly slower for simple reads
- **Verdict**: Data integrity worth the complexity

---

### Views & Materialized Views

**Decision**: Create analytical views for common queries

**Implemented Views**:

1. **`child_episode`**: Combines child demographics with episode data
```sql
   -- Denormalized for analysis
   SELECT c.*, e.*, county, episode_length_days
   FROM children c
   JOIN episodes e ON c.child_id = e.child_id
```

2. **`analysis_master`**: Comprehensive analytical dataset
```sql
   -- Includes aggregated features
   SELECT ce.*, ep.total_placements, ch.total_cases
   FROM child_episode ce
   LEFT JOIN episode_placements ep
   LEFT JOIN child_case_history ch
```

3. **`metrics_summary`**: Pre-aggregated KPIs
```sql
   -- County-level metrics
   SELECT county, 
          AVG(long_stay_3yr) AS longstay_rate,
          COUNT(*) AS episodes
   GROUP BY county
```

**Rationale**:
- ✅ Simplify notebook queries (reduce boilerplate)
- ✅ Ensure consistent metric calculations
- ✅ Performance optimization (for frequently-accessed data)
- ✅ Abstraction layer (isolate schema changes from analysis code)

**Materialized vs. Standard Views**:
- **Standard Views**: Most cases (data refreshes frequently)
- **Materialized**: Reserved for complex aggregations (future enhancement)

---

## ETL Pipeline Design

### Architecture: Python-Based Custom Pipeline

**Decision**: Build custom ETL using Python rather than commercial tools

**Rationale**:
- ✅ **Flexibility**: Full control over transformations
- ✅ **Cost**: No licensing fees (vs. Talend, Informatica)
- ✅ **Integration**: Seamless with analysis environment
- ✅ **Transparency**: Open-source, auditable
- ✅ **Learning**: Educational value for capstone project

**ETL Stages**:

1. **Extract**:
```python
   # Load CSV files
   children_df = pd.read_csv('data/raw/children.csv')
```

2. **Transform**:
```python
   # Data type conversions
   children_df['dob'] = pd.to_datetime(children_df['dob'])
   
   # Validation
   assert children_df['child_id'].is_unique
   
   # Derived features
   df['age_at_entry'] = calculate_age(df['dob'], df['entry_date'])
```

3. **Load**:
```python
   # Bulk insert to PostgreSQL
   children_df.to_sql('children', engine, if_exists='replace')
```

**Error Handling**:
```python
try:
    validate_data(df)
    load_to_db(df)
except ValidationError as e:
    log_error(e)
    raise
```

**Alternatives Considered**:
- ❌ **Apache Airflow**: Overkill for batch-once ETL
- ❌ **dbt**: Great for transforms, but requires separate extract/load
- ❌ **Manual SQL**: Less reproducible, harder to test

---

## Analytical Framework

### Notebook Organization

**Decision**: Separate notebooks for distinct analytical phases

**Structure**:
```
src/analysis/
├── eda_child_episodes.ipynb      # Exploratory analysis
├── multilevel_longstay.ipynb     # Statistical modeling
├── survival_analysis.ipynb       # Time-to-event analysis
└── causal_policy_sim.ipynb       # Policy simulations

src/nlp/
└── topics_keywords_demo.ipynb    # Text analytics
```

**Rationale**:
- ✅ **Modularity**: Each notebook has single responsibility
- ✅ **Reproducibility**: Clear execution order
- ✅ **Collaboration**: Easier to review specific analyses
- ✅ **Debugging**: Isolate errors to specific stages

**Alternative**: Single monolithic notebook (rejected—too unwieldy)

---

### Statistical Modeling Approach

**Decision**: Use mixed-effects models for primary analysis

**Rationale**:
- ✅ **Hierarchical Data**: Children nested in counties
- ✅ **Generalizability**: Separate fixed and random effects
- ✅ **Efficiency**: Account for within-county correlation
- ✅ **Interpretability**: Quantify county-level variation (ICC)

**Implementation**:
```python
import statsmodels.api as sm
from statsmodels.formula.api import mixedlm

# Fit mixed model
model = mixedlm(
    formula="long_stay ~ age + race + placements",
    data=df,
    groups=df["county"]
)
results = model.fit()
```

**Alternatives Considered**:
- ❌ **Standard Logistic Regression**: Ignores clustering
- ❌ **Fixed Effects Models**: Less efficient, poor generalization
- ❌ **Random Forests**: Less interpretable for policy

---

### NLP Methodology

**Decision**: Use LDA (Latent Dirichlet Allocation) for topic modeling

**Rationale**:
- ✅ **Unsupervised**: No labeled training data needed
- ✅ **Interpretability**: Produces human-readable topics
- ✅ **Established**: Well-validated in text mining literature
- ✅ **Probabilistic**: Provides uncertainty estimates

**Implementation**:
```python
from gensim.models import LdaMulticore

# Train LDA model
lda = LdaMulticore(
    corpus=corpus,
    num_topics=5,
    id2word=dictionary,
    passes=20,
    workers=4
)
```

**Alternatives Considered**:
- ❌ **BERT/Transformers**: Overkill for topic modeling, less interpretable
- ❌ **LSA (Latent Semantic Analysis)**: Less probabilistic framework
- ❌ **NMF (Non-negative Matrix Factorization)**: Good but less standard in social science

---

## Code Organization

### Project Structure

**Decision**: Separate code by functional area with clear hierarchy

**Structure**:
```
child-welfare-capstone/
├── data/                 # Data files (gitignored)
├── sql/                  # Schema definitions
├── src/
│   ├── etl/             # ETL scripts
│   ├── analysis/        # Analytical notebooks
│   ├── nlp/             # NLP components
│   └── viz/             # Visualization configs
├── tests/               # Unit and integration tests
└── docs/                # Documentation
```

**Rationale**:
- ✅ **Clarity**: Easy to locate code by purpose
- ✅ **Scalability**: New components fit logically
- ✅ **Collaboration**: Multiple developers can work independently
- ✅ **Testing**: Clear separation of test code

**Key Principles**:
1. **Separation of Concerns**: ETL ≠ Analysis ≠ Visualization
2. **DRY (Don't Repeat Yourself)**: Shared utilities in modules
3. **Version Control**: All code in Git, data in `.gitignore`

---

### Configuration Management

**Decision**: Use Python modules for configuration (not YAML/JSON)

**Rationale**:
- ✅ **Type Safety**: Python type hints catch errors
- ✅ **Dynamic**: Can compute derived values
- ✅ **IDE Support**: Autocomplete and linting
- ✅ **Simplicity**: No need for parsing libraries

**Example** (`src/etl/config.py`):
```python
from dataclasses import dataclass

@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "chapinhall_capstone"
    user: str = "postgres"
    password: str = "mypassword123"
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
```

**Alternative**: YAML config files (rejected—less type-safe)

---

## Testing Strategy

### Testing Philosophy

**Decision**: Pragmatic testing focused on data quality

**Test Types**:

1. **Data Quality Tests** (Priority: HIGH)
```python
   def test_no_negative_ages():
       assert (df['age_at_entry'] >= 0).all()
   
   def test_referential_integrity():
       assert df['county'].isin(VALID_COUNTIES).all()
```

2. **Statistical Tests** (Priority: MEDIUM)
```python
   def test_model_convergence():
       assert results.converged == True
   
   def test_reasonable_coefficients():
       assert -5 < results.params['age'] < 5
```

3. **Unit Tests** (Priority: LOW)
```python
   def test_calculate_age():
       assert calculate_age('2020-01-01', '2023-01-01') == 3
```

**Rationale**:
- Data quality issues have highest impact
- Statistical tests catch modeling errors
- Unit tests for reusable functions only (not exploratory code)

**Test Framework**: `pytest`

**Coverage Goal**: 60% (pragmatic for research code)

---

## Future Enhancements

### Short-Term (3-6 months)

1. **Power BI Dashboard**
   - Complete interactive dashboard
   - Real-time county comparisons
   - Drill-down capabilities

2. **Automated Reporting**
   - Scheduled monthly reports
   - Email delivery to stakeholders
   - Parameterized templates

3. **Model Monitoring**
   - Track model performance over time
   - Alert on drift detection
   - Retraining pipelines

### Medium-Term (6-12 months)

1. **Real Data Integration**
   - Adapt pipeline for actual AFCARS data
   - Privacy-preserving transformations
   - Compliance checks (HIPAA, FERPA)

2. **Advanced NLP**
   - Transformer models (BERT)
   - Entity recognition (names, locations)
   - Sentiment analysis at scale

3. **Geospatial Analysis**
   - PostGIS integration
   - County-level mapping
   - Resource proximity analysis

### Long-Term (12+ months)

1. **Machine Learning Pipeline**
   - MLflow for experiment tracking
   - Automated hyperparameter tuning
   - Model versioning

2. **Causal Inference**
   - Propensity score matching
   - Difference-in-differences
   - Synthetic control methods

3. **Web Application**
   - Flask/Django backend
   - React frontend
   - REST API for predictions

---

## Lessons Learned

### What Worked Well

1. **Early Schema Design**
2. **Modular Notebooks**
3. **Version Control**
4. **Documentation-First**

### What Could Be Improved

1. **Test Coverage**: Should have written tests earlier
2. **Data Validation**: Needed more upfront validation rules
3. **Error Handling**: Could be more robust in ETL
4. **Performance**: Some queries could be optimized

### Key Takeaways

- **Design for Change**: Requirements evolved; flexibility mattered
- **Iterate Quickly**: Better to have working code than perfect code
- **Document Decisions**: This document would have helped earlier!
- **Stakeholder Input**: Should have involved domain experts sooner

---

## References

1. Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit*. Wiley.
2. Kleppmann, M. (2017). *Designin Data-Intensive Applications*. O'Reilly.
3. Wickham, H. (2014). Tidy data. *Journal of Statistical Software*, 59(10), 1-23.
4. Hunt, A., & Thomas, D. (1999). *The Pragmatic Programmer*. Addison-Wesley.

---

**Last Updated**: November 10, 2024
