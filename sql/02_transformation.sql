-- ============================================
-- Chapin Hall Capstone - Analysis Transformations
-- ============================================
-- This creates analysis-ready views and materialized views

-- ============================================
-- 1. Child Episode View
-- Combines child demographics with episode info
-- ============================================

DROP VIEW IF EXISTS child_episode CASCADE;
DROP MATERIALIZED VIEW IF EXISTS child_episode_mv CASCADE;

CREATE VIEW child_episode AS
SELECT 
    e.episode_id,
    e.child_id,
    c.date_of_birth,
    c.gender,
    c.race,
    c.ethnicity,
    c.initial_county,
    
    -- Episode details
    e.entry_date,
    e.exit_date,
    e.removal_reason,
    e.episode_status,
    e.goal,
    
    -- Calculated fields
    EXTRACT(YEAR FROM AGE(e.entry_date, c.date_of_birth)) AS age_at_entry_years,
    e.entry_date - c.date_of_birth AS age_at_entry_days,
    
    -- Episode length calculations
    CASE 
        WHEN e.exit_date IS NOT NULL 
        THEN e.exit_date - e.entry_date 
        ELSE CURRENT_DATE - e.entry_date 
    END AS episode_length_days,
    
    CASE 
        WHEN e.exit_date IS NOT NULL 
        THEN ROUND((e.exit_date - e.entry_date) / 365.25, 2)
        ELSE ROUND((CURRENT_DATE - e.entry_date) / 365.25, 2)
    END AS episode_length_years,
    
    -- Long stay flags (critical metric)
    CASE 
        WHEN e.exit_date IS NOT NULL THEN
            CASE WHEN (e.exit_date - e.entry_date) >= 1095 THEN TRUE ELSE FALSE END
        ELSE
            CASE WHEN (CURRENT_DATE - e.entry_date) >= 1095 THEN TRUE ELSE FALSE END
    END AS long_stay_3yr,
    
    CASE 
        WHEN e.exit_date IS NOT NULL THEN
            CASE WHEN (e.exit_date - e.entry_date) >= 730 THEN TRUE ELSE FALSE END
        ELSE
            CASE WHEN (CURRENT_DATE - e.entry_date) >= 730 THEN TRUE ELSE FALSE END
    END AS long_stay_2yr,
    
    -- Is episode currently active?
    CASE WHEN e.exit_date IS NULL THEN TRUE ELSE FALSE END AS is_active,
    
    -- Entry year for trend analysis
    EXTRACT(YEAR FROM e.entry_date) AS entry_year,
    EXTRACT(MONTH FROM e.entry_date) AS entry_month,
    EXTRACT(QUARTER FROM e.entry_date) AS entry_quarter

FROM episodes e
INNER JOIN children c ON e.child_id = c.child_id;

-- ============================================
-- 2. Placement Summary View
-- Aggregates placement info per episode
-- ============================================

DROP VIEW IF EXISTS episode_placements CASCADE;

CREATE VIEW episode_placements AS
SELECT 
    p.episode_id,
    COUNT(*) AS total_placements,
    COUNT(DISTINCT placement_type) AS unique_placement_types,
    COUNT(DISTINCT placement_county) AS counties_lived_in,
    MIN(p.placement_start) AS first_placement_date,
    MAX(COALESCE(p.placement_end, CURRENT_DATE)) AS last_placement_date,
    
    -- Most common placement type
    MODE() WITHIN GROUP (ORDER BY p.placement_type) AS most_common_placement_type,
    
    -- Current placement (if active)
    MAX(CASE WHEN p.placement_end IS NULL THEN p.placement_type END) AS current_placement_type,
    MAX(CASE WHEN p.placement_end IS NULL THEN p.placement_county END) AS current_placement_county,
    
    -- Placement stability metric (fewer moves = more stable)
    CASE 
        WHEN COUNT(*) = 1 THEN 'Stable'
        WHEN COUNT(*) BETWEEN 2 AND 3 THEN 'Moderate'
        ELSE 'High Disruption'
    END AS stability_category

FROM placements p
GROUP BY p.episode_id;

-- ============================================
-- 3. Child Case History
-- Links children to their investigation history
-- ============================================

DROP VIEW IF EXISTS child_case_history CASCADE;

CREATE VIEW child_case_history AS
SELECT 
    ch.child_id,
    COUNT(DISTINCT cc.case_id) AS total_cases,
    MIN(ca.referral_date) AS first_referral_date,
    MAX(ca.referral_date) AS most_recent_referral_date,
    
    -- Count by case type
    COUNT(DISTINCT CASE WHEN ca.case_type = 'investigation' THEN ca.case_id END) AS investigation_cases,
    COUNT(DISTINCT CASE WHEN ca.case_type = 'assessment' THEN ca.case_id END) AS assessment_cases,
    
    -- Has indicated findings?
    MAX(CASE WHEN a.finding = 'indicated' THEN 1 ELSE 0 END) = 1 AS has_indicated_finding

