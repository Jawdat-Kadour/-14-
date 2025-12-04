#!/usr/bin/env python3
"""Verify the Data_Quality_Flag assignment issue"""

import pandas as pd

# Load data
df = pd.read_csv('expanded_syria_bi_data.csv')

# Calculate flags
df['Has_Negative_Agility'] = (
    df['Post_BI_Decision_Making_Agility_Score'] < 
    df['Pre_BI_Decision_Making_Agility_Score']
)

df['Has_Negative_Efficiency'] = (
    df['Post_BI_Operational_Efficiency_Index'] < 
    df['Pre_BI_Operational_Efficiency_Index']
)

df['Is_Recent'] = df['BI_Implementation_Year'] >= 2023

# Check for rows with both conditions
has_negative = df['Has_Negative_Agility'] | df['Has_Negative_Efficiency']
both_conditions = df[has_negative & df['Is_Recent']]

print("=" * 80)
print("VERIFYING Data_Quality_Flag ASSIGNMENT ISSUE")
print("=" * 80)
print(f"\nTotal rows: {len(df)}")
print(f"\nRows with negative improvements: {has_negative.sum()}")
print(f"  - Negative Agility: {df['Has_Negative_Agility'].sum()}")
print(f"  - Negative Efficiency: {df['Has_Negative_Efficiency'].sum()}")
print(f"\nRows with recent implementation (2023+): {df['Is_Recent'].sum()}")
print(f"\nRows with BOTH negative improvements AND recent implementation: {len(both_conditions)}")

if len(both_conditions) > 0:
    print("\n⚠️  ISSUE CONFIRMED: These rows would lose 'Unusual' flag!")
    print("\nSample of affected rows:")
    print(both_conditions[['Company_ID', 'Governorate', 'BI_Implementation_Year', 
                           'Pre_BI_Decision_Making_Agility_Score',
                           'Post_BI_Decision_Making_Agility_Score',
                           'Pre_BI_Operational_Efficiency_Index',
                           'Post_BI_Operational_Efficiency_Index']].head(10))
else:
    print("\n✅ No rows found with both conditions (issue may not affect current data)")

print("\n" + "=" * 80)

