import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

RANDOM_STATE = 42


# ==============================
# 1. LOAD & BASIC PREPROCESSING
# ==============================

def load_and_clean(path: str = "yellow_taxi_data/yellow_tripdata_2025-01.parquet") -> pd.DataFrame:
    """
    Load one month of yellow taxi data and do light cleaning + feature engineering
    good enough for fare prediction + generalization later.
    """
    df = pd.read_parquet(path)

    # Drop rows with critical nulls
    df = df.dropna(
        subset=[
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "fare_amount",
            "trip_distance",
            "passenger_count",
            "PULocationID",
            "DOLocationID",
            "payment_type",
        ]
    )

    # Basic sanity filters (tune if needed)
    df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 300)]
    df = df[(df["trip_distance"] > 0) & (df["trip_distance"] < 100)]
    df = df[df["passenger_count"] > 0]

    # Trip duration in minutes
    trip_duration_min = (
        (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"])
        .dt.total_seconds() / 60.0
    )
    df = df[(trip_duration_min > 0) & (trip_duration_min < 300)]
    df["trip_duration_min"] = trip_duration_min

    # Time features
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_dayofweek"] = df["tpep_pickup_datetime"].dt.dayofweek  # 0=Mon..6=Sun
    df["is_weekend"] = df["pickup_dayofweek"].isin([5, 6]).astype(int)

    # Cast some columns to int explicitly (important for generalization & encoding)
    df["PULocationID"] = df["PULocationID"].astype(int)
    df["DOLocationID"] = df["DOLocationID"].astype(int)
    df["payment_type"] = df["payment_type"].astype(int)
    df["passenger_count"] = df["passenger_count"].astype(float)

    if len(df) > 300_000:
        df = df.sample(300_000, random_state=42).reset_index(drop=True)

    return df

# 2. GENERALIZATION FUNCTIONS (LATTICE)
def generalize_time(df: pd.DataFrame, level: int) -> pd.DataFrame:
    """
    Time generalization over pickup time.
    Level 0: exact pickup hour (0-23)
    Level 1: 3-hour bucket (0-7) # 3-hour buckets: 0-2 -> 0, 3-5 -> 1, ..., 21-23 -> 7
    Level 2: weekday vs weekend (0 = weekday, 1 = weekend)
    """
    df = df.copy()

    if level == 0:
        df["time_gen"] = df["pickup_hour"].astype(int)

    elif level == 1:
        df["time_gen"] = (df["pickup_hour"] // 3).astype(int)

    elif level == 2:
        df["time_gen"] = df["is_weekend"].astype(int)

    else:
        raise ValueError(f"Unsupported time generalization level: {level}")

    return df


def generalize_location(df: pd.DataFrame, level: int) -> pd.DataFrame:
    """
    Location generalization over PULocationID and DOLocationID.
    Level 0: exact zone ID
    Level 1: bucket by // 10  (coarser zones)
    Level 2: bucket by // 25  (very coarse zones)
    """
    df = df.copy()

    if level == 0:
        df["PU_gen"] = df["PULocationID"].astype(int)
        df["DO_gen"] = df["DOLocationID"].astype(int)

    elif level == 1:
        df["PU_gen"] = (df["PULocationID"] // 10).astype(int)
        df["DO_gen"] = (df["DOLocationID"] // 10).astype(int)

    elif level == 2:
        df["PU_gen"] = (df["PULocationID"] // 25).astype(int)
        df["DO_gen"] = (df["DOLocationID"] // 25).astype(int)

    else:
        raise ValueError(f"Unsupported location generalization level: {level}")

    return df

# 3. MODEL TRAINING / EVALUATION STEP

def make_feature_target(df: pd.DataFrame):
    """
    Build X, y from a (possibly generalized) DataFrame.
    Target = fare_amount.
    """
    y = df["fare_amount"].values

    # Numeric features
    feature_cols_numeric = [
        "trip_distance",
        "trip_duration_min",
        "passenger_count",
    ]

    # Categorical / generalized features
    feature_cols_categorical = [
        "time_gen",
        "PU_gen",
        "DO_gen",
        "payment_type",
    ]

    X = df[feature_cols_numeric + feature_cols_categorical].copy()

    numeric_transformer = "passthrough"

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, feature_cols_numeric),
            ("cat", categorical_transformer, feature_cols_categorical),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=None,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    pipe = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return X, y, pipe


def train_and_evaluate(df: pd.DataFrame):
    """
    Train the pipeline on a given DataFrame (with time_gen & PU_gen/DO_gen)
    and return MAE, RMSE, R^2.
    """
    X, y, pipe = make_feature_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    return mae, rmse, r2

# 4. RUN GENERALIZATION LATTICE
def run_lattice():
    df = load_and_clean()

    time_levels = [0, 1, 2]
    loc_levels = [0, 1, 2]

    results = []

    for t in time_levels:
        for l in loc_levels:
            df_gen = generalize_time(df, t)
            df_gen = generalize_location(df_gen, l)

            mae, rmse, r2 = train_and_evaluate(df_gen)

            print(
                f"[time_level={t}, loc_level={l}] -> "
                f"MAE={mae:.3f}, RMSE={rmse:.3f}, R2={r2:.3f}"
            )

            results.append(
                {
                    "time_level": t,
                    "loc_level": l,
                    "mae": mae,
                    "rmse": rmse,
                    "r2": r2,
                    "n_records": len(df_gen),
                }
            )

    results_df = pd.DataFrame(results)
    results_df.to_csv("fare_lattice_results.csv", index=False)
    print("\nSaved lattice results to fare_lattice_results.csv")
    print(results_df)


if __name__ == "__main__":
    run_lattice()
