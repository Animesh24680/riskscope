import numpy as np
import pandas as pd

np.random.seed(42)

N = 10000

age = np.clip(np.random.normal(40, 13, N).astype(int), 18, 70)

income = np.clip(
    np.random.lognormal(mean=10.8, sigma=0.6, size=N).astype(int),
    15000, 250000
)

credit_base = np.random.normal(680, 60, N).astype(int)
missed_payments = np.random.poisson(1.2, N)
dti_base = np.clip(np.random.beta(2, 5, N), 0.05, 0.8)

delinquent_prob = np.zeros(N)
delinquent_prob += ((credit_base < 620).astype(float) * 0.35)
delinquent_prob += ((credit_base >= 620) & (credit_base < 680)).astype(float) * 0.15
delinquent_prob += ((missed_payments >= 3).astype(float) * 0.25)
delinquent_prob += ((missed_payments == 2).astype(float) * 0.08)
delinquent_prob += ((dti_base > 0.4).astype(float) * 0.15)
delinquent_prob += ((dti_base > 0.6).astype(float) * 0.10)
delinquent_prob += ((age < 25).astype(float) * 0.05)
delinquent_prob += ((income < 30000).astype(float) * 0.05)
delinquent_prob = np.clip(delinquent_prob, 0.02, 0.92)
delinquent = (np.random.random(N) < delinquent_prob).astype(int)

credit_score = np.where(
    delinquent == 1,
    np.clip(credit_base - np.random.randint(20, 60, N), 300, 850),
    np.clip(credit_base, 300, 850)
)
missed_payments = np.where(
    delinquent == 1,
    np.clip(missed_payments + np.random.randint(0, 3, N), 0, 15),
    np.clip(missed_payments, 0, 8)
)
dti = np.where(
    delinquent == 1,
    np.clip(dti_base + np.random.uniform(0.05, 0.15, N), 0.05, 0.8),
    dti_base
)

df = pd.DataFrame({
    "Age": age,
    "Income": income,
    "Credit_Score": credit_score,
    "Missed_Payments": missed_payments,
    "Debt_to_Income_Ratio": dti.round(2),
    "Delinquent": delinquent,
})

print(f"Generated {len(df)} records")
print(f"Delinquent rate: {df['Delinquent'].mean():.1%}")
print(f"\nFeature ranges:")
for col in df.columns:
    print(f"  {col}: {df[col].min()} to {df[col].max()}")

output_path = "data/raw/delinquency_data.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved to {output_path}")
