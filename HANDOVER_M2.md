# Member 2 → Member 3 Handover

## Completed
- Exploratory Data Analysis completed
- Churn distribution analyzed
- Contract-wise churn analyzed
- Tenure-wise churn analyzed
- Monthly Charges analyzed
- Internet Service analyzed
- Payment Method analyzed
- Customer characteristics analyzed
- Business insights documented

## Main Files
- notebooks/03_exploratory_data_analysis.ipynb
- reports/business_insights.md
- visuals/

## Important Findings
1. Month-to-month contract customers account for the majority of churn.
2. Fiber Optic users experience higher churn rates than DSL users.
3. Customers paying higher Monthly Charges exhibit increased churn tendency.
4. Electronic Check users have the highest churn rate among all payment methods.

## Recommendations
Focus retention campaigns on high-risk segments: short tenure, month-to-month contracts, high monthly charges, and fiber optic services.

## For Member 3
Use the cleaned dataset (`Data/telco_customer_churn_clean.csv`) and EDA findings to build churn prediction models.

Potential important variables identified during EDA:
- Contract
- Tenure
- MonthlyCharges
- InternetService
- PaymentMethod
- SeniorCitizen
- TotalCharges
-