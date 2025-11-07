-- ============================================
-- Chapin Hall Capstone - Core Schema
-- ============================================
-- Drop tables if they exist (for clean restart)
DROP TABLE IF EXISTS allegations CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS placements CASCADE;
DROP TABLE IF EXISTS episodes CASCADE;
DROP TABLE IF EXISTS case_child CASCADE;
DROP TABLE IF EXISTS cases CASCADE;
DROP TABLE IF EXISTS children CASCADE;

-- ============================================
-- Core Tables
-- ============================================

-- Children table: demographic information
CREATE TABLE children (
    child_id SERIAL PRIMARY KEY,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    initial_county VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cases table: investigation/referral cases
CREATE TABLE cases (
    case_id SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    referral_date DATE NOT NULL,
    case_type VARCHAR(50),
    intake_county VARCHAR(100),
    case_status VARCHAR(20),
    closure_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Case-Child linking table (many-to-many)
CREATE TABLE case_child (
    case_child_id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(case_id),
    child_id INTEGER NOT NULL REFERENCES children(child_id),
    role_in_case VARCHAR(50), -- e.g., 'victim', 'sibling'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, child_id)
);

-- Episodes table: periods of out-of-home care
CREATE TABLE episodes (
    episode_id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL REFERENCES children(child_id),
    entry_date DATE NOT NULL,
    exit_date DATE,
    removal_reason VARCHAR(100),
    entry_age_days INTEGER,
    episode_status VARCHAR(20), -- 'active', 'closed'
    goal VARCHAR(50), -- 'reunification', 'adoption', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Placements table: specific living arrangements during episodes
CREATE TABLE placements (
    placement_id SERIAL PRIMARY KEY,
    episode_id INTEGER NOT NULL REFERENCES episodes(episode_id),
    placement_start DATE NOT NULL,
    placement_end DATE,
    placement_type VARCHAR(50), -- 'foster_home', 'kinship', 'group_home'
    placement_county VARCHAR(100),
    provider_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Allegations table: specific maltreatment allegations
CREATE TABLE allegations (
    allegation_id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(case_id),
    child_id INTEGER NOT NULL REFERENCES children(child_id),
    allegation_type VARCHAR(50), -- 'neglect', 'physical_abuse', etc.
    allegation_date DATE,
    finding VARCHAR(20), -- 'indicated', 'unfounded', 'pending'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table: case notes and documentation
CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(case_id),
    child_id INTEGER REFERENCES children(child_id),
    episode_id INTEGER REFERENCES episodes(episode_id),
    note_date DATE NOT NULL,
    note_type VARCHAR(50), -- 'assessment', 'visit', 'court', etc.
    note_text TEXT,
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes for performance
-- ============================================

CREATE INDEX idx_children_dob ON children(date_of_birth);
CREATE INDEX idx_children_race ON children(race);
CREATE INDEX idx_children_county ON children(initial_county);

CREATE INDEX idx_cases_referral_date ON cases(referral_date);
CREATE INDEX idx_cases_county ON cases(intake_county);
CREATE INDEX idx_cases_status ON cases(case_status);

CREATE INDEX idx_case_child_case ON case_child(case_id);
CREATE INDEX idx_case_child_child ON case_child(child_id);

CREATE INDEX idx_episodes_child ON episodes(child_id);
CREATE INDEX idx_episodes_entry_date ON episodes(entry_date);
CREATE INDEX idx_episodes_status ON episodes(episode_status);

CREATE INDEX idx_placements_episode ON placements(episode_id);
CREATE INDEX idx_placements_type ON placements(placement_type);
CREATE INDEX idx_placements_start ON placements(placement_start);

CREATE INDEX idx_allegations_case ON allegations(case_id);
CREATE INDEX idx_allegations_child ON allegations(child_id);
CREATE INDEX idx_allegations_type ON allegations(allegation_type);

CREATE INDEX idx_notes_case ON notes(case_id);
CREATE INDEX idx_notes_child ON notes(child_id);
CREATE INDEX idx_notes_episode ON notes(episode_id);
CREATE INDEX idx_notes_date ON notes(note_date);

-- ============================================
-- Done!
-- ============================================
COMMENT ON DATABASE chapinhall_capstone IS 'Chapin Hall child welfare capstone project database';
