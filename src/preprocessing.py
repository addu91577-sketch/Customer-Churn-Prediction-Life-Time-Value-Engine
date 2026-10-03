import pandas as pd

# Load dataset
df = pd.read_csv("../data/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Convert TotalCharges to numeric
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

# Fill missing TotalCharges with 0
df["TotalCharges"] = df["TotalCharges"].fillna(0)

# Verify missing values are handled
print("Missing TotalCharges after cleaning:", df["TotalCharges"].isna().sum())

# Check dataset shape
print("Dataset shape:", df.shape)

# Check missing values in all columns
print("\nMissing values by column:")
print(df.isnull().sum())

# Check data types
print("\nData types:")
print(df.dtypes)

# Separate numerical and categorical columns
numerical_columns = df.select_dtypes(include=["int64", "float64"]).columns
categorical_columns = df.select_dtypes(include=["object"]).columns

print("\nNumerical columns:")
print(list(numerical_columns))

print("\nCategorical columns:")
print(list(categorical_columns))

# Remove customer ID because it is only an identifier
df = df.drop(columns=["customerID"])

print("\nColumns after removing customerID:")
print(df.columns.tolist())

# Final dataset check
print("\nFinal dataset shape:", df.shape)
print("\nFinal data types:")
print(df.dtypes)