
import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "stat_regional_accounts.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grp_regional.csv"

# Load raw data
df = pd.read_csv(RAW_PATH)

# Select total GRP
grp = df[
    (df["Показник"] == "Валовий регіональний продукт") &
    (df["Вид економічної діяльності"] == "Не застосовується") &
    (df["Періодичність"] == "Річна")
].copy()

# Keep regional observations only
grp = grp[
    ~grp["Територіальний розріз"].isin([
        "Україна",
        "Автономна Республіка Крим",
        "Севастополь"
    ])
].copy()

# Rename territory column
grp = grp.rename(columns={
    "Територіальний розріз": "region"
})

# Select year columns
year_columns = [
    col for col in grp.columns
    if str(col).isdigit()
]

# Convert wide format to long format
grp_long = grp.melt(
    id_vars=["region"],
    value_vars=year_columns,
    var_name="year",
    value_name="grp_million_uah"
)

# Data types
grp_long["year"] = grp_long["year"].astype(int)
grp_long["grp_million_uah"] = pd.to_numeric(
    grp_long["grp_million_uah"],
    errors="coerce"
)

# Remove rows without GRP values
grp_long = grp_long.dropna(subset=["grp_million_uah"])

# Sort
grp_long = grp_long.sort_values(
    ["region", "year"]
).reset_index(drop=True)

# Validation
assert not grp_long.duplicated(["region", "year"]).any()

print("GRP dataset shape:", grp_long.shape)
print("Unique regions:", grp_long["region"].nunique())
print("Years:", sorted(grp_long["year"].unique()))

print("\n2021 Ukraine GRP:")
print(
    df.loc[
        (df["Показник"] == "Валовий регіональний продукт") &
        (df["Територіальний розріз"] == "Україна"),
        "2021"
    ].iloc[0]
)

print("\n2021 regional GRP total:")
print(
    grp_long.loc[
        grp_long["year"] == 2021,
        "grp_million_uah"
    ].sum()
)

# Save
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
grp_long.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"\nSaved to: {OUTPUT_PATH}")