FROM children ch
LEFT JOIN case_child cc ON ch.child_id = cc.child_id
LEFT JOIN cases ca ON cc.case_id = ca.case_id
LEFT JOIN allegations a ON cc.case_id = a.case_id AND cc.child_id = a.child_id
GROUP BY ch.child_id;

-- ============================================
-- 4. Master Analysis View
-- Combines everything for easy analysis
-- ============================================

DROP VIEW IF EXISTS analysis_master CASCADE;

CREATE VIEW analysis_master AS
SELECT 
    ce.*,
    ep.total_placements,
    ep.unique_placement_types,
    ep.counties_lived_in,
    ep.stability_category,
    ep.current_placement_type,
    ep.current_placement_county,
    
    ch.total_cases,
    ch.first_referral_date,
    ch.most_recent_referral_date,
    ch.has_indicated_finding

FROM child_episode ce
LEFT JOIN episode_placements ep ON ce.episode_id = ep.episode_id
LEFT JOIN child_case_history ch ON ce.child_id = ch.child_id;

-- ============================================
-- 5. Key Metrics Summary
-- Aggregated stats for dashboard
-- ============================================

DROP VIEW IF EXISTS metrics_summary CASCADE;

CREATE VIEW metrics_summary AS
SELECT 
    -- Overall counts
    COUNT(DISTINCT child_id) AS total_children,
    COUNT(DISTINCT episode_id) AS total_episodes,
    COUNT(DISTINCT CASE WHEN is_active THEN episode_id END) AS active_episodes,
    
    -- Length of stay metrics
    AVG(episode_length_days) AS avg_episode_length_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY episode_length_days) AS median_episode_length_days,
    
    -- Long stay rates
    ROUND(100.0 * COUNT(CASE WHEN long_stay_3yr THEN 1 END) / COUNT(*), 2) AS pct_long_stay_3yr,
    ROUND(100.0 * COUNT(CASE WHEN long_stay_2yr THEN 1 END) / COUNT(*), 2) AS pct_long_stay_2yr,
    
    -- Demographics
    COUNT(CASE WHEN race = 'Black' THEN 1 END) AS black_children,
    COUNT(CASE WHEN race = 'White' THEN 1 END) AS white_children,
    COUNT(CASE WHEN race = 'Hispanic' THEN 1 END) AS hispanic_children,
    
    -- Age distribution
    AVG(age_at_entry_years) AS avg_age_at_entry,
    COUNT(CASE WHEN age_at_entry_years < 1 THEN 1 END) AS infants,
    COUNT(CASE WHEN age_at_entry_years BETWEEN 1 AND 5 THEN 1 END) AS young_children,
    COUNT(CASE WHEN age_at_entry_years BETWEEN 6 AND 12 THEN 1 END) AS school_age,
    COUNT(CASE WHEN age_at_entry_years >= 13 THEN 1 END) AS teens

FROM child_episode;

-- ============================================
-- 6. Disparities by Race and County
-- Critical for equity analysis
-- ============================================

DROP VIEW IF EXISTS disparities_race_county CASCADE;

CREATE VIEW disparities_race_county AS
SELECT 
    initial_county,
    race,
    COUNT(DISTINCT child_id) AS children_count,
    COUNT(DISTINCT episode_id) AS episodes_count,
    AVG(episode_length_days) AS avg_length_days,
    ROUND(100.0 * COUNT(CASE WHEN long_stay_3yr THEN 1 END) / COUNT(*), 2) AS pct_long_stay_3yr,
    COUNT(CASE WHEN is_active THEN 1 END) AS active_episodes,
    AVG(total_placements) AS avg_placements_per_episode

FROM analysis_master
GROUP BY initial_county, race
ORDER BY initial_county, race;

-- ============================================
-- 7. Monthly Trends
-- For time series analysis
-- ============================================

DROP VIEW IF EXISTS monthly_trends CASCADE;

CREATE VIEW monthly_trends AS
SELECT 
    DATE_TRUNC('month', entry_date) AS month,
    COUNT(DISTINCT child_id) AS new_entries,
    COUNT(DISTINCT episode_id) AS new_episodes,
    AVG(age_at_entry_years) AS avg_entry_age,
    COUNT(CASE WHEN race = 'Black' THEN 1 END) AS black_entries,
    COUNT(CASE WHEN race = 'White' THEN 1 END) AS white_entries,
    COUNT(CASE WHEN race = 'Hispanic' THEN 1 END) AS hispanic_entries

FROM child_episode
GROUP BY DATE_TRUNC('month', entry_date)
ORDER BY month;

-- ============================================
-- Create indexes on views for performance
-- ============================================

-- For faster queries on child_episode
CREATE INDEX IF NOT EXISTS idx_ce_child_id ON episodes(child_id);
CREATE INDEX IF NOT EXISTS idx_ce_entry_date ON episodes(entry_date);
CREATE INDEX IF NOT EXISTS idx_ce_status ON episodes(episode_status);

-- ============================================
-- Grant permissions (if needed)
-- ============================================

-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO your_user;

-- ============================================
-- Done!
-- ============================================
SELECT 'Transformation views created successfully!' AS status;
