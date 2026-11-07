import pandas as pd
from pathlib import Path

# Шлях до Excel
file_path = Path(
    "../Ukraine-Investment-Research/data/raw/"
    "FINAL_2021_wjp_rule_of_law_index_HISTORICAL_DATA_FILE.xlsx"
)

# Відповідність аркушів і років
sheet_years = {
    "WJP ROL Index 2014 Scores": "2014",
    "WJP ROL Index 2015 Scores": "2015",
    "WJP ROL Index 2016 Scores": "2016",
    "WJP ROL Index 2017-2018 Scores": "2017-2018",
    "WJP ROL Index 2019 Scores": "2019",
    "WJP ROL Index 2020 Scores": "2020",
    "WJP ROL Index 2021 Scores": "2021"
}

results = []

for sheet, year in sheet_years.items():

    df = pd.read_excel(file_path, sheet_name=sheet, header=None)

    # Знаходимо колонку України
    country_row = df.iloc[0].astype(str).str.strip()

    ukraine_col = country_row[
        country_row == "Ukraine"
    ].index[0]

    # Знаходимо назви показників
    indicators = df.iloc[:, 0].astype(str).str.strip()

    # Загальний бал
    overall_row = indicators[
        indicators.str.contains(
            "Overall Score",
            case=False,
            na=False
        )
    ].index[0]

    overall_score = pd.to_numeric(
        df.iloc[overall_row, ukraine_col],
        errors="coerce"
    )

    # Основні фактори
    factor_scores = {}

    for factor in range(1, 9):

        factor_row = indicators[
            indicators.str.match(
                rf"Factor {factor}:",
                case=False,
                na=False
            )
        ].index[0]

        factor_scores[f"factor_{factor}"] = pd.to_numeric(
            df.iloc[factor_row, ukraine_col],
            errors="coerce"
        )

    # Збираємо результат
    record = {
        "year": year,
        "overall_score": overall_score,
        **factor_scores
    }

    results.append(record)


# Створюємо DataFrame
wjp = pd.DataFrame(results)

# Перевірка розміру
print("Shape:", wjp.shape)

# Перевірка пропусків
print("\nMissing values:")
print(wjp.isna().sum())

# Перевірка дублікатів років
print("\nDuplicate years:", wjp["year"].duplicated().sum())

# Перевірка діапазону оцінок
score_columns = [
    "overall_score",
    "factor_1", "factor_2", "factor_3", "factor_4",
    "factor_5", "factor_6", "factor_7", "factor_8"
]

print("\nScore range:")
print(wjp[score_columns].agg(["min", "max"]).round(3))

# Перевірка відсутніх значень та діапазону 0–1
assert wjp[score_columns].notna().all().all()
assert wjp[score_columns].ge(0).all().all()
assert wjp[score_columns].le(1).all().all()
assert wjp["year"].is_unique

# Зберігаємо
output_path = Path(
    "../Ukraine-Investment-Research/data/processed/wjp_ukraine.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

wjp.to_csv(output_path, index=False)

print(wjp.to_string(index=False))