# 📊 Power BI DAX Measures Library

**Project:** Customer Churn & Lifetime Value (LTV) Engine  
**Dataset Table:** `'telco_churn_powerbi_dataset'`  
**Author:** Adarsh Kumar Pandey  

Copy and paste these measures directly into Power BI Desktop via **Modeling > New Measure**.

---

## 1. Core Volume & Churn KPI Measures

```dax
Total Customers = 
COUNTROWS('telco_churn_powerbi_dataset')
```

```dax
Churned Customers = 
CALCULATE(
    COUNTROWS('telco_churn_powerbi_dataset'),
    'telco_churn_powerbi_dataset'[Churn] = "Yes"
)
```

```dax
Active Customers = 
CALCULATE(
    COUNTROWS('telco_churn_powerbi_dataset'),
    'telco_churn_powerbi_dataset'[Churn] = "No"
)
```

```dax
Churn Rate % = 
DIVIDE([Churned Customers], [Total Customers], 0)
```

```dax
Retention Rate % = 
1 - [Churn Rate %]
```

---

## 2. Revenue & Financial Impact Measures

```dax
Total MRR = 
SUM('telco_churn_powerbi_dataset'[MonthlyCharges])
```

```dax
Active MRR = 
CALCULATE(
    SUM('telco_churn_powerbi_dataset'[MonthlyCharges]),
    'telco_churn_powerbi_dataset'[Churn] = "No"
)
```

```dax
Churned MRR (Lost Monthly Revenue) = 
CALCULATE(
    SUM('telco_churn_powerbi_dataset'[MonthlyCharges]),
    'telco_churn_powerbi_dataset'[Churn] = "Yes"
)
```

```dax
Total Historical Revenue = 
SUM('telco_churn_powerbi_dataset'[TotalCharges])
```

```dax
Average Monthly Charge = 
AVERAGE('telco_churn_powerbi_dataset'[MonthlyCharges])
```

```dax
Total Annual Revenue At Risk = 
SUM('telco_churn_powerbi_dataset'[Annual_Revenue_At_Risk])
```

---

## 3. Machine Learning Predictive Risk Measures

```dax
Average Churn Probability = 
AVERAGE('telco_churn_powerbi_dataset'[Churn_Probability])
```

```dax
High Risk Active Customers = 
CALCULATE(
    COUNTROWS('telco_churn_powerbi_dataset'),
    'telco_churn_powerbi_dataset'[Risk_Tier] = "High Risk",
    'telco_churn_powerbi_dataset'[Churn] = "No"
)
```

```dax
High Risk Revenue Exposure = 
CALCULATE(
    SUM('telco_churn_powerbi_dataset'[Annual_Revenue_At_Risk]),
    'telco_churn_powerbi_dataset'[Risk_Tier] = "High Risk",
    'telco_churn_powerbi_dataset'[Churn] = "No"
)
```

```dax
High Risk Customer % = 
DIVIDE([High Risk Active Customers], [Active Customers], 0)
```

---

## 4. Customer Lifetime Value (LTV) Measures

```dax
Average Customer LTV = 
AVERAGE('telco_churn_powerbi_dataset'[Customer_LTV])
```

```dax
Total Portfolio LTV = 
SUM('telco_churn_powerbi_dataset'[Customer_LTV])
```

```dax
Active Portfolio LTV = 
CALCULATE(
    SUM('telco_churn_powerbi_dataset'[Customer_LTV]),
    'telco_churn_powerbi_dataset'[Churn] = "No"
)
```

```dax
Average Expected Future Lifetime (Months) = 
AVERAGE('telco_churn_powerbi_dataset'[Expected_Future_Months])
```

---

## 5. Retention Campaign Economics & Projected ROI

```dax
Projected Retention Saves (25% Campaign Success) = 
[High Risk Active Customers] * 0.25
```

```dax
Projected Annual Revenue Saved = 
[High Risk Revenue Exposure] * 0.25
```

```dax
Estimated Campaign Cost ($35 per target) = 
[High Risk Active Customers] * 35
```

```dax
Projected Campaign Net ROI % = 
DIVIDE(
    [Projected Annual Revenue Saved] - [Estimated Campaign Cost ($35 per target)],
    [Estimated Campaign Cost ($35 per target)],
    0
)
```
