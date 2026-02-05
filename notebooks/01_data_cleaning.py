"""
Data Cleaning & Preparation
Sales Funnel Analytics Project

Objectives:
- Load all CRM datasets
- Identify and handle missing values
- Fix data type issues
- Create cleaned datasets for analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# =============================================================================
# 1. Load Datasets
# =============================================================================

# Load all datasets
accounts = pd.read_csv('../data/accounts.csv')
sales_pipeline = pd.read_csv('../data/sales_pipeline.csv')
sales_teams = pd.read_csv('../data/sales_teams.csv')
products = pd.read_csv('../data/products.csv')

print(f"Accounts: {accounts.shape[0]} rows, {accounts.shape[1]} columns")
print(f"Sales Pipeline: {sales_pipeline.shape[0]} rows, {sales_pipeline.shape[1]} columns")
print(f"Sales Teams: {sales_teams.shape[0]} rows, {sales_teams.shape[1]} columns")
print(f"Products: {products.shape[0]} rows, {products.shape[1]} columns")

# =============================================================================
# 2. Explore Data Structure
# =============================================================================

print("=== ACCOUNTS ===")
print(accounts.info())
print("\n")
print(accounts.head())

print("\n=== SALES PIPELINE ===")
print(sales_pipeline.info())
print("\n")
print(sales_pipeline.head())

print("\n=== SALES TEAMS ===")
print(sales_teams.info())
print("\n")
print(sales_teams.head())

print("\n=== PRODUCTS ===")
print(products.info())
print("\n")
print(products.head())

# =============================================================================
# 3. Check for Missing Values
# =============================================================================

def check_missing(df, name):
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    result = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
    result = result[result['Missing Count'] > 0]
    if len(result) > 0:
        print(f"\n{name} - Missing Values:")
        print(result)
    else:
        print(f"\n{name} - No missing values")
    return result

check_missing(accounts, 'Accounts')
check_missing(sales_pipeline, 'Sales Pipeline')
check_missing(sales_teams, 'Sales Teams')
check_missing(products, 'Products')

# =============================================================================
# 4. Clean Sales Pipeline Data
# =============================================================================

# Check deal stages
print("\nDeal Stages:")
print(sales_pipeline['deal_stage'].value_counts())

# Convert date columns to datetime
sales_pipeline['engage_date'] = pd.to_datetime(sales_pipeline['engage_date'], errors='coerce')
sales_pipeline['close_date'] = pd.to_datetime(sales_pipeline['close_date'], errors='coerce')

# Verify conversion
print("\nDate column types:")
print(f"engage_date: {sales_pipeline['engage_date'].dtype}")
print(f"close_date: {sales_pipeline['close_date'].dtype}")

# Calculate days to close for closed deals
sales_pipeline['days_to_close'] = (sales_pipeline['close_date'] - sales_pipeline['engage_date']).dt.days

# Check the calculation
closed_deals = sales_pipeline[sales_pipeline['deal_stage'].isin(['Won', 'Lost'])]
print("\nDays to close statistics (closed deals):")
print(closed_deals['days_to_close'].describe())

# Create is_won flag for easier analysis
sales_pipeline['is_won'] = (sales_pipeline['deal_stage'] == 'Won').astype(int)
sales_pipeline['is_closed'] = sales_pipeline['deal_stage'].isin(['Won', 'Lost']).astype(int)

print("\nNew columns added:")
print(sales_pipeline[['deal_stage', 'is_won', 'is_closed']].head(10))

# =============================================================================
# 5. Clean Accounts Data
# =============================================================================

# Check sectors
print("\nSectors:")
print(accounts['sector'].value_counts())

# Fix typo in sector (technolgy -> technology)
accounts['sector'] = accounts['sector'].replace('technolgy', 'technology')

print("\nSectors after fix:")
print(accounts['sector'].value_counts())

# Create company size categories
def categorize_size(employees):
    if pd.isna(employees):
        return 'Unknown'
    elif employees < 100:
        return 'Small'
    elif employees < 500:
        return 'Medium'
    elif employees < 1000:
        return 'Large'
    elif employees < 5000:
        return 'Enterprise'
    else:
        return 'Corporate'

accounts['company_size'] = accounts['employees'].apply(categorize_size)

print("\nCompany Size Distribution:")
print(accounts['company_size'].value_counts())

# Create revenue tier categories
def categorize_revenue(revenue):
    if pd.isna(revenue):
        return 'Unknown'
    elif revenue < 100:
        return 'Tier 1: < $100M'
    elif revenue < 500:
        return 'Tier 2: $100M-$499M'
    elif revenue < 1000:
        return 'Tier 3: $500M-$999M'
    elif revenue < 2500:
        return 'Tier 4: $1B-$2.5B'
    else:
        return 'Tier 5: > $2.5B'

accounts['revenue_tier'] = accounts['revenue'].apply(categorize_revenue)

print("\nRevenue Tier Distribution:")
print(accounts['revenue_tier'].value_counts())

# =============================================================================
# 6. Merge Datasets for Analysis
# =============================================================================

# Create master dataset by merging all tables
master_df = sales_pipeline.merge(accounts, on='account', how='left')
master_df = master_df.merge(sales_teams, on='sales_agent', how='left')
master_df = master_df.merge(products, on='product', how='left')

print(f"\nMaster dataset shape: {master_df.shape}")
print(f"\nColumns: {master_df.columns.tolist()}")

# Check the merged data
print("\nMaster dataset preview:")
print(master_df.head())

# Check for any join issues
print("\nJoin quality check:")
print("Records with missing account info:", master_df['sector'].isna().sum())
print("Records with missing sales team info:", master_df['manager'].isna().sum())
print("Records with missing product info:", master_df['series'].isna().sum())

# =============================================================================
# 7. Save Cleaned Data
# =============================================================================

# Save cleaned individual datasets
accounts.to_csv('../data/accounts_cleaned.csv', index=False)
sales_pipeline.to_csv('../data/sales_pipeline_cleaned.csv', index=False)

# Save master dataset
master_df.to_csv('../data/master_dataset.csv', index=False)

print("\n✓ Cleaned datasets saved:")
print("- data/accounts_cleaned.csv")
print("- data/sales_pipeline_cleaned.csv")
print("- data/master_dataset.csv")

# =============================================================================
# 8. Data Summary
# =============================================================================

print("\n" + "="*50)
print("DATA SUMMARY")
print("="*50)
print(f"\nTotal Opportunities: {len(sales_pipeline):,}")
print(f"Total Accounts: {len(accounts):,}")
print(f"Total Sales Agents: {len(sales_teams):,}")
print(f"Total Products: {len(products):,}")

print(f"\n--- Deal Stage Breakdown ---")
for stage, count in sales_pipeline['deal_stage'].value_counts().items():
    pct = count / len(sales_pipeline) * 100
    print(f"{stage}: {count:,} ({pct:.1f}%)")

won_deals = sales_pipeline[sales_pipeline['deal_stage'] == 'Won']
print(f"\n--- Revenue Summary ---")
print(f"Total Revenue (Won Deals): ${won_deals['close_value'].sum():,.0f}")
print(f"Average Deal Value: ${won_deals['close_value'].mean():,.0f}")
print(f"Median Deal Value: ${won_deals['close_value'].median():,.0f}")

print("\n✓ Data cleaning complete!")
