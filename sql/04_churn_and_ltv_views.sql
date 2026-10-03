-- ===================================================================
-- Customer Churn & Lifetime Value (LTV) Engine
-- Days 10–12 & Days 13–16: Analytical SQL Views for Power BI Integration
-- ===================================================================

-- 1. Executive Summary KPIs View
CREATE OR REPLACE VIEW vw_churn_executive_kpis AS
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS total_churned,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges)::NUMERIC, 2) AS total_mrr,
    ROUND(AVG(MonthlyCharges)::NUMERIC, 2) AS avg_monthly_charges,
    ROUND(AVG(tenure)::NUMERIC, 1) AS avg_tenure_months,
    ROUND(SUM(TotalCharges)::NUMERIC, 2) AS total_historical_revenue
FROM customers;

-- 2. Contract & Tenure Risk Matrix View
CREATE OR REPLACE VIEW vw_contract_tenure_risk_matrix AS
SELECT 
    Contract,
    CASE 
        WHEN tenure <= 12 THEN '0-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 36 THEN '25-36 Months'
        WHEN tenure <= 48 THEN '37-48 Months'
        WHEN tenure <= 60 THEN '49-60 Months'
        ELSE '61-72 Months'
    END AS tenure_cohort,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS cohort_churn_rate_pct,
    ROUND(AVG(MonthlyCharges)::NUMERIC, 2) AS avg_monthly_charges,
    ROUND(SUM(MonthlyCharges * 12)::NUMERIC, 2) AS annual_contract_value
FROM customers
GROUP BY 1, 2
ORDER BY 1, 2;

-- 3. High-Risk Retention Targeting Queue View
CREATE OR REPLACE VIEW vw_high_risk_retention_queue AS
SELECT 
    customerID,
    gender,
    SeniorCitizen,
    tenure,
    Contract,
    InternetService,
    PaymentMethod,
    MonthlyCharges,
    TotalCharges,
    -- Estimated Annual Revenue at Risk
    ROUND((MonthlyCharges * 12)::NUMERIC, 2) AS annual_revenue,
    CASE 
        WHEN Contract = 'Month-to-month' AND MonthlyCharges >= 70 THEN 'High Priority: Contract Discount & Annual Upgrade'
        WHEN InternetService = 'Fiber optic' AND TechSupport = 'No' THEN 'High Priority: Onboarding Tech Support Pack'
        WHEN PaymentMethod = 'Electronic check' THEN 'Medium Priority: Switch to Auto-Pay Incentive'
        ELSE 'Proactive Customer Success Check-in'
    END AS retention_action
FROM customers
WHERE Churn = 'No' AND Contract = 'Month-to-month' AND tenure <= 24
ORDER BY MonthlyCharges DESC;

-- 4. Service Adoption & Friction Analysis View
CREATE OR REPLACE VIEW vw_service_adoption_vs_churn AS
SELECT 
    InternetService,
    OnlineSecurity,
    TechSupport,
    COUNT(*) AS total_subscribers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churn_count,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges)::NUMERIC, 2) AS avg_monthly_charge
FROM customers
WHERE InternetService <> 'No'
GROUP BY 1, 2, 3
ORDER BY churn_rate_pct DESC;

-- 5. Customer LTV Aggregation View
CREATE OR REPLACE VIEW vw_customer_ltv_aggregations AS
SELECT 
    Contract,
    PaymentMethod,
    InternetService,
    COUNT(*) AS customer_count,
    ROUND(AVG(TotalCharges)::NUMERIC, 2) AS avg_historical_charges,
    ROUND(AVG(MonthlyCharges * (tenure + 12))::NUMERIC, 2) AS projected_ltv,
    ROUND(SUM(MonthlyCharges * (tenure + 12))::NUMERIC, 2) AS total_segment_ltv
FROM customers
GROUP BY 1, 2, 3
ORDER BY total_segment_ltv DESC;
