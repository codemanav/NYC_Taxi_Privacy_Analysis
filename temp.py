import pandas as pd

df = pd.read_parquet("yellow_tripdata_2025-01.parquet")
df.head().to_csv("sample.csv", index=False)
df.dtypes.to_frame("dtype").to_csv("schema.csv")