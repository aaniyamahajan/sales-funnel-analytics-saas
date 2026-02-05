-- Sales Funnel Analysis SQL Queries
-- These queries analyze the CRM dataset to identify bottlenecks and conversion rates

-- =============================================================================
-- 1. FUNNEL OVERVIEW - Stage Distribution
-- =============================================================================

-- Count of opportunities by deal stage
SELECT
    deal_stage,
    COUNT(*) as opportunity_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM sales_pipeline
GROUP BY deal_stage
ORDER BY
    CASE deal_stage
        WHEN 'Prospecting' THEN 1
        WHEN 'Engaging' THEN 2
        WHEN 'Won' THEN 3
        WHEN 'Lost' THEN 4
    END;

-- =============================================================================
-- 2. CONVERSION RATES - Overall Funnel Performance
-- =============================================================================

-- Overall conversion rate (Won vs Total Closed)
SELECT
    COUNT(CASE WHEN deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN deal_stage = 'Lost' THEN 1 END) as lost_deals,
    COUNT(CASE WHEN deal_stage IN ('Won', 'Lost') THEN 1 END) as total_closed,
    ROUND(
        COUNT(CASE WHEN deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent
FROM sales_pipeline;

-- =============================================================================
-- 3. CONVERSION BY INDUSTRY (SECTOR)
-- =============================================================================

-- Win rate by industry sector
SELECT
    a.sector,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as lost_deals,
    COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END) as total_closed,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as total_revenue
FROM sales_pipeline sp
LEFT JOIN accounts a ON sp.account = a.account
WHERE a.sector IS NOT NULL
GROUP BY a.sector
ORDER BY win_rate_percent DESC;

-- =============================================================================
-- 4. CONVERSION BY COMPANY SIZE
-- =============================================================================

-- Win rate by company size (employee count buckets)
SELECT
    CASE
        WHEN a.employees < 100 THEN 'Small (< 100)'
        WHEN a.employees < 500 THEN 'Medium (100-499)'
        WHEN a.employees < 1000 THEN 'Large (500-999)'
        WHEN a.employees < 5000 THEN 'Enterprise (1000-4999)'
        ELSE 'Corporate (5000+)'
    END as company_size,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as lost_deals,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    ROUND(AVG(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value END), 2) as avg_deal_value
FROM sales_pipeline sp
LEFT JOIN accounts a ON sp.account = a.account
WHERE a.employees IS NOT NULL
GROUP BY
    CASE
        WHEN a.employees < 100 THEN 'Small (< 100)'
        WHEN a.employees < 500 THEN 'Medium (100-499)'
        WHEN a.employees < 1000 THEN 'Large (500-999)'
        WHEN a.employees < 5000 THEN 'Enterprise (1000-4999)'
        ELSE 'Corporate (5000+)'
    END
ORDER BY win_rate_percent DESC;

-- =============================================================================
-- 5. CONVERSION BY REVENUE TIER
-- =============================================================================

-- Win rate by company revenue tier
SELECT
    CASE
        WHEN a.revenue < 100 THEN 'Tier 1: < $100M'
        WHEN a.revenue < 500 THEN 'Tier 2: $100M-$499M'
        WHEN a.revenue < 1000 THEN 'Tier 3: $500M-$999M'
        WHEN a.revenue < 2500 THEN 'Tier 4: $1B-$2.5B'
        ELSE 'Tier 5: > $2.5B'
    END as revenue_tier,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END) as total_closed,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as total_revenue
FROM sales_pipeline sp
LEFT JOIN accounts a ON sp.account = a.account
WHERE a.revenue IS NOT NULL
GROUP BY
    CASE
        WHEN a.revenue < 100 THEN 'Tier 1: < $100M'
        WHEN a.revenue < 500 THEN 'Tier 2: $100M-$499M'
        WHEN a.revenue < 1000 THEN 'Tier 3: $500M-$999M'
        WHEN a.revenue < 2500 THEN 'Tier 4: $1B-$2.5B'
        ELSE 'Tier 5: > $2.5B'
    END
ORDER BY revenue_tier;

-- =============================================================================
-- 6. PRODUCT PERFORMANCE
-- =============================================================================

