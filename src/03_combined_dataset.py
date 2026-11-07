import pandas as pd
from pathlib import Path

# Шляхи до очищених датасетів
data_path = Path("../Ukraine-Investment-Research/data/processed")

investments = pd.read_csv(
    data_path / "investments_national.csv"
)

wjp = pd.read_csv(
    data_path / "wjp_ukraine.csv"
)

# Відповідність випусків WJP рокам інвестицій
period_mapping = {
    "2015": [2015],
    "2016": [2016],
    "2017-2018": [2017, 2018],
    "2019": [2019],
    "2020": [2020],
    "2021": [2021]
}

# Готуємо інвестиційні дані для кожного випуску WJP
investment_records = []

for period, years in period_mapping.items():

    period_data = investments[
        investments["year"].isin(years)
    ]

# Перевіряємо наявність усіх очікуваних років
    assert len(period_data) == len(years), (
        f"Missing investment data for period {period}"
    )


    record = {
        "year": period,
        # Номінальні інвестиції
        "investment_billion_uah": (
            period_data["investment_billion_uah"].mean()
        ),
        # Реальні інвестиції в цінах 2025 року
        "investment_real_2025": (
            period_data["investment_real_2025"].mean()
        )
    }

    investment_records.append(record)

investment_periods = pd.DataFrame(investment_records)

# Об'єднуємо інвестиції з WJP
combined = wjp.merge(
    investment_periods,
    on="year",
    how="inner",
    validate="one_to_one"
)

# Визначаємо порядок колонок
combined = combined[
    [
        "year",
        "investment_billion_uah",
        "investment_real_2025",
        "overall_score",
        "factor_1",
        "factor_2",
        "factor_3",
        "factor_4",
        "factor_5",
        "factor_6",
        "factor_7",
        "factor_8"
    ]
]

# Перевірки
print("Dataset shape:", combined.shape)
print("\nMissing values:")
print(combined.isna().sum())

print("\nCombined dataset:")
print(combined.to_string(index=False))

# Зберігаємо
combined.to_csv(
    data_path / "combined_national.csv",
    index=False
)

print("Dataset shape:", combined.shape)
print("\nCombined dataset:")
print(combined.to_string(index=False))