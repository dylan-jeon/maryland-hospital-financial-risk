"""
Maryland Hospital Financial Stress Early Warning System
=======================================================
Author: Dylan Jeon
Data: CMS Hospital Provider Cost Report 2023 (data.cms.gov)
Description: Scores all Maryland hospitals across five financial stress
indicators and produces a composite risk ranking for strategic monitoring.

Indicators:
    1. Operating Margin
    2. Days Cash on Hand
    3. Debt to Asset Ratio
    4. Labor Cost Percentage
    5. Uncompensated Care Percentage

Scoring: Each indicator scored 1 (healthy) to 5 (critical)
Composite Score: Sum of 5 indicator scores (range: 5-25)
Risk Labels: Low (5-10), Moderate (11-15), High (16-20), Critical (21-25)
"""

import pandas as pd
import numpy as np


# =============================================================================
# STEP 1 — LOAD AND FILTER DATA
# =============================================================================

def load_maryland_hospitals(filepath):
    """
    Load CMS Hospital Cost Report data and filter to Maryland hospitals
    with sufficient data coverage across all key financial fields.

    Args:
        filepath (str): Path to the CMS Hospital Provider Cost Report CSV

    Returns:
        pd.DataFrame: Filtered Maryland hospital dataset
    """
    df = pd.read_csv(filepath)

    # Filter to Maryland
    md = df[df['State Code'] == 'MD'].copy()

    # Keep only hospitals with minimum required fields
    required_fields = ['Net Patient Revenue', 'Total Costs', 'Total Assets']
    md = md.dropna(subset=required_fields).copy()
    md = md.reset_index(drop=True)

    print(f"Total hospitals in dataset: {len(df)}")
    print(f"Maryland hospitals after filtering: {len(md)}")

    return md


# =============================================================================
# STEP 2 — CALCULATE STRESS INDICATORS
# =============================================================================

def calculate_indicators(md):
    """
    Derive five financial stress indicators from raw CMS cost report fields.
    Thresholds are informed by HFMA benchmarking standards.

    Args:
        md (pd.DataFrame): Maryland hospital dataset

    Returns:
        pd.DataFrame: Dataset with calculated indicator columns
    """

    # 1. Operating Margin — measures profitability from patient care operations
    #    Formula: Net Income / Net Patient Revenue
    #    Threshold: < 2% is a watch signal; negative is a warning
    md['Operating_Margin'] = md['Net Income'] / md['Net Patient Revenue']

    # 2. Days Cash on Hand — measures short-term liquidity
    #    Formula: Cash on Hand / (Total Costs / 365)
    #    Threshold: < 30 days is a warning; < 15 days is critical
    md['Days_Cash'] = (
        md['Cash on Hand and in Banks'] / (md['Total Costs'] / 365)
    )

    # 3. Debt to Asset Ratio — measures leverage and financial flexibility
    #    Formula: Total Liabilities / Total Assets
    #    Threshold: > 65% limits refinancing options; > 80% is critical
    md['Debt_to_Asset'] = md['Total Liabilities'] / md['Total Assets']

    # 4. Labor Cost Percentage — measures operational cost efficiency
    #    Formula: Total Salaries / Total Costs
    #    Threshold: > 62% indicates cost pressure; > 70% is critical
    md['Labor_Pct'] = (
        md['Total Salaries From Worksheet A'] / md['Total Costs']
    )

    # 5. Uncompensated Care Percentage — measures charity care burden
    #    Formula: Cost of Uncompensated Care / Net Patient Revenue
    #    Note: Lower coverage in dataset (14 of 51 hospitals reported)
    md['Uncompensated_Pct'] = (
        md['Cost of Uncompensated Care'] / md['Net Patient Revenue']
    )

    return md


# =============================================================================
# STEP 3 — SCORING FUNCTIONS
# =============================================================================

def score_operating_margin(x):
    """Score operating margin 1 (healthy) to 5 (critical)."""
    if pd.isna(x): return 3       # missing data gets neutral score
    if x >= 0.05:  return 1       # healthy: above 5% margin
    if x >= 0.02:  return 2       # watch: 2-5% margin
    if x >= 0.00:  return 3       # warning: break even
    if x >= -0.05: return 4       # high risk: slightly negative
    return 5                      # critical: deeply negative


def score_days_cash(x):
    """Score days cash on hand 1 (healthy) to 5 (critical)."""
    if pd.isna(x): return 3
    if x >= 60:  return 1         # healthy: 60+ days
    if x >= 30:  return 2         # watch: 30-60 days
    if x >= 15:  return 3         # warning: 15-30 days
    if x >= 5:   return 4         # high risk: 5-15 days
    return 5                      # critical: under 5 days


def score_debt_to_asset(x):
    """Score debt to asset ratio 1 (healthy) to 5 (critical)."""
    if pd.isna(x): return 3
    if x <= 0.30: return 1        # healthy: low leverage
    if x <= 0.50: return 2        # watch
    if x <= 0.65: return 3        # warning
    if x <= 0.80: return 4        # high risk
    return 5                      # critical: liabilities exceed 80% of assets


def score_labor_pct(x):
    """Score labor cost percentage 1 (healthy) to 5 (critical)."""
    if pd.isna(x): return 3
    if x <= 0.45: return 1        # healthy: efficient staffing
    if x <= 0.55: return 2        # watch
    if x <= 0.62: return 3        # warning
    if x <= 0.70: return 4        # high risk
    return 5                      # critical: labor consuming 70%+ of costs


