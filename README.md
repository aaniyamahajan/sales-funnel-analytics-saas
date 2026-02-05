# Sales Funnel & Lead Prioritization Analytics

## Business Problem
How can a SaaS company identify sales funnel bottlenecks and prioritize high-value opportunities to improve conversion rates?

## Dataset
This project uses a publicly available, fictional CRM dataset from Kaggle containing:
- **8,800** sales opportunities
- **85** customer accounts
- **35** sales agents across 3 regions
- **7** products across 3 series

## Objectives
- [x] Analyze the sales funnel to identify stage-level drop-offs
- [x] Compare conversion rates across industries and company sizes
- [x] Build a simple lead prioritization model to support sales decision-making

## Tools & Technologies
- **SQL** - Funnel analysis queries
- **Python** - Data analysis and modeling
  - Pandas - Data manipulation
  - Matplotlib - Visualization
  - Scikit-learn - Lead scoring model
- **GitHub** - Version control

## Project Structure

```
├── data/                           # CRM datasets
│   ├── accounts.csv                # Customer accounts (85 records)
│   ├── sales_pipeline.csv          # Sales opportunities (8,800 records)
│   ├── sales_teams.csv             # Sales agents (35 records)
│   ├── products.csv                # Product catalog (7 products)
│   └── data_dictionary.csv         # Schema documentation
│
├── sql/
│   └── funnel_analysis.sql         # 12 SQL queries for funnel metrics
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb      # Data prep & feature engineering
│   ├── 02_funnel_analysis.ipynb    # Funnel analysis & visualizations
│   └── 03_lead_prioritization.ipynb # ML lead scoring model
│
└── visuals/                        # Generated charts and outputs
```

## Analysis Components

### SQL Queries (`sql/funnel_analysis.sql`)
- Funnel stage distribution
- Conversion rates by sector, company size, and revenue tier
- Product and sales agent performance
- Regional analysis
- Sales cycle duration metrics
- Lead scoring data components

### Notebooks

**01 - Data Cleaning**
- Load and explore all datasets
- Handle missing values and fix data quality issues
- Create derived features (company size categories, revenue tiers)
- Merge datasets into master analysis table

**02 - Funnel Analysis**
- Stage-level drop-off analysis
- Conversion rate comparisons across segments
- Product and regional performance insights
- Sales cycle duration patterns
- Key findings summary

**03 - Lead Prioritization**
- Train Random Forest classifier on historical win/loss data
- Identify key predictive factors
- Score current pipeline opportunities
- Assign priority tiers (High/Medium/Low)

## Getting Started

1. Run the data cleaning notebook first:
   ```
   jupyter notebook notebooks/01_data_cleaning.ipynb
   ```

2. Run the funnel analysis:
   ```
   jupyter notebook notebooks/02_funnel_analysis.ipynb
   ```

3. Generate lead scores:
   ```
   jupyter notebook notebooks/03_lead_prioritization.ipynb
   ```

## Status
Project complete - Core analysis and modeling implemented
