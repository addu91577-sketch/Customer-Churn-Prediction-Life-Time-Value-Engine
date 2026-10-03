"""
Customer Churn & LTV Engine - Enriched Power BI Dataset Generator
Combines raw customer attributes with machine learning churn probabilities,
Customer Lifetime Value (LTV) projections, Risk Tiers, and Actionable Recommendations.
Author: Adarsh Kumar Pandey
"""

import os
import joblib
import numpy as np
import pandas as pd


def generate_powerbi_dataset():
    print("Loading cleaned dataset and trained XGBoost model...")
    raw_df = pd.read_csv('data/telco_customer_churn_clean.csv')
    xgb_model = joblib.load('models/xgboost_model.joblib')
    feature_names = joblib.load('models/feature_names.joblib')
    
    df = raw_df.copy()
    
    # Feature Engineering (matching train_models.py pipeline)
    bins = [-1, 12, 24, 36, 48, 60, 72]
    labels = ['0-12m', '13-24m', '25-36m', '37-48m', '49-60m', '61-72m']
    df['tenure_cohort'] = pd.cut(df['tenure'], bins=bins, labels=labels)
    
    service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    for col in service_cols:
        df[f'{col}_flag'] = (df[col] == 'Yes').astype(int)
    
    df['total_addon_services'] = df[[f'{col}_flag' for col in service_cols]].sum(axis=1)
    df['security_bundle'] = ((df['OnlineSecurity'] == 'Yes') & (df['TechSupport'] == 'Yes')).astype(int)
    df['streaming_bundle'] = ((df['StreamingTV'] == 'Yes') & (df['StreamingMovies'] == 'Yes')).astype(int)
    
    df['charge_ratio'] = df['TotalCharges'] / (df['tenure'] + 1.0)
    df['monthly_to_total_ratio'] = df['MonthlyCharges'] / (df['TotalCharges'] + 1.0)
    df['has_family'] = ((df['Partner'] == 'Yes') | (df['Dependents'] == 'Yes')).astype(int)
    
    df['is_month_to_month'] = (df['Contract'] == 'Month-to-month').astype(int)
    df['is_fiber_optic'] = (df['InternetService'] == 'Fiber optic').astype(int)
    df['is_electronic_check'] = (df['PaymentMethod'] == 'Electronic check').astype(int)
    df['high_monthly_charges'] = (df['MonthlyCharges'] >= 70.0).astype(int)
    
    drop_cols = ['customerID'] + [f'{col}_flag' for col in service_cols]
    df_ml = df.drop(columns=drop_cols)
    
    X = df_ml.drop(columns=['Churn'])
    cat_cols = X.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    X_encoded = pd.get_dummies(X, columns=cat_cols, drop_first=True)
    
    # Ensure all feature columns match the trained model schema
    for col in feature_names:
        if col not in X_encoded.columns:
            X_encoded[col] = 0
    X_encoded = X_encoded[feature_names]
    
    print("Generating model predictions and churn probabilities...")
    churn_probs = xgb_model.predict_proba(X_encoded.values)[:, 1]
    
    # Build enriched Power BI dataset
    powerbi_df = raw_df.copy()
    
    # 1. Churn Risk Probability & Tiers
    powerbi_df['Churn_Probability'] = np.round(churn_probs, 4)
    powerbi_df['Predicted_Churn'] = np.where(churn_probs >= 0.50, 'Yes', 'No')
    
    def assign_risk_tier(prob):
        if prob >= 0.60:
            return 'High Risk'
        elif prob >= 0.30:
            return 'Medium Risk'
        else:
            return 'Low Risk'
            
    powerbi_df['Risk_Tier'] = [assign_risk_tier(p) for p in churn_probs]
    
    # 2. Tenure Cohorts
    powerbi_df['Tenure_Cohort'] = pd.cut(
        powerbi_df['tenure'],
        bins=[-1, 12, 24, 36, 48, 60, 72],
        labels=['0-12 Months', '13-24 Months', '25-36 Months', '37-48 Months', '49-60 Months', '61-72 Months']
    )
    
    # 3. Customer Lifetime Value (LTV) Calculation
    # Formula: LTV = TotalCharges + Expected Future Revenue
    # Expected Future Months = (1 - Churn_Probability) * Average Cohort Lifetime (capped at 48 months)
    margin = 0.80  # 80% gross contribution margin
    expected_future_months = np.maximum(1, np.round((1.0 - churn_probs) * 36, 1))
    powerbi_df['Expected_Future_Months'] = expected_future_months
    powerbi_df['Expected_Future_Revenue'] = np.round(powerbi_df['MonthlyCharges'] * expected_future_months, 2)
    powerbi_df['Customer_LTV'] = np.round(powerbi_df['TotalCharges'] + powerbi_df['Expected_Future_Revenue'] * margin, 2)
    
    # 4. Revenue at Risk (Annualized MRR * Churn Probability)
    powerbi_df['Annual_Revenue_At_Risk'] = np.round(powerbi_df['MonthlyCharges'] * 12.0 * powerbi_df['Churn_Probability'], 2)
    
    # 5. Strategic Retention Recommendations
    def prescribe_action(row):
        if row['Risk_Tier'] == 'High Risk':
            if row['Contract'] == 'Month-to-month' and row['MonthlyCharges'] >= 70:
                return 'Offer 1-Year Contract with 15% Discount Bundle'
            elif row['InternetService'] == 'Fiber optic' and row['TechSupport'] == 'No':
                return 'Free Premium Tech Support & Speed Optimization Onboarding'
            elif row['PaymentMethod'] == 'Electronic check':
                return 'Auto-Pay Enrollment with $10 Billing Credit'
            else:
                return 'Dedicated Retention Call & Plan Re-evaluation'
        elif row['Risk_Tier'] == 'Medium Risk':
            if row['OnlineSecurity'] == 'No' or row['OnlineBackup'] == 'No':
                return 'Cross-sell Cybersecurity Protection Pack'
            else:
                return 'Quarterly Customer Satisfaction Check-in'
        else:
            return 'Upsell Premium Streaming & Loyalty Rewards'
            
    powerbi_df['Recommended_Retention_Action'] = powerbi_df.apply(prescribe_action, axis=1)
    
    # Re-order columns logically for clean Power BI tabular modeling
    out_csv = 'data/telco_churn_powerbi_dataset.csv'
    powerbi_df.to_csv(out_csv, index=False)
    print(f"Enriched Power BI dataset successfully saved to {out_csv} ({len(powerbi_df)} rows)")
    
    # Summary Metrics
    print("\n--- Power BI Dataset Summary ---")
    print("Risk Tiers Breakdown:")
    print(powerbi_df['Risk_Tier'].value_counts())
    print(f"Total Annual Revenue at Risk: ${powerbi_df['Annual_Revenue_At_Risk'].sum():,.2f}")
    print(f"Average Customer LTV: ${powerbi_df['Customer_LTV'].mean():,.2f}")


if __name__ == '__main__':
    generate_powerbi_dataset()
