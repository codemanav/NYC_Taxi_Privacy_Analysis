"""Write a 5-row sample and the column schema of one downloaded month.

Outputs:
    sample.csv  - first five trip records
    schema.csv  - column names and pandas dtypes

Usage:
    python inspect_schema.py [path/to/yellow_tripdata_YYYY-MM.parquet]
"""

import sys

import pandas as pd

DEFAULT_PATH = "yellow_taxi_data/yellow_tripdata_2025-01.parquet"


def main(path: str = DEFAULT_PATH) -> None:
    df = pd.read_parquet(path)
    df.head().to_csv("sample.csv", index=False)
    df.dtypes.to_frame("dtype").to_csv("schema.csv")
    print(f"Wrote sample.csv and schema.csv from {path} ({len(df):,} rows)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH)
