# Chapin Hall-Style Child Welfare Analytics Capstone

End-to-end synthetic project designed to mirror the Researcher (Data Analytics & Visualization) role:

- Large-scale administrative child welfare data (synthetic).
- Reproducible ETL and analytic data model.
- Transparent, documented code with version control.
- Policy-relevant statistical modeling and visualization.
- Intro integration of qualitative/NLP signals.

This repo simulates the workflow you would lead in collaboration with state partners and internal teams.

---

## 1. Objectives

1. **Data Engineering**
   - Ingest, clean, and integrate core child welfare tables (child, case, episode, placement, allegations, notes).
   - Implement an analysis-ready episode-level model with consistent rules for censoring, long stays, and re-entry.

2. **Analytics & Methods**
   - Estimate and interpret long-stay and re-entry metrics.
   - Fit interpretable models (e.g., logistic or multilevel) to explore factors associated with long stays.
   - Frame results in a cautious, policy-relevant way (associations, not blame).

3. **Visualization**
   - Build a Power BI report suited for leadership and program managers.
   - Emphasize clarity, drill-downs, and equity-disaggregated views.

4. **Collaboration**
   - Demonstrate Git-based workflows, code review practices, and clear documentation.

5. **Qualitative / NLP**
   - Use narrative notes as an additional signal; show how to integrate basic NLP responsibly.

---

## 2. Data Model

All data are synthetic and structurally modeled on common child welfare administrative systems.

### Core Entities

- **`cw.child`**  
  One row per child; demographics and home county.

- **`cw.case`**  
  One row per case; case type, primary reason, court, county.

- **`cw.case_child`**  
  Links children to cases; supports family-level cases and siblings.

- **`cw.episode`**  
  Care episodes (removal→exit) at the child level.

- **`cw.placement`**  
  Placement spells within episodes; used to derive placement stability.

- **`cw.allegation`**  
  Alleged maltreatment types, perpetrators, dispositions.

- **`cw.note`**  
  Narrative notes (synthetic); used for NLP-style theme extraction.

### Analytic Layer

- **`cw_ana.child_episode` (VIEW)**  
  Central fact view that standardizes:
  - Age at removal  
  - Episode length and censoring (configurable censor date)  
  - Long-stay flags (12 / 18 / 36 months)  
  - Placement instability (3+ placements)  
  - Re-entry within 12 months (next episode)  
  - County attribution

- **`cw_ana.child_episode_by_county` (VIEW)**  
  County-level rollup:
  - Episodes, children
  - Long-stay rates
  - Instability rate
  - Re-entry rate among non-censored exits

This separation mirrors a real-world pattern: raw → normalized → governed analytic views feeding BI and modeling.

---

## 3. Tech Stack

- **Database:** PostgreSQL
- **Languages:** Python (ETL, analysis), SQL
- **Visualization:** Power BI (or equivalent)
- **Packages (core):**
  - `pandas`, `sqlalchemy`, `psycopg2-binary`
  - `statsmodels`, `scikit-learn` (optional)
  - `pytest` for basic data quality tests
- **Workflow:** Git/GitHub or GitLab (branches, MRs, code review)

---

## 4. Repository Structure

```text
chapinhall-capstone/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ Makefile
├─ data/
│  ├─ raw/                # synthetic CSVs
│  ├─ interim/            # optional staging / QA extracts
│  └─ processed/          # exports for modeling / BI
├─ sql/
│  ├─ 00_core_schema.sql
│  ├─ 01_load_raw_to_staging.sql      (optional)
│  ├─ 02_child_episode_view.sql
│  └─ 03_child_episode_by_county.sql
├─ src/
│  ├─ etl/
│  │  ├─ __init__.py
│  │  ├─ load_raw.py                  # CSV → Postgres loader
│  │  └─ build_analysis_views.md      # notes on running SQL
│  ├─ analysis/
│  │  ├─ longstay_multilevel.ipynb    # long-stay modeling demo
│  │  └─ reentry_analysis.ipynb       # (optional)
│  ├─ viz/
│  │  └─ powerbi_dataset_notes.md     # how PBIX connects to DB/views
│  └─ nlp/
│     ├─ notes_preprocess.py
│     └─ notes_topics_demo.ipynb
├─ tests/
│  ├─ test_data_quality.py
│  └─ test_metrics_consistency.py
└─ CONTRIBUTING.md                    # Git flow & code review guidelines
