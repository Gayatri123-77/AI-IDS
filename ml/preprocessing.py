
from pathlib import Path

import numpy as np
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

# Look for CSV files inside MachineLearningCSV
DATASET_DIR = DATA_DIR / "CICIDS2017" / "MachineLearningCSV"

# If your folder is directly inside data/raw, change the line above to:
# DATASET_DIR = DATA_DIR / "MachineLearningCSV"

LABEL_COLUMN = "Label"

# Metadata columns that should not be used as ML features
DROP_COLUMNS = [
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Timestamp",
]


def load_dataset():
    """Load and combine the CIC-IDS2017 CSV files."""

    csv_files = sorted(DATASET_DIR.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in: {DATASET_DIR}\n"
            "Check your dataset folder path."
        )

    print(f"Found {len(csv_files)} CSV file(s).")

    dataframes = []

    for file in csv_files:
        print(f"Loading: {file.name}")

        df = pd.read_csv(
            file,
            low_memory=False,
            encoding="utf-8-sig",
        )

        # Remove extra spaces from column names
        df.columns = df.columns.str.strip()

        # Standardize the target column name
        label_matches = [
            col for col in df.columns
            if col.casefold() == LABEL_COLUMN.casefold()
        ]

        if not label_matches:
            raise ValueError(
                f"Label column not found in {file.name}. "
                f"Available columns: {list(df.columns)}"
            )

        df = df.rename(
            columns={label_matches[0]: LABEL_COLUMN}
        )

        dataframes.append(df)

    data = pd.concat(
        dataframes,
        ignore_index=True,
        sort=False,
    )

    print(f"Combined dataset shape: {data.shape}")

    return data


def clean_dataset(data):
    """Clean the data and prepare features and labels."""

    # Remove spaces from labels
    data[LABEL_COLUMN] = (
        data[LABEL_COLUMN]
        .astype("string")
        .str.strip()
    )

    # Remove rows without a valid label
    data = data.dropna(subset=[LABEL_COLUMN]).copy()
    data = data[data[LABEL_COLUMN] != ""]

    # Remove duplicate records
    before = len(data)
    data = data.drop_duplicates().copy()

    print(f"Duplicate rows removed: {before - len(data)}")

    # Remove unwanted metadata columns if present
    columns_to_drop = [
        col for col in data.columns
        if col.casefold() in {
            name.casefold() for name in DROP_COLUMNS
        }
    ]

    data = data.drop(columns=columns_to_drop)

    # Separate target labels from input features
    y = data[LABEL_COLUMN].astype(str).str.strip()
    X = data.drop(columns=[LABEL_COLUMN]).copy()

    # Convert feature columns to numeric values
    for column in X.columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
        )

    # Replace infinite values with missing values
    X = X.replace([np.inf, -np.inf], np.nan)

    # Remove columns that contain no usable numeric values
    empty_columns = X.columns[X.isna().all()].tolist()

    if empty_columns:
        print(f"Removing empty columns: {empty_columns}")
        X = X.drop(columns=empty_columns)

    # Remove rows where all feature values are missing
    valid_rows = X.notna().any(axis=1)
    X = X.loc[valid_rows].copy()
    y = y.loc[valid_rows].copy()

    if X.empty:
        raise ValueError("No usable numeric feature rows remain.")

    # Basic imputation for an initial baseline
    # For rigorous evaluation, fit imputation on training data only.
    X = X.fillna(X.median())

    # Combine cleaned features and labels
    cleaned_data = X.copy()
    cleaned_data[LABEL_COLUMN] = y

    print(f"Final dataset shape: {cleaned_data.shape}")
    print(f"Feature count: {X.shape[1]}")
    print(f"Number of classes: {y.nunique()}")

    print("\nClass distribution:")
    print(y.value_counts())

    return cleaned_data


def save_dataset(data):
    """Save the cleaned dataset to data/processed."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "cicids2017_cleaned.csv"

    data.to_csv(output_file, index=False)

    print(f"\nCleaned dataset saved to:\n{output_file}")


def main():
    print("=== AI-IDS Data Preprocessing ===\n")

    raw_data = load_dataset()
    cleaned_data = clean_dataset(raw_data)
    save_dataset(cleaned_data)

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    main()
