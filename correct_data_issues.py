#!/usr/bin/env python3
"""
Data Correction Script
Corrects identified issues in the Syria BI dataset
"""

import pandas as pd
import numpy as np
from datetime import datetime

def correct_data_issues():
    """Correct identified data issues"""
    
    print("Loading data...")
    df = pd.read_csv('expanded_syria_bi_data.csv')
    
    original_count = len(df)
    corrections_made = []
    
    # 1. Add data source flag
    print("\n1. Adding data source flags...")
    df['Data_Source'] = df['Reference'].apply(
        lambda x: 'Synthetic' if 'Synthetic' in str(x) else 'Research'
    )
    corrections_made.append(f"Added Data_Source column: {df['Data_Source'].value_counts().to_dict()}")
    
    # 2. Fix calculation inconsistencies (if any)
    print("2. Verifying calculation consistency...")
    
    # Recalculate improvements to ensure accuracy
    df['Decision_Making_Agility_Improvement_Recalc'] = (
        df['Post_BI_Decision_Making_Agility_Score'] - 
        df['Pre_BI_Decision_Making_Agility_Score']
    )
    
    df['Operational_Efficiency_Improvement_Recalc'] = (
        df['Post_BI_Operational_Efficiency_Index'] - 
        df['Pre_BI_Operational_Efficiency_Index']
    )
    
    df['Data_Driven_Decisions_Improvement_Recalc'] = (
        df['Post_BI_Data_Driven_Decisions_Percentage'] - 
        df['Pre_BI_Data_Driven_Decisions_Percentage']
    )
    
    # Check for significant differences
    agility_diff = (df['Decision_Making_Agility_Improvement'] - 
                    df['Decision_Making_Agility_Improvement_Recalc']).abs()
    if (agility_diff > 0.01).any():
        corrections_made.append(f"Found {agility_diff[agility_diff > 0.01].count()} agility calculation discrepancies")
        # Use recalculated values
        df['Decision_Making_Agility_Improvement'] = df['Decision_Making_Agility_Improvement_Recalc']
    
    efficiency_diff = (df['Operational_Efficiency_Improvement'] - 
                       df['Operational_Efficiency_Improvement_Recalc']).abs()
    if (efficiency_diff > 1.0).any():
        corrections_made.append(f"Found {efficiency_diff[efficiency_diff > 1.0].count()} efficiency calculation discrepancies")
        df['Operational_Efficiency_Improvement'] = df['Operational_Efficiency_Improvement_Recalc']
    
    data_driven_diff = (df['Data_Driven_Decisions_Improvement'] - 
                        df['Data_Driven_Decisions_Improvement_Recalc']).abs()
    if (data_driven_diff > 0.01).any():
        corrections_made.append(f"Found {data_driven_diff[data_driven_diff > 0.01].count()} data-driven calculation discrepancies")
        df['Data_Driven_Decisions_Improvement'] = df['Data_Driven_Decisions_Improvement_Recalc']
    
    # Remove temporary columns
    df = df.drop(columns=[
        'Decision_Making_Agility_Improvement_Recalc',
        'Operational_Efficiency_Improvement_Recalc',
        'Data_Driven_Decisions_Improvement_Recalc'
    ])
    
    # 3. Add data quality flags
    print("3. Adding data quality flags...")
    
    # Flag unusual cases
    df['Has_Negative_Agility_Improvement'] = (
        df['Post_BI_Decision_Making_Agility_Score'] < 
        df['Pre_BI_Decision_Making_Agility_Score']
    )
    
    df['Has_Negative_Efficiency_Improvement'] = (
        df['Post_BI_Operational_Efficiency_Index'] < 
        df['Pre_BI_Operational_Efficiency_Index']
    )
    
    df['Is_Recent_Implementation'] = df['BI_Implementation_Year'] >= 2023
    
    df['Data_Quality_Flag'] = 'Normal'
    df.loc[df['Has_Negative_Agility_Improvement'] | 
           df['Has_Negative_Efficiency_Improvement'], 'Data_Quality_Flag'] = 'Unusual'
    df.loc[df['Is_Recent_Implementation'], 'Data_Quality_Flag'] = 'Preliminary'
    
    unusual_count = (df['Data_Quality_Flag'] == 'Unusual').sum()
    preliminary_count = (df['Data_Quality_Flag'] == 'Preliminary').sum()
    
    corrections_made.append(f"Flagged {unusual_count} unusual cases and {preliminary_count} preliminary cases")
    
    # 4. Standardize reference format
    print("4. Standardizing references...")
    
    # Keep original references but add standardized version
    df['Reference_Standardized'] = df['Reference'].apply(
        lambda x: 'Hayan Hamdan (2022) - Effect of Business Intelligence System on Organizational Agility: Evidence from Syria' 
        if 'Hayan Hamdan' in str(x) 
        else ('Synthetic Data Model (2025) - Simulated BI Impact Analysis' 
              if 'Synthetic' in str(x) 
              else str(x))
    )
    
    corrections_made.append(f"Standardized {len(df)} references")
    
    # 5. Add metadata
    print("5. Adding metadata...")
    
    df['Data_Last_Verified'] = datetime.now().strftime('%Y-%m-%d')
    df['Data_Version'] = '1.1'
    
    # Save corrected data
    output_file = 'expanded_syria_bi_data_corrected.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ Corrections complete!")
    print(f"   Original records: {original_count}")
    print(f"   Corrected records: {len(df)}")
    print(f"   Output file: {output_file}")
    
    print("\n📋 Summary of corrections:")
    for correction in corrections_made:
        print(f"   - {correction}")
    
    # Generate correction report
    with open('data_corrections_log.txt', 'w', encoding='utf-8') as f:
        f.write("DATA CORRECTIONS LOG\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Original Records: {original_count}\n")
        f.write(f"Corrected Records: {len(df)}\n\n")
        f.write("Corrections Made:\n")
        for i, correction in enumerate(corrections_made, 1):
            f.write(f"{i}. {correction}\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("New Columns Added:\n")
        f.write("  - Data_Source: 'Research' or 'Synthetic'\n")
        f.write("  - Has_Negative_Agility_Improvement: Boolean flag\n")
        f.write("  - Has_Negative_Efficiency_Improvement: Boolean flag\n")
        f.write("  - Is_Recent_Implementation: Boolean flag (2023+)\n")
        f.write("  - Data_Quality_Flag: 'Normal', 'Unusual', or 'Preliminary'\n")
        f.write("  - Reference_Standardized: Standardized reference format\n")
        f.write("  - Data_Last_Verified: Date of last verification\n")
        f.write("  - Data_Version: Version number\n")
    
    print(f"\n📄 Correction log saved to: data_corrections_log.txt")
    
    return df

if __name__ == "__main__":
    corrected_df = correct_data_issues()
    print("\n✅ All corrections applied successfully!")

