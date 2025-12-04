#!/usr/bin/env python3
"""
Comprehensive Data Verification Script
Verifies accuracy, consistency, and reliability of the Syria BI dataset
"""

import pandas as pd
import json
from collections import Counter
import numpy as np

# Official 14 governorates of Syria (verified from official sources)
OFFICIAL_GOVERNORATES = {
    'Aleppo', 'Damascus', 'Homs', 'Hama', 'Latakia', 'Tartus', 
    'Idlib', 'Daraa', 'As-Suwayda', 'Quneitra', 'Rif Dimashq',
    'Al-Hasakah', 'Ar-Raqqah', 'Deir ez-Zor'
}

# Expected industries (common business sectors)
EXPECTED_INDUSTRIES = {
    'Telecommunications', 'Healthcare', 'Finance', 'Services',
    'Manufacturing', 'Education', 'Retail'
}

def verify_governorates(df):
    """Verify governorate names match official list"""
    issues = []
    found_govs = set(df['Governorate'].unique())
    
    # Check for missing governorates
    missing = OFFICIAL_GOVERNORATES - found_govs
    if missing:
        issues.append(f"Missing governorates: {missing}")
    
    # Check for extra/unrecognized governorates
    extra = found_govs - OFFICIAL_GOVERNORATES
    if extra:
        issues.append(f"Unrecognized governorates: {extra}")
    
    # Check for typos or variations
    variations = {}
    for gov in found_govs:
        if gov not in OFFICIAL_GOVERNORATES:
            # Find closest match
            for official in OFFICIAL_GOVERNORATES:
                if gov.lower() in official.lower() or official.lower() in gov.lower():
                    variations[gov] = official
                    break
    
    return {
        'status': 'PASS' if not issues else 'ISSUES',
        'issues': issues,
        'found_count': len(found_govs),
        'expected_count': len(OFFICIAL_GOVERNORATES),
        'variations': variations
    }

def verify_data_ranges(df):
    """Verify data ranges are reasonable"""
    issues = []
    warnings = []
    
    # Check Pre-BI Agility (should be 1-10 scale, typically lower)
    pre_agility = df['Pre_BI_Decision_Making_Agility_Score']
    if pre_agility.min() < 1.0 or pre_agility.max() > 10.0:
        issues.append(f"Pre-BI Agility out of expected range (1-10): {pre_agility.min():.2f} - {pre_agility.max():.2f}")
    if pre_agility.max() > 7.0:
        warnings.append(f"Pre-BI Agility unusually high: max = {pre_agility.max():.2f}")
    
    # Check Post-BI Agility (should be 1-10 scale, typically higher)
    post_agility = df['Post_BI_Decision_Making_Agility_Score']
    if post_agility.min() < 1.0 or post_agility.max() > 10.0:
        issues.append(f"Post-BI Agility out of expected range (1-10): {post_agility.min():.2f} - {post_agility.max():.2f}")
    if post_agility.min() < 4.0:
        warnings.append(f"Post-BI Agility unusually low: min = {post_agility.min():.2f}")
    
    # Check Efficiency Index (should be 0-100)
    pre_eff = df['Pre_BI_Operational_Efficiency_Index']
    post_eff = df['Post_BI_Operational_Efficiency_Index']
    if pre_eff.min() < 0 or pre_eff.max() > 100:
        issues.append(f"Pre-BI Efficiency out of range (0-100): {pre_eff.min():.2f} - {pre_eff.max():.2f}")
    if post_eff.min() < 0 or post_eff.max() > 100:
        issues.append(f"Post-BI Efficiency out of range (0-100): {post_eff.min():.2f} - {post_eff.max():.2f}")
    
    # Check Percentage fields (should be 0-100)
    percentage_fields = [
        'Pre_BI_Data_Driven_Decisions_Percentage',
        'Post_BI_Data_Driven_Decisions_Percentage',
        'Revenue_Growth_After_BI_Percentage',
        'Cost_Reduction_After_BI_Percentage',
        'Customer_Satisfaction_Increase_After_BI_Percentage',
        'Market_Share_Increase_After_BI_Percentage'
    ]
    
    for field in percentage_fields:
        values = df[field]
        if values.min() < 0 or values.max() > 100:
            issues.append(f"{field} out of range (0-100): {values.min():.2f} - {values.max():.2f}")
    
    # Check improvement calculations
    df['calc_agility_improvement'] = df['Post_BI_Decision_Making_Agility_Score'] - df['Pre_BI_Decision_Making_Agility_Score']
    df['calc_efficiency_improvement'] = df['Post_BI_Operational_Efficiency_Index'] - df['Pre_BI_Operational_Efficiency_Index']
    df['calc_data_driven_improvement'] = df['Post_BI_Data_Driven_Decisions_Percentage'] - df['Pre_BI_Data_Driven_Decisions_Percentage']
    
    # Check if calculated improvements match stored values (allowing for floating point errors)
    agility_diff = (df['calc_agility_improvement'] - df['Decision_Making_Agility_Improvement']).abs()
    if (agility_diff > 0.01).any():
        issues.append(f"Agility improvement calculation mismatch in {agility_diff[agility_diff > 0.01].count()} rows")
    
    efficiency_diff = (df['calc_efficiency_improvement'] - df['Operational_Efficiency_Improvement']).abs()
    if (efficiency_diff > 1.0).any():  # Allow larger tolerance for efficiency
        issues.append(f"Efficiency improvement calculation mismatch in {efficiency_diff[efficiency_diff > 1.0].count()} rows")
    
    data_driven_diff = (df['calc_data_driven_improvement'] - df['Data_Driven_Decisions_Improvement']).abs()
    if (data_driven_diff > 0.01).any():
        issues.append(f"Data-driven improvement calculation mismatch in {data_driven_diff[data_driven_diff > 0.01].count()} rows")
    
    return {
        'status': 'PASS' if not issues else 'ISSUES',
        'issues': issues,
        'warnings': warnings
    }