-- Win rate and revenue by product
SELECT
    sp.product,
    p.series,
    p.sales_price as list_price,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as lost_deals,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as total_revenue,
    ROUND(AVG(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value END), 2) as avg_deal_value
FROM sales_pipeline sp
LEFT JOIN products p ON sp.product = p.product
GROUP BY sp.product, p.series, p.sales_price
ORDER BY total_revenue DESC;

-- =============================================================================
-- 7. SALES AGENT PERFORMANCE
-- =============================================================================

-- Top performing sales agents
SELECT
    sp.sales_agent,
    st.manager,
    st.regional_office,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as lost_deals,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as total_revenue
FROM sales_pipeline sp
LEFT JOIN sales_teams st ON sp.sales_agent = st.sales_agent
GROUP BY sp.sales_agent, st.manager, st.regional_office
HAVING COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END) >= 10
ORDER BY win_rate_percent DESC, total_revenue DESC;

-- =============================================================================
-- 8. REGIONAL PERFORMANCE
-- =============================================================================

-- Performance by regional office
SELECT
    st.regional_office,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as lost_deals,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as win_rate_percent,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as total_revenue,
    COUNT(DISTINCT sp.sales_agent) as agent_count
FROM sales_pipeline sp
LEFT JOIN sales_teams st ON sp.sales_agent = st.sales_agent
WHERE st.regional_office IS NOT NULL
GROUP BY st.regional_office
ORDER BY total_revenue DESC;

-- =============================================================================
-- 9. SALES CYCLE ANALYSIS
-- =============================================================================

-- Average days from engagement to close by outcome
SELECT
    deal_stage,
    COUNT(*) as deal_count,
    ROUND(AVG(JULIANDAY(close_date) - JULIANDAY(engage_date)), 1) as avg_days_to_close,
    MIN(JULIANDAY(close_date) - JULIANDAY(engage_date)) as min_days,
    MAX(JULIANDAY(close_date) - JULIANDAY(engage_date)) as max_days
FROM sales_pipeline
WHERE deal_stage IN ('Won', 'Lost')
  AND engage_date IS NOT NULL
  AND close_date IS NOT NULL
GROUP BY deal_stage;

-- =============================================================================
-- 10. LEAD PRIORITIZATION SCORE COMPONENTS
-- =============================================================================

-- Account-level metrics for lead scoring
SELECT
    a.account,
    a.sector,
    a.revenue as company_revenue,
    a.employees,
    COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) as historical_wins,
    COUNT(CASE WHEN sp.deal_stage = 'Lost' THEN 1 END) as historical_losses,
    ROUND(
        COUNT(CASE WHEN sp.deal_stage = 'Won' THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN sp.deal_stage IN ('Won', 'Lost') THEN 1 END), 0),
    2) as account_win_rate,
    SUM(CASE WHEN sp.deal_stage = 'Won' THEN sp.close_value ELSE 0 END) as lifetime_value
FROM accounts a
LEFT JOIN sales_pipeline sp ON a.account = sp.account
GROUP BY a.account, a.sector, a.revenue, a.employees
ORDER BY lifetime_value DESC;

-- =============================================================================
-- 11. PIPELINE VALUE ANALYSIS
-- =============================================================================

-- Current pipeline value (opportunities still in progress)
SELECT
    deal_stage,
    COUNT(*) as opportunity_count,
    SUM(COALESCE(close_value, 0)) as pipeline_value
FROM sales_pipeline
WHERE deal_stage IN ('Prospecting', 'Engaging')
GROUP BY deal_stage;

-- =============================================================================
-- 12. TIME-BASED TRENDS
-- =============================================================================

-- Monthly win rate trends (for closed deals)
SELECT
    strftime('%Y-%m', close_date) as close_month,
    COUNT(CASE WHEN deal_stage = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN deal_stage = 'Lost' THEN 1 END) as lost_deals,
    ROUND(
        COUNT(CASE WHEN deal_stage = 'Won' THEN 1 END) * 100.0 /
        COUNT(*),
    2) as win_rate_percent,
    SUM(CASE WHEN deal_stage = 'Won' THEN close_value ELSE 0 END) as monthly_revenue
FROM sales_pipeline
WHERE deal_stage IN ('Won', 'Lost')
  AND close_date IS NOT NULL
GROUP BY strftime('%Y-%m', close_date)
ORDER BY close_month;
