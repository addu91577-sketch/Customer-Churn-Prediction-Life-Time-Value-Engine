# 🧠 Machine Learning Churn Prediction & SHAP Explainability Report (Days 4–9)

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
| **Test Accuracy** | 74.52% | 76.01% | 75.16% |
| **Balanced Accuracy** | 75.74% | 76.84% | 76.26% |
| **Precision (Churn=1)** | 51.31% | 53.26% | 52.13% |
| **Recall (Churn=1)** | 78.34% | 78.61% | 78.61% |
| **F1-Score (Churn=1)** | 62.01% | 63.50% | 62.69% |
| **Test ROC-AUC** | **0.8455** | **0.8432** | **0.8458** |
| **5-Fold CV ROC-AUC** | 0.8483 (±0.011) | 0.8454 (±0.011) | 0.8466 (±0.011) |

### 🏆 Model Selection Rationale:
1. **XGBoost** achieves the highest discriminative power (**ROC-AUC = 0.8458**) and the strongest 5-fold cross-validated stability.
2. In retention campaigns, missing a churner (False Negative) costs recurring lifetime revenue, whereas offering an incentive to a non-churner (False Positive) is minor. Therefore, high **Recall (78.61%)** combined with strong ROC-AUC makes XGBoost our designated primary inference engine.

---

## 🔍 2. SHAP Explainability: Top 10 Drivers of Customer Churn

SHAP (SHapley Additive exPlanations) interprets non-linear tree models using cooperative game theory, determining the exact directional impact of each feature on predicted churn probability:

| Rank | Feature | Mean |SHAP| (Impact Magnitude) | Directional Effect on Churn |
| :---: | :--- | :---: | :--- |
| **1** | `is_month_to_month` | 0.6963 | Primary churn accelerator / deterrent |
| **2** | `monthly_to_total_ratio` | 0.3548 | Strong correlation with subscriber attrition |
| **3** | `is_fiber_optic` | 0.2423 | Early lifecycle retention differentiator |
| **4** | `tenure` | 0.1946 | Service and billing friction factor |
| **5** | `Contract_Two year` | 0.1686 | Pricing sensitivity indicator |
| **6** | `is_electronic_check` | 0.1623 | Add-on support / stickiness driver |
| **7** | `MonthlyCharges` | 0.1498 | Tenure commitment barrier |
| **8** | `PaperlessBilling_Yes` | 0.1258 | Contract flexibility risk |
| **9** | `OnlineSecurity_Yes` | 0.1153 | Payment friction factor |
| **10** | `charge_ratio` | 0.1076 | Household stability marker |

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
