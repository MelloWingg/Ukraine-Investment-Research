
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INVESTMENTS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "investments_regional.csv"
)
GRP_PATH = (
    PROJECT_ROOT / "data" / "processed" / "grp_regional.csv"
)
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "regional_investment_grp_comparison_2021.csv"
)

# Load data
investments = pd.read_csv(INVESTMENTS_PATH)
grp = pd.read_csv(GRP_PATH)

# Select 2021 observations
investments_2021 = investments[
    investments["year"] == 2021
].copy()

grp_2021 = grp[
    grp["year"] == 2021
].copy()

# Normalize region names
investments_2021["region"] = (
    investments_2021["region"].str.strip()
)
grp_2021["region"] = grp_2021["region"].str.strip()

# Check regional coverage
investment_regions = set(investments_2021["region"])
grp_regions = set(grp_2021["region"])

print("Regions only in investments:")
print(sorted(investment_regions - grp_regions))

print("\nRegions only in GRP:")
print(sorted(grp_regions - investment_regions))

# Merge datasets
comparison = investments_2021[
    ["region", "investment_billion_uah"]
].merge(
    grp_2021[["region", "grp_million_uah"]],
    on="region",
    how="outer",
    indicator=True,
    validate="one_to_one"
)

# Check merge results
print("\nMerge status:")
print(comparison["_merge"].value_counts())

assert (comparison["_merge"] == "both").all(), (
    "Some regions were not matched between datasets."
)

comparison = comparison.drop(columns="_merge")

assert len(comparison) == 25
assert not comparison["region"].duplicated().any()

# Calculate regional shares
total_investment = comparison["investment_billion_uah"].sum()
total_grp = comparison["grp_million_uah"].sum()

comparison["investment_share_pct"] = (
    comparison["investment_billion_uah"] /
    total_investment * 100
)

comparison["grp_share_pct"] = (
    comparison["grp_million_uah"] /
    total_grp * 100
)

# Difference between shares, in percentage points
comparison["share_gap_pp"] = (
    comparison["investment_share_pct"] -
    comparison["grp_share_pct"]
)

# Sort by investment share
comparison = comparison.sort_values(
    "investment_share_pct",
    ascending=False
).reset_index(drop=True)

# Validation
print("\nTotal regional investments, billion UAH:")
print(total_investment)

print("\nTotal regional GRP, million UAH:")
print(total_grp)

print("\nSum of investment shares:")
print(comparison["investment_share_pct"].sum())

print("\nSum of GRP shares:")
print(comparison["grp_share_pct"].sum())

assert np.isclose(comparison["investment_share_pct"].sum(), 100)
assert np.isclose(comparison["grp_share_pct"].sum(), 100)

# Save
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
comparison.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nComparison table:")
print(comparison.round(2).to_string(index=False))

print(f"\nSaved to: {OUTPUT_PATH}")