def verify_temporal_consistency(df):
    """Verify temporal consistency (BI implementation years)"""
    issues = []
    warnings = []
    
    # Check BI implementation years
    bi_years = sorted(df['BI_Implementation_Year'].unique())
    current_year = 2024
    
    # Check for future dates
    future_years = [y for y in bi_years if y > current_year]
    if future_years:
        issues.append(f"Future BI implementation years found: {future_years}")
    
    # Check for unrealistic past dates (before 2000)
    old_years = [y for y in bi_years if y < 2000]
    if old_years:
        issues.append(f"Unrealistically old BI implementation years: {old_years}")
    
    # Check if post-BI metrics make sense relative to implementation year
    # Companies with BI in 2024 shouldn't have extensive post-BI data yet
    recent_implementations = df[df['BI_Implementation_Year'] >= 2023]
    if len(recent_implementations) > 0:
        warnings.append(f"{len(recent_implementations)} companies implemented BI in 2023-2024, post-BI metrics may be preliminary")
    
    return {
        'status': 'PASS' if not issues else 'ISSUES',
        'issues': issues,
        'warnings': warnings,
        'year_range': f"{min(bi_years)} - {max(bi_years)}"
    }

def verify_logical_consistency(df):
    """Verify logical consistency (e.g., post-BI should generally be better than pre-BI)"""
    issues = []
    warnings = []
    
    # Post-BI agility should generally be higher than Pre-BI
    negative_agility = df[df['Post_BI_Decision_Making_Agility_Score'] < df['Pre_BI_Decision_Making_Agility_Score']]
    if len(negative_agility) > 0:
        warnings.append(f"{len(negative_agility)} companies show decreased agility after BI (may be valid but unusual)")
    
    # Post-BI efficiency should generally be higher
    negative_efficiency = df[df['Post_BI_Operational_Efficiency_Index'] < df['Pre_BI_Operational_Efficiency_Index']]
    if len(negative_efficiency) > 0:
        warnings.append(f"{len(negative_efficiency)} companies show decreased efficiency after BI (may be valid but unusual)")
    
    # Post-BI data-driven decisions should generally be higher
    negative_data_driven = df[df['Post_BI_Data_Driven_Decisions_Percentage'] < df['Pre_BI_Data_Driven_Decisions_Percentage']]
    if len(negative_data_driven) > 0:
        warnings.append(f"{len(negative_data_driven)} companies show decreased data-driven decisions after BI (may be valid but unusual)")
    
    # Check for unrealistic improvements
    large_agility_jump = df[df['Decision_Making_Agility_Improvement'] > 7.0]
    if len(large_agility_jump) > 0:
        warnings.append(f"{len(large_agility_jump)} companies show very large agility improvements (>7 points)")
    
    return {
        'status': 'PASS',
        'issues': issues,
        'warnings': warnings
    }

def verify_reference_consistency(df):
    """Verify reference field consistency"""
    issues = []
    
    # Check if all references are the same
    references = df['Reference'].unique()
    if len(references) > 1:
        warnings = [f"Multiple references found: {len(references)} unique references"]
        # Check if they're all variations of the same study
        base_ref = "Hayan Hamdan (2022)"
        non_matching = [r for r in references if base_ref not in r]
        if non_matching:
            issues.append(f"Non-matching references: {non_matching[:3]}")
    else:
        warnings = []
    
    return {
        'status': 'PASS' if not issues else 'ISSUES',
        'issues': issues,
        'warnings': warnings,
        'reference_count': len(references),
        'primary_reference': references[0] if len(references) > 0 else None
    }

