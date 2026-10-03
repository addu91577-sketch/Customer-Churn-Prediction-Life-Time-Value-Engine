-- Total Customers Count
SELECT COUNT(*) FROM customers;

-- Churn Breakdown
SELECT Churn, COUNT(*) 
FROM customers 
GROUP BY Churn;

-- Contract Breakdown
SELECT Contract, COUNT(*) 
FROM customers 
GROUP BY Contract;

-- Internet Service Breakdown
SELECT InternetService, COUNT(*) 
FROM customers 
GROUP BY InternetService;
