# Entity Relationship Diagram (ERD)
## Child Welfare Database Schema

---

## Overview

This document describes the relational database schema for the child welfare capstone project. The database is designed to support longitudinal analysis of child welfare cases, episodes, placements, and outcomes.

**Database**: PostgreSQL 16  
**Total Tables**: 7 core tables + 6 analysis views  
**Normalization**: 3NF (Third Normal Form)

---

## Core Tables

### 1. **children**
Primary entity representing individual children in the system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `child_id` | INTEGER | PRIMARY KEY | Unique child identifier |
| `date_of_birth` | DATE | NOT NULL | Child's birth date |
| `sex` | VARCHAR(10) | NOT NULL | Sex (Male/Female/Other) |
| `race` | VARCHAR(50) | NOT NULL | Race/ethnicity |
| `removed_reason` | VARCHAR(100) | | Primary removal reason |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**: 
- PRIMARY KEY on `child_id`
- INDEX on `race` for equity analysis
- INDEX on `date_of_birth` for age calculations

---

### 2. **cases**
Investigation or referral cases that may lead to removal.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `case_id` | INTEGER | PRIMARY KEY | Unique case identifier |
| `report_date` | DATE | NOT NULL | Date case reported |
| `allegation_type` | VARCHAR(100) | | Type of maltreatment |
| `disposition` | VARCHAR(50) | | Case finding (indicated/unfounded) |
| `county` | VARCHAR(50) | NOT NULL | Investigating county |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `case_id`
- INDEX on `county` for geographic analysis
- INDEX on `disposition` for filtering

---