def generate_verification_report(df):
    """Generate comprehensive verification report"""
    print("=" * 80)
    print("DATA VERIFICATION REPORT - Syria BI Dataset")
    print("=" * 80)
    print(f"\nDataset Overview:")
    print(f"  Total Records: {len(df):,}")
    print(f"  Total Columns: {len(df.columns)}")
    print(f"  Date Range: {df['BI_Implementation_Year'].min()} - {df['BI_Implementation_Year'].max()}")
    
    print("\n" + "=" * 80)
    print("1. GOVERNORATE VERIFICATION")
    print("=" * 80)
    gov_result = verify_governorates(df)
    print(f"Status: {gov_result['status']}")
    print(f"Found: {gov_result['found_count']} governorates")
    print(f"Expected: {gov_result['expected_count']} governorates")
    if gov_result['issues']:
        for issue in gov_result['issues']:
            print(f"  ⚠️  {issue}")
    if gov_result.get('variations'):
        print(f"  ℹ️  Variations found: {gov_result['variations']}")
    
    print("\n" + "=" * 80)
    print("2. DATA RANGE VERIFICATION")
    print("=" * 80)
    range_result = verify_data_ranges(df)
    print(f"Status: {range_result['status']}")
    if range_result['issues']:
        for issue in range_result['issues']:
            print(f"  ❌ {issue}")
    if range_result['warnings']:
        for warning in range_result['warnings']:
            print(f"  ⚠️  {warning}")
    
    print("\n" + "=" * 80)
    print("3. TEMPORAL CONSISTENCY VERIFICATION")
    print("=" * 80)
    temporal_result = verify_temporal_consistency(df)
    print(f"Status: {temporal_result['status']}")
    print(f"Year Range: {temporal_result['year_range']}")
    if temporal_result['issues']:
        for issue in temporal_result['issues']:
            print(f"  ❌ {issue}")
    if temporal_result['warnings']:
        for warning in temporal_result['warnings']:
            print(f"  ⚠️  {warning}")
    
    print("\n" + "=" * 80)
    print("4. LOGICAL CONSISTENCY VERIFICATION")
    print("=" * 80)
    logical_result = verify_logical_consistency(df)
    print(f"Status: {logical_result['status']}")
    if logical_result['issues']:
        for issue in logical_result['issues']:
            print(f"  ❌ {issue}")
    if logical_result['warnings']:
        for warning in logical_result['warnings']:
            print(f"  ⚠️  {warning}")
    
    print("\n" + "=" * 80)
    print("5. REFERENCE VERIFICATION")
    print("=" * 80)
    ref_result = verify_reference_consistency(df)
    print(f"Status: {ref_result['status']}")
    print(f"Reference Count: {ref_result['reference_count']}")
    if ref_result['primary_reference']:
        print(f"Primary Reference: {ref_result['primary_reference'][:100]}...")
    if ref_result['issues']:
        for issue in ref_result['issues']:
            print(f"  ❌ {issue}")
    if ref_result['warnings']:
        for warning in ref_result['warnings']:
            print(f"  ⚠️  {warning}")
    
    print("\n" + "=" * 80)
    print("6. DATA QUALITY SUMMARY")
    print("=" * 80)
    
    # Calculate overall status
    all_issues = (
        len(gov_result['issues']) +
        len(range_result['issues']) +
        len(temporal_result['issues']) +
        len(logical_result['issues']) +
        len(ref_result['issues'])
    )
    
    all_warnings = (
        len(range_result['warnings']) +
        len(temporal_result['warnings']) +
        len(logical_result['warnings']) +
        len(ref_result['warnings'])
    )
    
    print(f"Total Issues Found: {all_issues}")
    print(f"Total Warnings: {all_warnings}")
    
    if all_issues == 0:
        print("\n✅ OVERALL STATUS: DATA APPEARS ACCURATE AND RELIABLE")
        print("   All critical checks passed. Data is suitable for analysis.")
    elif all_issues < 5:
        print("\n⚠️  OVERALL STATUS: DATA MOSTLY ACCURATE WITH MINOR ISSUES")
        print("   Some issues detected but data is generally reliable.")
    else:
        print("\n❌ OVERALL STATUS: DATA HAS SIGNIFICANT ISSUES")
        print("   Multiple issues detected. Review recommended before use.")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    if all_issues == 0 and all_warnings == 0:
        recommendations.append("✅ Data quality is excellent. No corrections needed.")
    else:
        if gov_result['issues']:
            recommendations.append("Review and standardize governorate names")
        if range_result['issues']:
            recommendations.append("Review data ranges and correct out-of-range values")
        if temporal_result['issues']:
            recommendations.append("Verify and correct temporal inconsistencies")
        if logical_result['warnings']:
            recommendations.append("Review cases with unexpected patterns (e.g., negative improvements)")
        if ref_result['issues']:
            recommendations.append("Standardize reference citations")
    
    if not recommendations:
        recommendations.append("Data appears ready for use. Monitor for any anomalies during analysis.")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 80)
    return {
        'governorates': gov_result,
        'ranges': range_result,
        'temporal': temporal_result,
        'logical': logical_result,
        'references': ref_result,
        'total_issues': all_issues,
        'total_warnings': all_warnings
    }

if __name__ == "__main__":
    print("Loading data...")
    df = pd.read_csv('expanded_syria_bi_data.csv')
    
    print("Running verification checks...\n")
    results = generate_verification_report(df)
    
    # Save detailed report
    with open('data_verification_report.txt', 'w', encoding='utf-8') as f:
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        generate_verification_report(df)
        report_text = sys.stdout.getvalue()
        sys.stdout = old_stdout
        f.write(report_text)
    
    print("\n✅ Verification complete. Report saved to 'data_verification_report.txt'")

