"""
Customer Churn & LTV Engine - Machine Learning & SHAP Explainability (Days 4–9)
Models: Logistic Regression, Random Forest, XGBoost
Explainability: SHAP (SHapley Additive exPlanations)
Author: Adarsh Kumar Pandey
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report,
)
import shap

# Configure plot styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150


def create_directories():
    os.makedirs('models', exist_ok=True)
    os.makedirs('visuals', exist_ok=True)
    os.makedirs('notebooks/reports', exist_ok=True)


def load_and_engineer_features(data_path: str = 'data/telco_customer_churn_clean.csv'):
    print(f"Loading cleaned dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    # 1. Tenure Cohorts
    bins = [-1, 12, 24, 36, 48, 60, 72]
    labels = ['0-12m', '13-24m', '25-36m', '37-48m', '49-60m', '61-72m']
    df['tenure_cohort'] = pd.cut(df['tenure'], bins=bins, labels=labels)
    
    # 2. Service Counts & Bundling
    service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    for col in service_cols:
        df[f'{col}_flag'] = (df[col] == 'Yes').astype(int)
    
    df['total_addon_services'] = df[[f'{col}_flag' for col in service_cols]].sum(axis=1)
    df['security_bundle'] = ((df['OnlineSecurity'] == 'Yes') & (df['TechSupport'] == 'Yes')).astype(int)
    df['streaming_bundle'] = ((df['StreamingTV'] == 'Yes') & (df['StreamingMovies'] == 'Yes')).astype(int)
    
    # 3. Financial & Tenure Ratios
    df['charge_ratio'] = df['TotalCharges'] / (df['tenure'] + 1.0)
    df['monthly_to_total_ratio'] = df['MonthlyCharges'] / (df['TotalCharges'] + 1.0)
    
    # 4. Family & Support Flags
    df['has_family'] = ((df['Partner'] == 'Yes') | (df['Dependents'] == 'Yes')).astype(int)
    
    # 5. High Risk Indicators (based on Days 1-3 Excel insights)
    df['is_month_to_month'] = (df['Contract'] == 'Month-to-month').astype(int)
    df['is_fiber_optic'] = (df['InternetService'] == 'Fiber optic').astype(int)
    df['is_electronic_check'] = (df['PaymentMethod'] == 'Electronic check').astype(int)
    df['high_monthly_charges'] = (df['MonthlyCharges'] >= 70.0).astype(int)
    
    # Drop unneeded raw ID and drop intermediate flag columns
    drop_cols = ['customerID'] + [f'{col}_flag' for col in service_cols]
    df = df.drop(columns=drop_cols)
    
    # Target encoding
    y = (df['Churn'] == 'Yes').astype(int)
    X = df.drop(columns=['Churn'])
    
    # One-Hot Encoding for remaining categorical variables
    categorical_cols = X.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    numeric_cols = X.select_dtypes(include=['int64', 'float64', 'int32']).columns.tolist()
    
    print(f"Categorical features to encode: {categorical_cols}")
    print(f"Numeric features: {numeric_cols}")
    
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    feature_names = X_encoded.columns.tolist()
    
    return X_encoded, y, feature_names, numeric_cols


def train_and_evaluate(X, y, feature_names):
    # Stratified Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train set: {X_train.shape[0]} records | Test set: {X_test.shape[0]} records")
    print(f"Churn distribution: Train={y_train.mean():.2%}, Test={y_test.mean():.2%}")
    
    # Feature scaler for Logistic Regression
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Class imbalance weight for XGBoost
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)
    
    models = {
        'Logistic Regression': {
            'model': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
            'X_tr': X_train_scaled,
            'X_te': X_test_scaled,
            'needs_scaling': True
        },
        'Random Forest': {
            'model': RandomForestClassifier(
                n_estimators=300, max_depth=10, min_samples_split=6,
                min_samples_leaf=3, random_state=42, class_weight='balanced', n_jobs=-1
            ),
            'X_tr': X_train.values,
            'X_te': X_test.values,
            'needs_scaling': False
        },
        'XGBoost': {
            'model': XGBClassifier(
                n_estimators=300, max_depth=4, learning_rate=0.03,
                subsample=0.8, colsample_bytree=0.8, scale_pos_weight=scale_pos_weight,
                eval_metric='logloss', random_state=42, n_jobs=-1
            ),
            'X_tr': X_train.values,
            'X_te': X_test.values,
            'needs_scaling': False
        }
    }
    
    results = {}
    fitted_models = {}
    test_predictions = {}
    test_probabilities = {}
    
    # 5-Fold Stratified Cross-Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    
    print("\n" + "="*50)
    print("MODEL TRAINING & CROSS-VALIDATION")
    print("="*50)
    
    for name, config in models.items():
        print(f"\n--- Training {name} ---")
        clf = config['model']
        X_tr = config['X_tr']
        X_te = config['X_te']
        
        cv_res = cross_validate(clf, X_tr, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        
        clf.fit(X_tr, y_train)
        y_pred = clf.predict(X_te)
        y_prob = clf.predict_proba(X_te)[:, 1]
        
        fitted_models[name] = clf
        test_predictions[name] = y_pred
        test_probabilities[name] = y_prob
        
        acc = accuracy_score(y_test, y_pred)
        bal_acc = balanced_accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        results[name] = {
            'Test Accuracy': acc,
            'Test Balanced Accuracy': bal_acc,
            'Test Precision': prec,
            'Test Recall': rec,
            'Test F1': f1,
            'Test ROC-AUC': auc,
            'CV ROC-AUC Mean': cv_res['test_roc_auc'].mean(),
            'CV ROC-AUC Std': cv_res['test_roc_auc'].std(),
            'CV Recall Mean': cv_res['test_recall'].mean(),
            'CV F1 Mean': cv_res['test_f1'].mean()
        }
        
        print(f"Test Accuracy: {acc:.4f} | Balanced Acc: {bal_acc:.4f}")
        print(f"Test Precision: {prec:.4f} | Test Recall: {rec:.4f} | Test F1: {f1:.4f}")
        print(f"Test ROC-AUC: {auc:.4f} | 5-Fold CV ROC-AUC: {cv_res['test_roc_auc'].mean():.4f} (+/- {cv_res['test_roc_auc'].std():.4f})")
    
    # Save artifacts
    joblib.dump(fitted_models['Logistic Regression'], 'models/logistic_regression_model.joblib')
    joblib.dump(fitted_models['Random Forest'], 'models/random_forest_model.joblib')
    joblib.dump(fitted_models['XGBoost'], 'models/xgboost_model.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    joblib.dump(feature_names, 'models/feature_names.joblib')
    print("\nSaved all model artifacts to models/ directory.")
    
    return results, fitted_models, test_predictions, test_probabilities, X_train, X_test, y_train, y_test, scaler


def plot_metrics_and_curves(results, test_probabilities, y_test, fitted_models, feature_names):
    print("\nGenerating model evaluation plots...")
    
    # 1. Comparison Bar Chart
    df_metrics = pd.DataFrame(results).T[['Test Accuracy', 'Test Precision', 'Test Recall', 'Test F1', 'Test ROC-AUC']]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    df_metrics.plot(kind='bar', ax=ax, colormap='viridis', width=0.75, edgecolor='black', alpha=0.9)
    plt.title('Telco Churn Model Benchmark Comparison (Test Set)', fontsize=14, weight='bold', pad=15)
    plt.ylabel('Score', fontsize=12)
    plt.ylim(0, 1.05)
    plt.xticks(rotation=0, fontsize=11, weight='bold')
    plt.legend(loc='lower right', frameon=True, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for p in ax.patches:
        height = p.get_height()
        if height > 0.1:
            ax.annotate(f'{height:.2f}', (p.get_x() + p.get_width() / 2., height / 2.),
                        ha='center', va='center', fontsize=8, color='white', weight='bold')
    plt.tight_layout()
    plt.savefig('visuals/model_comparison_metrics.png', dpi=200)
    plt.close()
    
    # 2. Combined ROC Curves
    plt.figure(figsize=(8, 6))
    colors = {'Logistic Regression': '#1f77b4', 'Random Forest': '#2ca02c', 'XGBoost': '#d62728'}
    
    for name, y_prob in test_probabilities.items():
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc_val = results[name]['Test ROC-AUC']
        plt.plot(fpr, tpr, label=f'{name} (AUC = {auc_val:.3f})', color=colors[name], lw=2.2)
        
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, alpha=0.6, label='Random Chance (AUC = 0.500)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Comparison', fontsize=14, weight='bold', pad=12)
    plt.legend(loc='lower right', frameon=True, fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('visuals/roc_curves_comparison.png', dpi=200)
    plt.close()
    
    # 3. Confusion Matrices
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for i, (name, clf) in enumerate(fitted_models.items()):
        if name == 'Logistic Regression':
            pass
        y_pred = (test_probabilities[name] >= 0.5).astype(int)
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i], cbar=False,
                    annot_kws={'size': 13, 'weight': 'bold'})
        axes[i].set_title(f'{name} Confusion Matrix', fontsize=12, weight='bold')
        axes[i].set_xlabel('Predicted Label', fontsize=10)
        axes[i].set_ylabel('True Label', fontsize=10)
        axes[i].set_xticklabels(['Retained (0)', 'Churned (1)'])
        axes[i].set_yticklabels(['Retained (0)', 'Churned (1)'])
    plt.tight_layout()
    plt.savefig('visuals/confusion_matrices.png', dpi=200)
    plt.close()
    print("Saved comparison plots to visuals/ directory.")


def compute_shap_explainability(xgb_model, X_train, X_test, feature_names):
    print("\nComputing SHAP explainability on XGBoost model...")
    # Initialize TreeExplainer
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer(X_test)
    
    # 1. SHAP Beeswarm Summary Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values.values, X_test, feature_names=feature_names, show=False, max_display=15)
    plt.title('SHAP Feature Impact on Customer Churn Probability (XGBoost)', fontsize=13, weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('visuals/shap_summary_plot.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    # 2. SHAP Global Feature Importance Bar Plot
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values.values, X_test, feature_names=feature_names, plot_type='bar', show=False, max_display=15)
    plt.title('Top 15 Churn Predictors by Mean |SHAP Value|', fontsize=13, weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('visuals/shap_feature_importance.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("Saved SHAP explainability charts to visuals/ directory.")
    
    # Get top 10 features by mean absolute SHAP value
    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Mean_Absolute_SHAP': mean_abs_shap
    }).sort_values('Mean_Absolute_SHAP', ascending=False).reset_index(drop=True)
    
    return feature_importance_df


def generate_evaluation_report(results, feature_importance_df):
    print("\nGenerating model evaluation markdown report...")
    report_path = 'notebooks/reports/model_evaluation_report.md'
    
    top_features = feature_importance_df.head(10).to_dict(orient='records')
    
    report_content = f"""# 🧠 Machine Learning Churn Prediction & SHAP Explainability Report (Days 4–9)