def score_uncompensated(x):
    """Score uncompensated care percentage 1 (healthy) to 5 (critical)."""
    if pd.isna(x): return 3
    if x <= 0.02: return 1        # healthy: low charity care burden
    if x <= 0.05: return 2        # watch
    if x <= 0.08: return 3        # warning
    if x <= 0.12: return 4        # high risk
    return 5                      # critical: high uncompensated care burden


def apply_scores(md):
    """
    Apply all five scoring functions and calculate composite stress score.

    Args:
        md (pd.DataFrame): Dataset with calculated indicator columns

    Returns:
        pd.DataFrame: Dataset with scores and risk labels
    """
    md['Score_Margin']        = md['Operating_Margin'].apply(score_operating_margin)
    md['Score_Days_Cash']     = md['Days_Cash'].apply(score_days_cash)
    md['Score_Debt']          = md['Debt_to_Asset'].apply(score_debt_to_asset)
    md['Score_Labor']         = md['Labor_Pct'].apply(score_labor_pct)
    md['Score_Uncompensated'] = md['Uncompensated_Pct'].apply(score_uncompensated)

    # Composite score: equally weighted sum of all 5 indicators (range 5-25)
    md['Composite_Score'] = (
        md['Score_Margin'] +
        md['Score_Days_Cash'] +
        md['Score_Debt'] +
        md['Score_Labor'] +
        md['Score_Uncompensated']
    )

    # Assign risk label based on composite score
    def risk_label(score):
        if score <= 10: return 'Low'
        if score <= 15: return 'Moderate'
        if score <= 20: return 'High'
        return 'Critical'

    md['Risk_Level'] = md['Composite_Score'].apply(risk_label)

    # Sort by most stressed first
    md = md.sort_values('Composite_Score', ascending=False).reset_index(drop=True)
    md['Rank'] = md.index + 1

    return md


# =============================================================================
# STEP 4 — EXPORT CLEAN CSV FOR TABLEAU
# =============================================================================

def export_tableau_csv(md, output_path):
    """
    Export clean, scored dataset as CSV for Tableau visualization.

    Args:
        md (pd.DataFrame): Fully scored hospital dataset
        output_path (str): Output file path
    """
    out = md[[
        'Hospital Name', 'City', 'Rank', 'Risk_Level', 'Composite_Score',
        'Operating_Margin', 'Days_Cash', 'Debt_to_Asset', 'Labor_Pct',
        'Uncompensated_Pct', 'Score_Margin', 'Score_Days_Cash',
        'Score_Debt', 'Score_Labor', 'Score_Uncompensated',
        'Net Income', 'Net Patient Revenue', 'Total Costs',
        'Total Assets', 'Total Liabilities', 'Cash on Hand and in Banks',
        'Total Salaries From Worksheet A'
    ]].copy()

    out.columns = [
        'Hospital Name', 'City', 'Rank', 'Risk Level', 'Composite Score',
        'Operating Margin', 'Days Cash on Hand', 'Debt to Asset Ratio',
        'Labor Cost Pct', 'Uncompensated Care Pct',
        'Score - Margin', 'Score - Days Cash', 'Score - Debt',
        'Score - Labor', 'Score - Uncompensated',
        'Net Income', 'Net Patient Revenue', 'Total Costs',
        'Total Assets', 'Total Liabilities', 'Cash on Hand',
        'Total Salaries'
    ]

    out.to_csv(output_path, index=False)
    print(f"Exported {len(out)} hospitals to {output_path}")


# =============================================================================
# STEP 5 — SUMMARY STATISTICS
# =============================================================================

def print_summary(md):
    """Print key findings from the analysis."""
    print("\n=== MARYLAND HOSPITAL FINANCIAL STRESS SUMMARY ===")
    print(f"Total hospitals analyzed: {len(md)}")
    print(f"Critical risk:  {len(md[md['Risk_Level']=='Critical'])}")
    print(f"High risk:      {len(md[md['Risk_Level']=='High'])}")
    print(f"Moderate risk:  {len(md[md['Risk_Level']=='Moderate'])}")
    print(f"Low risk:       {len(md[md['Risk_Level']=='Low'])}")
    print(f"\nAverage composite score: {md['Composite_Score'].mean():.1f} / 25")
    print(f"Median operating margin: {md['Operating_Margin'].median():.1%}")
    print(f"Hospitals with negative margin: {len(md[md['Operating_Margin'] < 0])}")
    print(f"Hospitals with < 30 days cash: {len(md[md['Days_Cash'] < 30])}")
    print("\n=== TOP 5 MOST STRESSED HOSPITALS ===")
    top5 = md[['Hospital Name', 'City', 'Composite_Score', 'Risk_Level']].head(5)
    for _, row in top5.iterrows():
        print(f"  {row['Hospital Name'].title()} ({row['City'].title()}): "
              f"Score={int(row['Composite_Score'])}, Risk={row['Risk_Level']}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # File paths — update if needed
    INPUT_FILE  = 'Hospital_Provider_Cost_Report_2023.csv'
    OUTPUT_FILE = 'MD_Hospital_Stress_Tableau.csv'

    # Run pipeline
    md = load_maryland_hospitals(INPUT_FILE)
    md = calculate_indicators(md)
    md = apply_scores(md)
    export_tableau_csv(md, OUTPUT_FILE)
    print_summary(md)
