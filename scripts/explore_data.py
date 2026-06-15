from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data/raw/olist"

def print_section(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def get_csv_files() -> list[Path]:
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}. "
            "Please make sure the Olist dataset is placed correctly."
        )
    
    return csv_files

def show_basic_info(file_path: Path, df: pd.DataFrame) -> None:
    print_section(f"FILE: {file_path.name}")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\nColumn names:")
    for col in df.columns:
        print(f"- {col}")

def show_data_types(df: pd.DataFrame) -> None:
    print("\nData types:")
    print(df.dtypes)

def show_missing_values(df: pd.DataFrame) -> None:
    print("\nMissing values:")

    missing = (
        df.isna()
        .sum()
        .reset_index()
        .rename(columns={"index": "column", 0: "missing_count"})
    )
    missing["missing_percent"] = (
        missing["missing_count"] / len(df) * 100
    ).round(2)

    missing = missing[missing["missing_count"] > 0]

    if missing.empty:
        print("No missing value.")
    else:
        print(missing.to_string(index=False))

def show_duplicate_rows(df: pd.DataFrame) -> None:
    duplicate_count = df.duplicated().sum()
    print(f"\nDuplicate full rows: {duplicate_count:,}")

def show_unique_counts(df: pd.DataFrame) -> None:
    print("\nUnique values per column:")

    unique_counts = []

    for col in df.columns:
        unique_counts.append(
            {
                "column": col,
                "unique_count": df[col].nunique(dropna=True),
                "total_rows": len(df),
            }
        )
    
    result = pd.DataFrame(unique_counts)
    print(result.to_string(index=False))

def show_possible_key_columns(df: pd.DataFrame) -> None:
    print("\nPossible key columns:")

    possible_keys = []

    for col in df.columns:
        non_null_count = df[col].notna().sum()
        unique_count = df[col].nunique(dropna=True)

        if non_null_count == len(df) and unique_count == len(df):
            possible_keys.append(col)
    
    if possible_keys:
        for col in possible_keys:
            print(f"- {col}")
    else:
        print("No single-column unique key found.")

def show_sample_data(df: pd.DataFrame) -> None:
    print("\nSample data:")
    print(df.head(10).to_string(index=False))

def explore_file(file_path: Path) -> None:
    df = pd.read_csv(file_path)

    show_basic_info(file_path, df)
    show_data_types(df)
    show_missing_values(df)
    show_duplicate_rows(df)
    show_unique_counts(df)
    show_possible_key_columns(df)
    show_sample_data(df)

def main() -> None:
    csv_file = get_csv_files()

    print_section("OLIST RAW DATA EXPLORATION")
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print(f"Number of CSV files found: {len(csv_file)}")

    for file_path in csv_file:
        explore_file(file_path)

if __name__ == "__main__":
    main()