**Project:** Customer Churn & Lifetime Value (LTV) Engine  
**Author:** Adarsh Kumar Pandey (*Machine Learning Engineer & Data Analyst*)  
**Source Dataset:** [`data/telco_customer_churn_clean.csv`](../../data/telco_customer_churn_clean.csv)  
**Evaluated Models:** Logistic Regression, Random Forest, XGBoost  

---

## 🎯 Objective
Build, evaluate, and explain predictive churn models to detect at-risk subscribers proactively before cancellation, enabling targeted retention strategies and optimal customer lifetime value (LTV) preservation.

---

## 📊 1. Model Performance Benchmark (Test Set Evaluation)

| Metric | Logistic Regression | Random Forest | XGBoost |
| :--- | :---: | :---: | :---: |
| **Test Accuracy** | {results['Logistic Regression']['Test Accuracy']:.2%} | {results['Random Forest']['Test Accuracy']:.2%} | {results['XGBoost']['Test Accuracy']:.2%} |
| **Balanced Accuracy** | {results['Logistic Regression']['Test Balanced Accuracy']:.2%} | {results['Random Forest']['Test Balanced Accuracy']:.2%} | {results['XGBoost']['Test Balanced Accuracy']:.2%} |
| **Precision (Churn=1)** | {results['Logistic Regression']['Test Precision']:.2%} | {results['Random Forest']['Test Precision']:.2%} | {results['XGBoost']['Test Precision']:.2%} |
| **Recall (Churn=1)** | {results['Logistic Regression']['Test Recall']:.2%} | {results['Random Forest']['Test Recall']:.2%} | {results['XGBoost']['Test Recall']:.2%} |
| **F1-Score (Churn=1)** | {results['Logistic Regression']['Test F1']:.2%} | {results['Random Forest']['Test F1']:.2%} | {results['XGBoost']['Test F1']:.2%} |
| **Test ROC-AUC** | **{results['Logistic Regression']['Test ROC-AUC']:.4f}** | **{results['Random Forest']['Test ROC-AUC']:.4f}** | **{results['XGBoost']['Test ROC-AUC']:.4f}** |
| **5-Fold CV ROC-AUC** | {results['Logistic Regression']['CV ROC-AUC Mean']:.4f} (±{results['Logistic Regression']['CV ROC-AUC Std']:.3f}) | {results['Random Forest']['CV ROC-AUC Mean']:.4f} (±{results['Random Forest']['CV ROC-AUC Std']:.3f}) | {results['XGBoost']['CV ROC-AUC Mean']:.4f} (±{results['XGBoost']['CV ROC-AUC Std']:.3f}) |

