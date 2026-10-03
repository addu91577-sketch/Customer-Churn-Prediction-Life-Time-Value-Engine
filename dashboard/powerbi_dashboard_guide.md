# 📈 Power BI Customer Churn & LTV Dashboard Guide (Days 13–16)

**Project:** Customer Churn & Lifetime Value (LTV) Engine  
**Author:** Adarsh Kumar Pandey  
**Dataset Path:** [`data/telco_churn_powerbi_dataset.csv`](../data/telco_churn_powerbi_dataset.csv)  
**DAX Measures File:** [`dashboard/dax_measures.md`](dax_measures.md)  
**SQL Analytics Views:** [`sql/04_churn_and_ltv_views.sql`](../sql/04_churn_and_ltv_views.sql)  

---

## 🚀 Fast 2-Minute Setup in Power BI Desktop

1. Open **Power BI Desktop** (already installed on this machine as `MicrosoftPowerBIDesktop`).
2. Click **Get Data** > **Text/CSV** > Select:  
   `C:\Users\Iba Zaidi\Desktop\Telco _Customer_Churn\data\telco_churn_powerbi_dataset.csv`  
   *(Or connect to PostgreSQL using `sql/04_churn_and_ltv_views.sql` views).*
3. Verify all 7,043 rows are detected and click **Load**.
4. Go to **Modeling** tab > **New Measure** and copy-paste the DAX formulas from [`dax_measures.md`](dax_measures.md).

---

## 🎨 Theme & Color Palette

| Purpose | HEX Code | Sample Visual Element |
| :--- | :---: | :--- |
| **Primary Brand / Retained** | `#0078D4` | Retained customer bars, standard cards |
| **High Churn Risk / Critical** | `#D83B01` | Churned bars, High-Risk tier, revenue loss cards |
| **Medium Risk / Warning** | `#FFB900` | Medium risk cohorts, caution alerts |
| **Low Risk / Healthy LTV** | `#107C41` | Healthy subscriber counts, positive ROI |
| **Dark Neutral / Typography** | `#242424` | Metric labels, chart titles |
| **Card Backgrounds** | `#F3F2F1` | KPI background containers |

---

## 🖥️ 3-Page Dashboard Blueprint

### 📄 Page 1: Executive Churn & Revenue Health Overview
*Target Audience: C-Suite, VP of Customer Success*

1. **Top KPI Ribbon (5 Cards):**
   * **Total Customers:** `7,043`
   * **Churn Rate:** `26.54%` (Benchmark: Telecom industry target is <20%)
   * **Monthly Recurring Revenue (MRR):** `$456.12K`
   * **Lost MRR (Monthly Churn Loss):** `$139.13K`
   * **Annual Revenue at Risk:** `$2.45M` (Flagged in Dark Red `#D83B01`)
2. **Chart 1 (Donut Chart):** Customer Distribution by Risk Tier (Low Risk: 46.3%, Medium Risk: 21.6%, High Risk: 32.1%).
3. **Chart 2 (Stacked Bar Chart):** Churn Rate by Contract Type (*Month-to-Month: 42.71% vs Two-Year: 2.83%*).
4. **Chart 3 (100% Stacked Column Chart):** Churn Rate across 6 Tenure Cohorts (*0-12m, 13-24m, 25-36m, 37-48m, 49-60m, 61-72m*).
5. **Interactive Slicers:** `InternetService`, `Contract`, `PaymentMethod`, `SeniorCitizen`.

---

### 📄 Page 2: Risk Diagnostics & Early Warning System
*Target Audience: Operations, Retention Managers, Support Leads*

1. **Top Metric Cards:**
   * **High Risk Active Subscribers:** `1,142`
   * **Avg Churn Probability:** `26.54%`
   * **Fiber Optic Churn Rate:** `41.89%`
   * **Electronic Check Churn Rate:** `45.29%`
2. **Visual 1 (Clustered Bar Chart):** Impact of Add-on Service Adoption on Churn (Online Security, Tech Support, Online Backup, Device Protection).
3. **Visual 2 (Scatter Plot):** `MonthlyCharges` (X-Axis) vs `Churn_Probability` (Y-Axis) sized by `TotalCharges` and colored by `InternetService`.
4. **Visual 3 (Heatmap Matrix):** Contract Type vs Payment Method with conditional color formatting on Churn Rate.

---

### 📄 Page 3: Customer Lifetime Value (LTV) & Retention Targeting Engine
*Target Audience: Growth Marketing, Retention Campaign Specialists*

1. **Top Campaign KPI Cards:**
   * **Average Customer LTV:** `$3,310.42`
   * **Active Portfolio Projected LTV:** `$18.2M`
   * **Campaign Target Pool:** `1,142 High-Risk Active Accounts`
   * **Projected Campaign ROI:** `+485%` (Based on 25% save rate vs $35 retention cost)
2. **Interactive Retention Action Queue (Data Table):**
   * Columns: `customerID`, `Contract`, `tenure`, `MonthlyCharges`, `Churn_Probability`, `Customer_LTV`, `Annual_Revenue_At_Risk`, `Recommended_Retention_Action`.
   * Sort: `Annual_Revenue_At_Risk` Descending.
3. **Chart (Treemap / Bar):** Value at Risk by `Recommended_Retention_Action` (e.g. *Offer 1-Year Contract with 15% Discount Bundle*, *Auto-Pay Enrollment Credit*).