### 3. **case_child**
Junction table linking children to cases (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `case_child_id` | INTEGER | PRIMARY KEY | Unique link identifier |
| `case_id` | INTEGER | FOREIGN KEY | Reference to cases table |
| `child_id` | INTEGER | FOREIGN KEY | Reference to children table |

**Indexes**:
- PRIMARY KEY on `case_child_id`
- UNIQUE constraint on (`case_id`, `child_id`)
- INDEX on `case_id`
- INDEX on `child_id`

**Foreign Keys**:
```sql
FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
FOREIGN KEY (child_id) REFERENCES children(child_id) ON DELETE CASCADE
```

---

### 4. **episodes**
Out-of-home care episodes (foster care placements).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `episode_id` | INTEGER | PRIMARY KEY | Unique episode identifier |
| `child_id` | INTEGER | FOREIGN KEY | Reference to children table |
| `entry_date` | DATE | NOT NULL | Date entered care |
| `exit_date` | DATE | | Date exited care (NULL if active) |
| `exit_reason` | VARCHAR(100) | | Reason for exit (reunification, adoption, etc.) |
| `initial_county` | VARCHAR(50) | NOT NULL | County managing case |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `episode_id`
- INDEX on `child_id`
- INDEX on `entry_date`, `exit_date` for temporal queries
- INDEX on `initial_county`

**Constraints**:
```sql
CHECK (exit_date IS NULL OR exit_date >= entry_date)
```

---

### 5. **placements**
Individual placements during an episode (can have multiple per episode).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `placement_id` | INTEGER | PRIMARY KEY | Unique placement identifier |
| `episode_id` | INTEGER | FOREIGN KEY | Reference to episodes table |
| `placement_start` | DATE | NOT NULL | Placement start date |
| `placement_end` | DATE | | Placement end date (NULL if current) |
| `placement_type` | VARCHAR(50) | NOT NULL | Type (foster, kinship, group home) |
| `provider_id` | INTEGER | | Provider/agency identifier |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `placement_id`
- INDEX on `episode_id`
- INDEX on `placement_type`
- INDEX on `provider_id`

**Constraints**:
```sql
CHECK (placement_end IS NULL OR placement_end >= placement_start)
```

---

### 6. **allegations**
Specific maltreatment allegations within cases.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `allegation_id` | INTEGER | PRIMARY KEY | Unique allegation identifier |
| `case_id` | INTEGER | FOREIGN KEY | Reference to cases table |
| `allegation_type` | VARCHAR(100) | NOT NULL | Type of maltreatment |
| `perpetrator_relationship` | VARCHAR(50) | | Relationship to child |
| `disposition` | VARCHAR(50) | | Finding (indicated/unfounded) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `allegation_id`
- INDEX on `case_id`
- INDEX on `allegation_type`

---

### 7. **notes**
Case documentation and narrative notes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `note_id` | INTEGER | PRIMARY KEY | Unique note identifier |
| `child_id` | INTEGER | FOREIGN KEY | Reference to children table |
| `note_date` | DATE | NOT NULL | Date note written |
| `note_type` | VARCHAR(50) | | Type (case note, court report, etc.) |
| `note_text` | TEXT | NOT NULL | Full text content |
| `author` | VARCHAR(100) | | Caseworker/author name |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `note_id`
- INDEX on `child_id`
- INDEX on `note_date`
- Full-text search index on `note_text` (PostgreSQL GIN)

---

## Analysis Views

### 1. **child_episode**
Combines child demographics with episode information.
```sql
CREATE VIEW child_episode AS
SELECT 
    c.child_id,
    c.date_of_birth,
    c.sex,
    c.race,
    c.removed_reason,
    e.episode_id,
    e.entry_date,
    e.exit_date,
    e.exit_reason,
    e.initial_county,
    EXTRACT(YEAR FROM AGE(e.entry_date, c.date_of_birth)) AS age_at_entry,
    CASE 
        WHEN e.exit_date IS NULL THEN CURRENT_DATE - e.entry_date
        ELSE e.exit_date - e.entry_date 
    END AS episode_length_days,
    CASE WHEN e.exit_date IS NULL THEN TRUE ELSE FALSE END AS is_active,
    CASE 
        WHEN (COALESCE(e.exit_date, CURRENT_DATE) - e.entry_date) >= 1095 
        THEN TRUE ELSE FALSE 
    END AS long_stay_3yr
FROM children c
JOIN episodes e ON c.child_id = e.child_id;
```

---

### 2. **episode_placements**
Aggregates placement information per episode.
```sql
CREATE VIEW episode_placements AS
SELECT 
    episode_id,
    COUNT(*) AS total_placements,
    MIN(placement_start) AS first_placement_date,
    MAX(COALESCE(placement_end, CURRENT_DATE)) AS last_placement_date,
    CASE 
        WHEN COUNT(*) = 1 THEN 'Stable'
        WHEN COUNT(*) <= 3 THEN 'Moderate'
        ELSE 'High Instability'
    END AS stability_category,
    MODE() WITHIN GROUP (ORDER BY placement_type) AS most_common_type
FROM placements
GROUP BY episode_id;
```

---

### 3. **analysis_master**
Comprehensive view combining all relevant data for modeling.
```sql
CREATE VIEW analysis_master AS
SELECT 
    ce.*,
    ep.total_placements,
    ep.stability_category,
    ep.most_common_type AS primary_placement_type,
    ch.total_cases,
    ch.has_indicated_finding
FROM child_episode ce
LEFT JOIN episode_placements ep ON ce.episode_id = ep.episode_id
LEFT JOIN child_case_history ch ON ce.child_id = ch.child_id;
```

---

### 4. **child_case_history**
Aggregates case history per child.
```sql
CREATE VIEW child_case_history AS
SELECT 
    c.child_id,
    COUNT(DISTINCT cs.case_id) AS total_cases,
    MAX(CASE WHEN cs.disposition = 'Indicated' THEN 1 ELSE 0 END) AS has_indicated_finding,
    STRING_AGG(DISTINCT cs.allegation_type, ', ') AS allegation_types
FROM children c
LEFT JOIN case_child cc ON c.child_id = cc.child_id
LEFT JOIN cases cs ON cc.case_id = cs.case_id
GROUP BY c.child_id;
```

---

### 5. **metrics_summary**
Key performance indicators for reporting.
```sql
CREATE VIEW metrics_summary AS
SELECT 
    COUNT(DISTINCT child_id) AS total_children,
    COUNT(DISTINCT episode_id) AS total_episodes,
    AVG(episode_length_days) AS avg_episode_length,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY episode_length_days) AS median_episode_length,
    SUM(CASE WHEN long_stay_3yr THEN 1 ELSE 0 END) AS longstay_count,
    AVG(CASE WHEN long_stay_3yr THEN 1.0 ELSE 0.0 END) * 100 AS longstay_rate_pct,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_episodes
FROM child_episode;
```

---

### 6. **disparities_race_county**
Equity analysis by race and county.
```sql
CREATE VIEW disparities_race_county AS
SELECT 
    race,
    initial_county,
    COUNT(*) AS n_episodes,
    AVG(episode_length_days) AS avg_length,
    AVG(CASE WHEN long_stay_3yr THEN 1.0 ELSE 0.0 END) * 100 AS longstay_rate_pct
FROM child_episode
GROUP BY race, initial_county
ORDER BY race, initial_county;
```

---

## Relationships Diagram
```
┌─────────────┐
│  children   │
│─────────────│
│ child_id PK │◄─────────┐
│ dob         │          │
│ sex         │          │
│ race        │          │
└─────────────┘          │
       ▲                 │
       │ 1:N             │
       │                 │
┌──────┴──────┐          │
│  episodes   │          │
│─────────────│          │
│ episode_id  │          │
│ child_id FK │          │
│ entry_date  │          │
│ exit_date   │          │
└─────────────┘          │
       ▲                 │
       │ 1:N             │
       │                 │
┌──────┴──────┐          │
│ placements  │          │
│─────────────│          │
│ placement_id│          │
│ episode_id  │          │
│ start_date  │          │
└─────────────┘          │
                         │
┌─────────────┐          │
│    notes    │          │
│─────────────│          │
│ note_id     │          │
│ child_id FK │──────────┘
│ note_text   │
└─────────────┘

┌─────────────┐
│    cases    │
│─────────────│
│ case_id PK  │◄─────┐
│ report_date │      │
│ county      │      │
└─────────────┘      │
       ▲             │
       │             │
       │             │
┌──────┴──────┐      │
│ case_child  │      │
│─────────────│      │
│ case_id FK  │      │
│ child_id FK │──────┘
└─────────────┘
       │
       ▼
┌─────────────┐
│ allegations │
│─────────────│
│ allegation  │
│ case_id FK  │
│ type        │
└─────────────┘
```

---

## Data Flow
```
┌──────────────┐
│  Raw CSV     │
│  Files       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Python ETL   │
│ (load_raw.py)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
│ Core Tables  │
└──────┬───────┘
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ Analysis     │   │ Power BI     │
│ Views        │   │ Dashboards   │
└──────┬───────┘   └──────────────┘
       │
       ▼
┌──────────────┐
│ Python       │
│ Notebooks    │
└──────────────┘
```

---

## Key Design Decisions

1. **Separate Episodes from Placements**: Allows tracking multiple placements within a single episode
2. **Many-to-Many for Cases**: One case can involve multiple children, one child can have multiple cases
3. **Temporal Flexibility**: NULL exit dates allow active/ongoing records
4. **County Tracking**: Enables geographic analysis and jurisdictional patterns
5. **View-Based Analytics**: Pre-computed metrics for performance
6. **Full-Text Search**: GIN index on notes for NLP analysis

---

## Sample Queries

### Get all children with long-stay episodes:
```sql
SELECT child_id, race, age_at_entry, episode_length_days
FROM child_episode
WHERE long_stay_3yr = TRUE;
```

### Calculate county-level metrics:
```sql
SELECT 
    initial_county,
    COUNT(*) AS total_episodes,
    AVG(episode_length_days) AS avg_length,
    SUM(CASE WHEN long_stay_3yr THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 AS longstay_pct
FROM child_episode
GROUP BY initial_county
ORDER BY longstay_pct DESC;
```

### Find placement instability:
```sql
SELECT child_id, COUNT(*) AS placement_moves
FROM placements p
JOIN episodes e ON p.episode_id = e.episode_id
GROUP BY child_id
HAVING COUNT(*) >= 5
ORDER BY placement_moves DESC;
```

---

**Last Updated**: November 2024  
**Version**: 1.0
