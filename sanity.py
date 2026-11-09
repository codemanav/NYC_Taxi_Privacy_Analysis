from fare_lattice import load_and_clean, generalize_time, generalize_location, train_and_evaluate


df = load_and_clean()
print(df.shape)
print(df[["fare_amount", "trip_distance", "pickup_hour", "PULocationID"]].head())
print(df.shape)

df = load_and_clean()
df = generalize_time(df, level=0)
df = generalize_location(df, level=0)

mae, rmse, r2 = train_and_evaluate(df)
print("Baseline (time=0, loc=0):", mae, rmse, r2)
