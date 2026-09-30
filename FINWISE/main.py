import pandas as pd

# Load the CSV you created
df = pd.read_csv("stock_volatility.csv")

# Ask the user for their risk preference
risk_preference = input("Enter your risk preference (Low / Medium / High): ").capitalize()

# Define risk category boundaries
def classify_risk(std_dev):
    if std_dev < 0.015:
        return "Low"
    elif std_dev < 0.03:
        return "Medium"
    else:
        return "High"


# Add a Risk column based on the std_dev
df['Risk'] = df['Volatility'].apply(classify_risk)

# Filter based on user preference
filtered_stocks = df[df['Risk'] == risk_preference]

# Show results
print(f"\nStocks classified as {risk_preference} risk:")
print(filtered_stocks.head(10))  # Show top 10

# Optional: Save to new file
filtered_stocks.to_csv(f"{risk_preference.lower()}_risk_stocks.csv", index=False)