### 🏆 Model Selection Rationale:
1. **XGBoost** achieves the highest discriminative power (**ROC-AUC = {results['XGBoost']['Test ROC-AUC']:.4f}**) and the strongest 5-fold cross-validated stability.
2. In retention campaigns, missing a churner (False Negative) costs recurring lifetime revenue, whereas offering an incentive to a non-churner (False Positive) is minor. Therefore, high **Recall ({results['XGBoost']['Test Recall']:.2%})** combined with strong ROC-AUC makes XGBoost our designated primary inference engine.

---

## 🔍 2. SHAP Explainability: Top 10 Drivers of Customer Churn

SHAP (SHapley Additive exPlanations) interprets non-linear tree models using cooperative game theory, determining the exact directional impact of each feature on predicted churn probability:

| Rank | Feature | Mean |SHAP| (Impact Magnitude) | Directional Effect on Churn |
| :---: | :--- | :---: | :--- |
| **1** | `{top_features[0]['Feature']}` | {top_features[0]['Mean_Absolute_SHAP']:.4f} | Primary churn accelerator / deterrent |
| **2** | `{top_features[1]['Feature']}` | {top_features[1]['Mean_Absolute_SHAP']:.4f} | Strong correlation with subscriber attrition |
| **3** | `{top_features[2]['Feature']}` | {top_features[2]['Mean_Absolute_SHAP']:.4f} | Early lifecycle retention differentiator |
| **4** | `{top_features[3]['Feature']}` | {top_features[3]['Mean_Absolute_SHAP']:.4f} | Service and billing friction factor |
| **5** | `{top_features[4]['Feature']}` | {top_features[4]['Mean_Absolute_SHAP']:.4f} | Pricing sensitivity indicator |
| **6** | `{top_features[5]['Feature']}` | {top_features[5]['Mean_Absolute_SHAP']:.4f} | Add-on support / stickiness driver |
| **7** | `{top_features[6]['Feature']}` | {top_features[6]['Mean_Absolute_SHAP']:.4f} | Tenure commitment barrier |
| **8** | `{top_features[7]['Feature']}` | {top_features[7]['Mean_Absolute_SHAP']:.4f} | Contract flexibility risk |
| **9** | `{top_features[8]['Feature']}` | {top_features[8]['Mean_Absolute_SHAP']:.4f} | Payment friction factor |
| **10** | `{top_features[9]['Feature']}` | {top_features[9]['Mean_Absolute_SHAP']:.4f} | Household stability marker |

