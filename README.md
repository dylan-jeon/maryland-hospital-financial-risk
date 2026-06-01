# Maryland Hospital Financial Risk Dashboard

A financial stress early warning system for Maryland hospitals built using publicly available CMS Hospital Cost Report data.

## Project Overview

This project scores all 51 Maryland hospitals across five financial health indicators to identify institutions showing early signs of financial distress — before they become crises. The goal is to give finance and strategy teams a data-driven framework for proactive monitoring rather than reactive response.

**Key finding:** 27% of Maryland hospitals operated at negative margins in 2023, with liquidity (days cash on hand) emerging as the most acute system-wide risk indicator.

## Live Dashboard

[View on Tableau Public →](https://public.tableau.com/app/profile/dylan.jeon)

## Methodology

Each hospital is scored 1 (healthy) to 5 (critical) across five indicators:

| Indicator | Formula | Critical Threshold |
|---|---|---|
| Operating Margin | Net Income / Net Patient Revenue | < -5% |
| Days Cash on Hand | Cash / (Total Costs / 365) | < 5 days |
| Debt to Asset Ratio | Total Liabilities / Total Assets | > 80% |
| Labor Cost % | Total Salaries / Total Costs | > 70% |
| Uncompensated Care % | Uncomp. Care Cost / Net Patient Revenue | > 12% |

**Composite Score** = Sum of 5 indicator scores (range: 5–25)

**Risk Labels:**
- Low: 5–10
- Moderate: 11–15
- High: 16–20
- Critical: 21–25

Scoring thresholds are informed by HFMA (Healthcare Financial Management Association) benchmarking standards.

## Results

| Risk Level | Hospitals | % of Total |
|---|---|---|
| Critical | 1 | 2% |
| High | 10 | 20% |
| Moderate | 27 | 53% |
| Low | 13 | 25% |

**Most stressed hospital:** J Kent McNew Family Medical Center (Annapolis) — Composite Score: 21/25, with critical scores on Leverage, Liquidity, and Margin simultaneously.

## Repository Structure

```
maryland-hospital-financial-risk/
├── README.md
├── code/
│   └── hospital_stress_scoring.py    # Python scoring pipeline
├── data/
│   └── MD_Hospital_Stress_Tableau.csv  # Clean scored dataset for Tableau
└── output/
    ├── MD_Hospital_Stress_Dashboard.xlsx  # Excel dashboard (3 sheets)
    └── MD_Hospital_Stress_Memo.docx       # Executive memo
```

## How to Run

1. Download the CMS Hospital Provider Cost Report from [data.cms.gov](https://data.cms.gov/provider-compliance/cost-report/hospital-provider-cost-report)
2. Save as `Hospital_Provider_Cost_Report_2023.csv` in the project folder
3. Run the scoring pipeline:

```bash
pip install pandas numpy
python code/hospital_stress_scoring.py
```

4. Open `MD_Hospital_Stress_Tableau.csv` in Tableau Public to rebuild the dashboard

## Data Source

- **CMS Hospital Provider Cost Report 2023** — [data.cms.gov](https://data.cms.gov)
- Covers fiscal year 2023 financial data for 6,100+ U.S. hospitals
- Maryland subset: 51 hospitals with sufficient data coverage

## Tools Used

- **Python** (pandas, numpy) — data cleaning, indicator calculation, composite scoring
- **Excel** — financial model, KPI dashboard, scoring methodology documentation
- **Tableau Public** — interactive risk dashboard (bar chart, scatter plot, heatmap)
- **Microsoft Word** — executive memo for CFO-level audience

## Author

Dylan Jeon | [GitHub](https://github.com/dylan-jeon) | dylanjeon03@gmail.com
