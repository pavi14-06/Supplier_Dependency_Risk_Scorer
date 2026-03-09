-- ══════════════════════════════════════════════════════════════════════
-- SUPPLIER DEPENDENCY RISK SCORER — SQL QUERY LIBRARY
-- Author  : Pavithra V | Data Analyst
-- Domain  : Pharmaceutical Supply Chain Analytics
-- Engine  : SQLite (portable) | Compatible with PostgreSQL / MySQL
-- ══════════════════════════════════════════════════════════════════════


-- ─────────────────────────────────────────────
-- TABLE DEFINITIONS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS supplier_master (
    supplier_id   TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    country       TEXT NOT NULL,
    region        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS supply_chain_records (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id             TEXT REFERENCES supplier_master(supplier_id),
    material                TEXT NOT NULL,
    annual_spend_usd        REAL,
    lead_time_days          INTEGER,
    on_time_delivery_pct    REAL,
    quality_reject_pct      REAL,
    sole_source             INTEGER DEFAULT 0,   -- 1=Yes, 0=No
    geopolitical_risk_score INTEGER,              -- 1 (safe) to 10 (high risk)
    regulatory_compliance   TEXT,                 -- FDA, EMA, Both, None
    last_audit_days_ago     INTEGER,
    disruption_incidents    INTEGER DEFAULT 0,
    record_date             TEXT
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id     TEXT,
    supplier_name   TEXT,
    country         TEXT,
    region          TEXT,
    composite_score REAL,
    risk_tier       TEXT,
    scored_on       TEXT
);


-- ─────────────────────────────────────────────
-- QUERY 1: FULL SUPPLIER RISK DASHBOARD VIEW
-- Used in Power BI as primary data source
-- ─────────────────────────────────────────────
SELECT
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.region,
    COUNT(r.id)                         AS total_materials_supplied,
    SUM(r.annual_spend_usd)             AS total_annual_spend_usd,
    AVG(r.lead_time_days)               AS avg_lead_time_days,
    AVG(r.on_time_delivery_pct)         AS avg_on_time_delivery_pct,
    AVG(r.quality_reject_pct)           AS avg_quality_reject_pct,
    SUM(CASE WHEN r.sole_source = 1
             THEN 1 ELSE 0 END)         AS sole_source_count,
    AVG(r.geopolitical_risk_score)      AS avg_geo_risk_score,
    SUM(r.disruption_incidents)         AS total_disruptions,
    rs.composite_score,
    rs.risk_tier,
    rs.scored_on
FROM supplier_master s
JOIN supply_chain_records r ON s.supplier_id = r.supplier_id
JOIN risk_scores rs          ON s.supplier_id = rs.supplier_id
GROUP BY
    s.supplier_id, s.supplier_name, s.country,
    s.region, rs.composite_score, rs.risk_tier, rs.scored_on
ORDER BY rs.composite_score DESC;


-- ─────────────────────────────────────────────
-- QUERY 2: COUNTRY-LEVEL DEPENDENCY ANALYSIS
-- Identifies over-reliance on specific countries
-- ─────────────────────────────────────────────
SELECT
    s.country,
    s.region,
    COUNT(DISTINCT s.supplier_id)       AS supplier_count,
    COUNT(DISTINCT r.material)          AS unique_materials,
    SUM(r.annual_spend_usd)             AS total_spend_usd,
    ROUND(AVG(rs.composite_score), 2)   AS avg_risk_score,
    ROUND(
        SUM(r.annual_spend_usd) * 100.0 /
        (SELECT SUM(annual_spend_usd) FROM supply_chain_records), 2
    )                                   AS spend_concentration_pct,
    CASE
        WHEN AVG(rs.composite_score) >= 60 THEN 'CRITICAL DEPENDENCY'
        WHEN AVG(rs.composite_score) >= 40 THEN 'HIGH DEPENDENCY'
        WHEN AVG(rs.composite_score) >= 25 THEN 'MODERATE DEPENDENCY'
        ELSE                                    'LOW DEPENDENCY'
    END                                 AS dependency_alert
FROM supplier_master s
JOIN supply_chain_records r ON s.supplier_id = r.supplier_id
JOIN risk_scores rs          ON s.supplier_id = rs.supplier_id
GROUP BY s.country, s.region
ORDER BY avg_risk_score DESC;


-- ─────────────────────────────────────────────
-- QUERY 3: SOLE-SOURCE CRITICAL MATERIALS
-- Materials with NO backup supplier — highest risk
-- ─────────────────────────────────────────────
SELECT
    r.material,
    COUNT(DISTINCT r.supplier_id)       AS supplier_count,
    SUM(CASE WHEN r.sole_source = 1
             THEN 1 ELSE 0 END)         AS sole_source_suppliers,
    SUM(r.annual_spend_usd)             AS total_spend_usd,
    AVG(r.lead_time_days)               AS avg_lead_time,
    ROUND(AVG(rs.composite_score), 2)   AS avg_risk_score,
    CASE
        WHEN COUNT(DISTINCT r.supplier_id) = 1 THEN '🔴 SINGLE SOURCE — CRITICAL'
        WHEN SUM(CASE WHEN r.sole_source = 1 THEN 1 ELSE 0 END) > 0
                                         THEN '🟠 PARTIAL SOLE SOURCE'
        ELSE                                  '🟢 MULTI-SOURCED'
    END                                 AS sourcing_risk_flag
FROM supply_chain_records r
JOIN risk_scores rs ON r.supplier_id = rs.supplier_id
GROUP BY r.material
ORDER BY sole_source_suppliers DESC, avg_risk_score DESC;


-- ─────────────────────────────────────────────
-- QUERY 4: HIGH-RISK SUPPLIER WATCHLIST
-- Suppliers crossing the CRITICAL threshold (score >= 60)
-- ─────────────────────────────────────────────
SELECT
    rs.supplier_id,
    rs.supplier_name,
    rs.country,
    rs.composite_score,
    rs.risk_tier,
    SUM(r.annual_spend_usd)             AS total_annual_spend,
    SUM(r.disruption_incidents)         AS total_disruptions,
    AVG(r.on_time_delivery_pct)         AS avg_on_time,
    AVG(r.quality_reject_pct)           AS avg_reject_pct,
    r.regulatory_compliance
FROM risk_scores rs
JOIN supply_chain_records r ON rs.supplier_id = r.supplier_id
WHERE rs.composite_score >= 40
GROUP BY
    rs.supplier_id, rs.supplier_name, rs.country,
    rs.composite_score, rs.risk_tier, r.regulatory_compliance
ORDER BY rs.composite_score DESC;


-- ─────────────────────────────────────────────
-- QUERY 5: REGULATORY COMPLIANCE GAP REPORT
-- Suppliers with no FDA/EMA compliance — audit risk
-- ─────────────────────────────────────────────
SELECT
    s.supplier_name,
    s.country,
    r.regulatory_compliance,
    r.last_audit_days_ago,
    COUNT(r.id)                         AS materials_supplied,
    SUM(r.annual_spend_usd)             AS at_risk_spend_usd,
    rs.composite_score,
    rs.risk_tier,
    CASE
        WHEN r.regulatory_compliance = 'None'
             THEN '🔴 NON-COMPLIANT — IMMEDIATE REVIEW'
        WHEN r.last_audit_days_ago > 365
             THEN '🟠 AUDIT OVERDUE (>1 year)'
        WHEN r.last_audit_days_ago > 180
             THEN '🟡 AUDIT DUE SOON (>6 months)'
        ELSE      '🟢 COMPLIANT'
    END                                 AS compliance_flag
FROM supply_chain_records r
JOIN supplier_master s  ON r.supplier_id = s.supplier_id
JOIN risk_scores rs     ON r.supplier_id = rs.supplier_id
GROUP BY
    s.supplier_name, s.country, r.regulatory_compliance,
    r.last_audit_days_ago, rs.composite_score, rs.risk_tier
ORDER BY r.last_audit_days_ago DESC, rs.composite_score DESC;


-- ─────────────────────────────────────────────
-- QUERY 6: SPEND-RISK CONCENTRATION INDEX
-- Find suppliers where HIGH spend meets HIGH risk
-- (The most dangerous quadrant for pharma supply chains)
-- ─────────────────────────────────────────────
SELECT
    rs.supplier_name,
    rs.country,
    SUM(r.annual_spend_usd)             AS total_spend_usd,
    rs.composite_score,
    rs.risk_tier,
    ROUND(
        SUM(r.annual_spend_usd) * 100.0 /
        (SELECT SUM(annual_spend_usd) FROM supply_chain_records), 2
    )                                   AS spend_share_pct,
    ROUND(
        (SUM(r.annual_spend_usd) / 1e6) * (rs.composite_score / 100.0), 4
    )                                   AS spend_risk_index,
    CASE
        WHEN rs.composite_score >= 40
         AND SUM(r.annual_spend_usd) > 5000000
             THEN '⚠️  HIGH-SPEND HIGH-RISK — STRATEGIC PRIORITY'
        WHEN rs.composite_score >= 40
             THEN '🟠 HIGH RISK — MODERATE SPEND'
        WHEN SUM(r.annual_spend_usd) > 5000000
             THEN '💰 HIGH SPEND — MONITOR RISK'
        ELSE      '✅ ACCEPTABLE'
    END                                 AS strategic_flag
FROM risk_scores rs
JOIN supply_chain_records r ON rs.supplier_id = r.supplier_id
GROUP BY rs.supplier_name, rs.country, rs.composite_score, rs.risk_tier
ORDER BY spend_risk_index DESC;
