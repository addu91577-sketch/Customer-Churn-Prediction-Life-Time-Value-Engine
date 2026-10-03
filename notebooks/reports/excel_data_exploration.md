# 📑 Excel Data Exploration Report (Days 1–3)

**Project:** Customer Churn & Lifetime Value (LTV) Engine  
**Author:** Adarsh Kumar Pandey (*Data Analyst*)  
**Source Dataset:** Telco Customer Churn (IBM Watson / Kaggle)  
**Deliverable File:** [`excel/Telco_Customer_Churn_Exploration.xlsx`](../../excel/Telco_Customer_Churn_Exploration.xlsx)

---

## 🎯 Objective
Perform initial exploratory data auditing, hygiene verification, pivot table segmentation, cohort bucketing, and price outlier identification in Microsoft Excel before downstream SQL database ingestion and predictive modeling.

---

## 🔍 Step 1: Data Auditing & Quality Verification
- **Total Records:** 7,043 customers, 21 attribute columns.
- **Data Type Discrepancies & Blanks Found:**
  - `TotalCharges` initially loaded as a **Text/String** column instead of numeric currency.
  - **11 blank space characters (`" "`)** were detected in `TotalCharges`.
  - **Root Cause:** All 11 records have `tenure = 0` (brand new subscribers who joined during the billing cycle and have not yet incurred their first month-end bill).
- **Remediation:**
  - Replaced whitespace strings with `0.00` and cast the column to numeric float (`$#,##0.00`).
  - Added binary numeric flag `Churn_Numeric` (1 = Yes, 0 = No) for streamlined aggregation formulas.

---

## 📊 Step 2: Pivot Table 1 — Churn Risk by Contract Type
*Rows: `Contract` | Filter: `Churn` | Values: Total Customers, Churned, Churn Rate %, Average Monthly Charges*

| Contract Type | Total Customers | Churned Customers | Retained Customers | Churn Rate (%) | Retention Rate (%) | Avg Monthly Charges |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Month-to-month** | 3,875 | 1,655 | 2,220 | **42.71%** | 57.29% | $66.40 |
| **One year** | 1,473 | 166 | 1,307 | **11.27%** | 88.73% | $65.05 |
| **Two year** | 1,695 | 48 | 1,647 | **2.83%** | 97.17% | $60.77 |
| **Grand Total** | **7,043** | **1,869** | **5,174** | **26.54%** | **73.46%** | **$64.76** |

### Key Business Insights:
1. **88.55% of all churn** (1,655 out of 1,869 accounts) originates from **Month-to-Month** contracts.
2. Two-year contracts drop churn risk to just **2.83%**, confirming that long-term contract lock-in is the single most effective barrier against subscriber attrition.

---

## ⏱️ Step 3: Pivot Table 2 — Early-Tenure Cohort Risk
*Rows: `Tenure_Cohort` (Bucketed) | Values: Total Customers, Churned, Churn Rate %, % of Total Churn*

| Tenure Cohort | Total Customers | Churned Customers | Churn Rate (%) | % Share of All Churn | Avg Monthly Charges |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0–12 Months (New)** | 2,186 | 1,037 | **47.44%** | **55.48%** | $59.20 |
| **13–24 Months** | 1,024 | 294 | **28.71%** | **15.73%** | $63.26 |
| **25–36 Months** | 832 | 180 | **21.63%** | **9.63%** | $66.38 |
| **37–48 Months** | 762 | 145 | **19.03%** | **7.76%** | $68.37 |
| **49–60 Months** | 832 | 120 | **14.42%** | **6.42%** | $74.52 |
| **61–72 Months (Loyal)**| 1,407 | 93 | **6.61%** | **4.98%** | $74.48 |
| **Grand Total** | **7,043** | **1,869** | **26.54%** | **100.00%** | **$64.76** |

### Key Business Insights:
1. **The First Year Cliff:** Over half (**55.48%**) of all churners drop out within their first 12 months.
2. Once a customer reaches 24+ months of tenure, churn rates plummet below 20%, reaching an ultra-low **6.61%** after year 5.
3. Onboarding interventions must be heavily front-loaded in the first 90–180 days.

---

## 🎨 Step 4: Outlier & Price Sensitivity Analysis (Conditional Formatting)
- **Monthly Charges Distribution:**
  - Minimum: $18.25
  - 25th Percentile: $35.50
  - Median (50th): $70.35
  - 75th Percentile (Q3): $89.85
  - Maximum: $118.75
- **Conditional Formatting Applied:**
  - Column `MonthlyCharges` in sheet `Data_Cleaned` has a soft red highlight (`#FFC7CE`) with dark red text (`#9C0006`) applied to charges **≥ $70.00**.
  - Subscribers paying in the top tiers ($70–$118.75/month) show an elevated churn rate compared to lower-tier basic service subscribers, identifying price fatigue as an attrition driver.

---

## 📁 Workbook Structure in `Telco_Customer_Churn_Exploration.xlsx`
1. `Executive_Summary`: Executive KPI cards, metric table, and analytical observations.
2. `Pivot_Contract_Analysis`: Contract-wise churn breakdown with counts, percentages, and revenue.
3. `Pivot_Tenure_Cohorts`: 6-tier tenure risk buckets demonstrating early lifecycle drop-off.
4. `Data_Cleaned`: All 7,043 audited records with frozen panes, formatted currencies, and conditional formatting rules applied.
