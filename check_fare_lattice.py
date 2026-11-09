"""Quick sanity check for fare_lattice.py before running the full lattice.

Loads and cleans one month, prints the engineered features, and trains the
baseline model (exact hour, exact pickup zone) once.

Usage:
    python check_fare_lattice.py
"""

from fare_lattice import (
    generalize_location,
    generalize_time,
    load_and_clean,
    train_and_evaluate,
)


def main() -> None:
    df = load_and_clean()
    print("Cleaned shape:", df.shape)
    print(df[["fare_amount", "trip_distance", "pickup_hour", "PULocationID"]].head())

    df = generalize_time(df, level=0)
    df = generalize_location(df, level=0)

    mae, rmse, r2 = train_and_evaluate(df)
    print(f"Baseline (time=0, loc=0): MAE={mae:.3f} RMSE={rmse:.3f} R2={r2:.3f}")


if __name__ == "__main__":
    main()
