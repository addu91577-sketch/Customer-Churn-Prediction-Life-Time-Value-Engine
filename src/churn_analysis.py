import pandas as pd

# Load dataset
df = pd.read_csv("../data/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Churn counts
churn_counts = df["Churn"].value_counts()

print("Churn Counts:")
print(churn_counts)

# Churn percentages
churn_percentages = df["Churn"].value_counts(normalize=True) * 100

print("\nChurn Percentages:")
print(churn_percentages)

# Churn summary
total_customers = len(df)

print("\nTotal Customers:", total_customers)
print("Churn Rate:", round(churn_percentages["Yes"], 2), "%")
print("Retention Rate:", round(churn_percentages["No"], 2), "%")

# Check missing values in Churn
print("\nMissing Churn Values:", df["Churn"].isnull().sum())