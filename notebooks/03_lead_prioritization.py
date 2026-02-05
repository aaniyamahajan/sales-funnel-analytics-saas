"""
Lead Prioritization Model
Builds a machine learning model to prioritize leads based on conversion probability

Objectives:
1. Identify key factors that predict deal success
2. Build a scoring model to prioritize leads
3. Apply the model to current pipeline opportunities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

pd.set_option('display.max_columns', None)

# Load the master dataset
df = pd.read_csv('../data/master_dataset.csv')
df['engage_date'] = pd.to_datetime(df['engage_date'])
df['close_date'] = pd.to_datetime(df['close_date'])

print(f"Total records: {len(df):,}")
print(f"Deal stages: {df['deal_stage'].value_counts().to_dict()}")

# =============================================================================
# 1. Prepare Training Data
# =============================================================================

# Filter to closed deals only for training
closed_df = df[df['deal_stage'].isin(['Won', 'Lost'])].copy()
print(f"\nClosed deals for training: {len(closed_df):,}")
print(f"Win/Loss ratio: {closed_df['is_won'].value_counts().to_dict()}")

# Select features for the model
features = ['sector', 'company_size', 'revenue_tier', 'product', 'regional_office', 'series']

# Check for missing values
print("\nMissing values in features:")
print(closed_df[features].isnull().sum())

# Drop rows with missing feature values
model_df = closed_df.dropna(subset=features)
print(f"\nRecords after dropping missing: {len(model_df):,}")

# Encode categorical variables
encoders = {}
X = pd.DataFrame()

for feature in features:
    le = LabelEncoder()
    X[feature] = le.fit_transform(model_df[feature])
    encoders[feature] = le

y = model_df['is_won'].values

print(f"\nFeature matrix shape: {X.shape}")
print(f"Target distribution: Won={y.sum()}, Lost={len(y)-y.sum()}")

# =============================================================================
# 2. Train the Model
# =============================================================================

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")

# Train Random Forest model
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=20,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
print("\n✓ Model trained successfully!")

# Evaluate model
y_pred = rf_model.predict(X_test)
y_prob = rf_model.predict_proba(X_test)[:, 1]

print("\n=== MODEL PERFORMANCE ===")
print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_prob):.3f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Lost', 'Won']))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n=== FEATURE IMPORTANCE ===")
print(feature_importance.to_string(index=False))

# =============================================================================
# 3. Score Current Pipeline
# =============================================================================

# Get current pipeline
pipeline_df = df[df['deal_stage'].isin(['Prospecting', 'Engaging'])].copy()
print(f"\nCurrent pipeline opportunities: {len(pipeline_df):,}")

# Scoring function
def score_lead(row):
    try:
        input_data = pd.DataFrame([{
            'sector': encoders['sector'].transform([row['sector']])[0],
            'company_size': encoders['company_size'].transform([row['company_size']])[0],
            'revenue_tier': encoders['revenue_tier'].transform([row['revenue_tier']])[0],
            'product': encoders['product'].transform([row['product']])[0],
            'regional_office': encoders['regional_office'].transform([row['regional_office']])[0],
            'series': encoders['series'].transform([row['series']])[0]
        }])
        probability = rf_model.predict_proba(input_data)[0, 1]
        return round(probability * 100, 1)
    except:
        return None

pipeline_df['lead_score'] = pipeline_df.apply(score_lead, axis=1)

# Create priority tiers
def assign_priority(score):
    if pd.isna(score):
        return 'Unscored'
    elif score >= 70:
        return 'High Priority'
    elif score >= 50:
        return 'Medium Priority'
    else:
        return 'Low Priority'

pipeline_df['priority'] = pipeline_df['lead_score'].apply(assign_priority)

print("\n=== PIPELINE PRIORITY DISTRIBUTION ===")
print(pipeline_df['priority'].value_counts())

# Save prioritized pipeline
output_cols = [
    'opportunity_id', 'account', 'product', 'deal_stage', 'sales_agent',
    'sector', 'company_size', 'revenue_tier', 'regional_office',
    'lead_score', 'priority'
]

pipeline_output = pipeline_df[output_cols].sort_values('lead_score', ascending=False)
pipeline_output.to_csv('../data/prioritized_pipeline.csv', index=False)

print("\n✓ Prioritized pipeline saved to: data/prioritized_pipeline.csv")
print("✓ Lead prioritization complete!")