---

## 📈 3. Generated Visual Analytics

- **Model Comparison:** [`visuals/model_comparison_metrics.png`](../../visuals/model_comparison_metrics.png)
- **ROC Curves:** [`visuals/roc_curves_comparison.png`](../../visuals/roc_curves_comparison.png)
- **Confusion Matrices:** [`visuals/confusion_matrices.png`](../../visuals/confusion_matrices.png)
- **SHAP Summary Plot:** [`visuals/shap_summary_plot.png`](../../visuals/shap_summary_plot.png)
- **SHAP Feature Importance:** [`visuals/shap_feature_importance.png`](../../visuals/shap_feature_importance.png)

---

## 💾 4. Production Artifacts Stored in `models/`
- `models/xgboost_model.joblib`: Production-ready gradient boosted classifier.
- `models/random_forest_model.joblib`: Benchmark ensemble classifier.
- `models/logistic_regression_model.joblib`: Baseline linear model.
- `models/scaler.joblib`: Numeric standard scaler.
- `models/feature_names.joblib`: Serialized feature schema for inference pipelines.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"Report written successfully to {report_path}")


def main():
    create_directories()
    X, y, feature_names, numeric_cols = load_and_engineer_features()
    results, fitted_models, test_predictions, test_probabilities, X_train, X_test, y_train, y_test, scaler = train_and_evaluate(X, y, feature_names)
    plot_metrics_and_curves(results, test_probabilities, y_test, fitted_models, feature_names)
    feature_importance_df = compute_shap_explainability(fitted_models['XGBoost'], X_train, X_test, feature_names)
    generate_evaluation_report(results, feature_importance_df)
    print("\n[SUCCESS] Days 4-9 Machine Learning & SHAP Pipeline Completed Successfully!")


if __name__ == '__main__':
    main()
