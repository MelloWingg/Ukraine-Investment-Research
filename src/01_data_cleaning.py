import pandas as pd

from pathlib import Path


# Шлях до вихідного CSV
file_path = Path("../Ukraine-Investment-Research/data/raw/stat_investments.csv")

df = pd.read_csv(file_path)

# 1. Відбираємо загальні обсяги капітальних інвестицій
investments = df[
    (df["Показник"] == "Обсяг капітальних інвестицій") &
    (df["Категорія розрізу"] == "Загалом") &
    (df["Розріз"].str.strip() == "Усього") &
    (df["Вид економічної діяльності"].str.strip() == "Усього") &
    (df["Витрати на придбання активів"] == "Загалом")
].copy()

# 2. Залишаємо потрібні колонки
year_columns = [str(year) for year in range(2015, 2026)]

investments = investments[
    ["Територіальний розріз"] + year_columns
]

# 3. Перетворюємо таблицю з широкого формату в довгий
investments = investments.melt(
    id_vars="Територіальний розріз",
    var_name="year",
    value_name="investment_thousand_uah"
)

# 4. Перейменовуємо колонки
investments = investments.rename(
    columns={"Територіальний розріз": "region"}
)

# 5. Перетворюємо типи даних
investments["year"] = investments["year"].astype(int)

investments["investment_thousand_uah"] = pd.to_numeric(
    investments["investment_thousand_uah"],
    errors="coerce"
)

# 6. Переводимо тисячі гривень у мільярди гривень
investments["investment_billion_uah"] = (
    investments["investment_thousand_uah"] / 1_000_000
)

# 7. Створюємо таблицю CPI та дефлятор до цін 2025 року
cpi_data = {
    "year": list(range(2015, 2026)),
    "cpi_pct": [
        48.7, 13.9, 14.4, 10.9, 7.9, 2.7,
        9.4, 20.2, 12.8, 6.5, 12.7
    ]
}

cpi = pd.DataFrame(cpi_data)

cpi["inflation_factor"] = 1 + cpi["cpi_pct"] / 100

cpi["deflator_to_2025"] = 1.0

for i in range(len(cpi) - 2, -1, -1):
    cpi.loc[i, "deflator_to_2025"] = (
        cpi.loc[i + 1, "deflator_to_2025"]
        * cpi.loc[i + 1, "inflation_factor"]
    )

# 8. Додаємо CPI та дефлятор до інвестицій і рахуємо реальні інвестиції
investments = investments.merge(
    cpi[["year", "cpi_pct", "deflator_to_2025"]],
    on="year",
    how="left",
    validate="many_to_one"
)

investments["investment_real_2025"] = (
    investments["investment_billion_uah"]
    * investments["deflator_to_2025"]
)

# 9. Відокремлюємо Україну від областей
national = investments[
    investments["region"] == "Україна"
].copy()

regional = investments[
    investments["region"] != "Україна"
].copy()


# 10. Рахуємо річну зміну інвестицій (номінальну та реальну)
national = national.sort_values("year")
regional = regional.sort_values(["region", "year"])

national["nominal_yoy_growth_pct"] = (
    national["investment_billion_uah"]
    .pct_change(fill_method=None) * 100
)

national["real_yoy_growth_pct"] = (
    national["investment_real_2025"]
    .pct_change(fill_method=None) * 100
)

regional["nominal_yoy_growth_pct"] = (
    regional.groupby("region")["investment_billion_uah"]
    .pct_change(fill_method=None) * 100
)

regional["real_yoy_growth_pct"] = (
    regional.groupby("region")["investment_real_2025"]
    .pct_change(fill_method=None) * 100
)

# Кількість унікальних регіонів
print("Unique regions:", regional["region"].nunique())

# Перевірка років
print("Years:", sorted(investments["year"].unique()))

# Перевірка пропущених значень
print("\nMissing values:")
print(investments.isna().sum())

# Перевірка дублікатів
print(
    "\nDuplicate region-year pairs:",
    investments.duplicated(["region", "year"]).sum()
)

# Перевірка регіонів
print("\nRegions:")
print(sorted(regional["region"].unique()))

# Перевірка екстремальних значень
print("\nNational investment statistics (real, 2025 prices):")
print(national["investment_real_2025"].describe())

# 11. Зберігаємо результати
Path("../Ukraine-Investment-Research/data/processed").mkdir(parents=True, exist_ok=True)

national.to_csv(
    "../Ukraine-Investment-Research/data/processed/investments_national.csv",
    index=False
)

regional.to_csv(
    "../Ukraine-Investment-Research/data/processed/investments_regional.csv",
    index=False
)

print("National dataset:", national.shape)
print("Regional dataset:", regional.shape)

print(national.head())
print(regional.head())