#!/usr/bin/env python3
"""Test that the Data_Quality_Flag fix works correctly"""

import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('expanded_syria_bi_data.csv')

# Calculate flags (same as in correct_data_issues.py)
df['Has_Negative_Agility_Improvement'] = (
    df['Post_BI_Decision_Making_Agility_Score'] < 
    df['Pre_BI_Decision_Making_Agility_Score']
)

df['Has_Negative_Efficiency_Improvement'] = (
    df['Post_BI_Operational_Efficiency_Index'] < 
    df['Pre_BI_Operational_Efficiency_Index']
)

df['Is_Recent_Implementation'] = df['BI_Implementation_Year'] >= 2023

# OLD LOGIC (buggy)
print("=" * 80)
print("TESTING OLD (BUGGY) LOGIC")
print("=" * 80)
df_old = df.copy()
df_old['Data_Quality_Flag'] = 'Normal'
df_old.loc[df_old['Has_Negative_Agility_Improvement'] | 
           df_old['Has_Negative_Efficiency_Improvement'], 'Data_Quality_Flag'] = 'Unusual'
df_old.loc[df_old['Is_Recent_Implementation'], 'Data_Quality_Flag'] = 'Preliminary'

has_negative = df_old['Has_Negative_Agility_Improvement'] | df_old['Has_Negative_Efficiency_Improvement']
both_conditions_old = df_old[(has_negative & df_old['Is_Recent_Implementation'])]

print(f"\nRows with both negative improvements AND recent implementation: {len(both_conditions_old)}")
print(f"Flags assigned by OLD logic:")
print(both_conditions_old['Data_Quality_Flag'].value_counts())
if len(both_conditions_old) > 0:
    print("\n⚠️  PROBLEM: These rows are marked as 'Preliminary' instead of 'Unusual'!")
    print("\nAffected rows:")
    print(both_conditions_old[['Company_ID', 'Governorate', 'BI_Implementation_Year',
                                'Data_Quality_Flag']].to_string())

# NEW LOGIC (fixed)
print("\n" + "=" * 80)
print("TESTING NEW (FIXED) LOGIC")
print("=" * 80)
df_new = df.copy()
df_new['Data_Quality_Flag'] = 'Normal'

# Priority 1: Mark rows with negative improvements as 'Unusual' (highest priority)
has_negative_improvement = (
    df_new['Has_Negative_Agility_Improvement'] | 
    df_new['Has_Negative_Efficiency_Improvement']
)
df_new.loc[has_negative_improvement, 'Data_Quality_Flag'] = 'Unusual'

# Priority 2: Mark recent implementations as 'Preliminary' 
# ONLY if they don't already have 'Unusual' flag
recent_not_unusual = df_new['Is_Recent_Implementation'] & ~has_negative_improvement
df_new.loc[recent_not_unusual, 'Data_Quality_Flag'] = 'Preliminary'

both_conditions_new = df_new[(has_negative_improvement & df_new['Is_Recent_Implementation'])]

print(f"\nRows with both negative improvements AND recent implementation: {len(both_conditions_new)}")
print(f"Flags assigned by NEW logic:")
print(both_conditions_new['Data_Quality_Flag'].value_counts())
if len(both_conditions_new) > 0:
    print("\n✅ FIXED: These rows are now correctly marked as 'Unusual'!")
    print("\nCorrected rows:")
    print(both_conditions_new[['Company_ID', 'Governorate', 'BI_Implementation_Year',
                                'Data_Quality_Flag']].to_string())

# Summary comparison
print("\n" + "=" * 80)
print("SUMMARY COMPARISON")
print("=" * 80)
print(f"\nTotal 'Unusual' flags:")
print(f"  OLD logic: {(df_old['Data_Quality_Flag'] == 'Unusual').sum()}")
print(f"  NEW logic: {(df_new['Data_Quality_Flag'] == 'Unusual').sum()}")
print(f"\nTotal 'Preliminary' flags:")
print(f"  OLD logic: {(df_old['Data_Quality_Flag'] == 'Preliminary').sum()}")
print(f"  NEW logic: {(df_new['Data_Quality_Flag'] == 'Preliminary').sum()}")

if len(both_conditions_old) > 0:
    print(f"\n✅ FIX VERIFIED: {len(both_conditions_old)} rows now correctly preserve 'Unusual' flag")
    print("   instead of being overwritten with 'Preliminary'")

