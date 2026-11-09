import pandas as pd
import numpy as np
import os
import json

# Find all parquet files
data_dir = 'yellow_taxi_data'
parquet_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.parquet')])

print("="*80)
print(f"BATCH K-ANONYMITY ANALYSIS - {len(parquet_files)} FILES")
print("="*80)

# Function to calculate k-anonymity
def calculate_k_anonymity(df, quasi_identifiers):
    group_sizes = df.groupby(quasi_identifiers, observed=True).size()
    k_value = group_sizes.min()
    avg_group_size = group_sizes.mean()
    unique_groups = len(group_sizes)
    violations = (group_sizes < 5).sum()
    violation_pct = (violations / len(group_sizes)) * 100
    unique_k1 = (group_sizes == 1).sum()
    unique_k1_pct = (unique_k1 / len(group_sizes)) * 100

    return {
        'k': int(k_value),
        'avg_group_size': float(avg_group_size),
        'unique_groups': int(unique_groups),
        'groups_k<5': int(violations),
        'violation_pct': float(violation_pct),
        'unique_k1': int(unique_k1),
        'unique_k1_pct': float(unique_k1_pct)
    }

# Store all results
all_results = []

for filename in parquet_files:
    filepath = os.path.join(data_dir, filename)
    year_month = filename.replace('yellow_tripdata_', '').replace('.parquet', '')

    print(f"\n{'='*80}")
    print(f"Processing: {year_month}")
    print(f"{'='*80}")

    try:
        df = pd.read_parquet(filepath)

        # Add derived columns
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        df['distance_bin'] = pd.cut(df['trip_distance'],
                                     bins=[0, 1, 3, 5, 10, 100],
                                     labels=['0-1mi', '1-3mi', '3-5mi', '5-10mi', '10+mi'])

        result = {'year_month': year_month, 'total_records': len(df)}

        # Scenario 1: Location only
        print("  Scenario 1: Location-based...")
        qi_1 = ['PULocationID', 'DOLocationID']
        res_1 = calculate_k_anonymity(df, qi_1)
        result.update({f'loc_{k}': v for k, v in res_1.items()})

        # Scenario 2: Location + Time
        print("  Scenario 2: Location + Time...")
        qi_2 = ['PULocationID', 'DOLocationID', 'pickup_hour']
        res_2 = calculate_k_anonymity(df, qi_2)
        result.update({f'loc_time_{k}': v for k, v in res_2.items()})

        # Scenario 3: Location + Time + Distance
        print("  Scenario 3: Location + Time + Distance...")
        qi_3 = ['PULocationID', 'DOLocationID', 'pickup_hour', 'distance_bin']
        df_clean = df[df['distance_bin'].notna()]
        res_3 = calculate_k_anonymity(df_clean, qi_3)
        result.update({f'loc_time_dist_{k}': v for k, v in res_3.items()})

        # Scenario 4: Location + Time + Passenger
        print("  Scenario 4: Location + Time + Passenger...")
        if 'passenger_count' in df.columns:
            qi_4 = ['PULocationID', 'DOLocationID', 'pickup_hour', 'passenger_count']
            df_clean = df[df['passenger_count'].notna()]
            res_4 = calculate_k_anonymity(df_clean, qi_4)
            result.update({f'loc_time_pass_{k}': v for k, v in res_4.items()})

        all_results.append(result)

        # Print summary
        print(f"  Results:")
        print(f"    Location: k={res_1['k']}, unique_k1={res_1['unique_k1_pct']:.2f}%")
        print(f"    Loc+Time: k={res_2['k']}, unique_k1={res_2['unique_k1_pct']:.2f}%")
        print(f"    Loc+Time+Dist: k={res_3['k']}, unique_k1={res_3['unique_k1_pct']:.2f}%")

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        continue

# Save results
results_df = pd.DataFrame(all_results)
results_df.to_csv('k_anonymity_summary_all_months.csv', index=False)

print("\n" + "="*80)
print("K-ANONYMITY SUMMARY - ALL MONTHS")
print("="*80)

# Display key metrics
display_cols = ['year_month', 'total_records',
                'loc_k', 'loc_unique_k1_pct', 'loc_violation_pct',
                'loc_time_k', 'loc_time_unique_k1_pct', 'loc_time_violation_pct']

if all(col in results_df.columns for col in display_cols):
    print(results_df[display_cols].to_string(index=False))

print("\n" + "="*80)
print("AGGREGATE STATISTICS")
print("="*80)

# Calculate averages
print("\nAverage k-values across all months:")
print(f"  Location only: {results_df['loc_k'].mean():.2f}")
print(f"  Location + Time: {results_df['loc_time_k'].mean():.2f}")
print(f"  Location + Time + Distance: {results_df['loc_time_dist_k'].mean():.2f}")

print("\nAverage unique groups (k=1) percentage:")
print(f"  Location only: {results_df['loc_unique_k1_pct'].mean():.2f}%")
print(f"  Location + Time: {results_df['loc_time_unique_k1_pct'].mean():.2f}%")
print(f"  Location + Time + Distance: {results_df['loc_time_dist_unique_k1_pct'].mean():.2f}%")

print("\nAverage violation (k<5) percentage:")
print(f"  Location only: {results_df['loc_violation_pct'].mean():.2f}%")
print(f"  Location + Time: {results_df['loc_time_violation_pct'].mean():.2f}%")
print(f"  Location + Time + Distance: {results_df['loc_time_dist_violation_pct'].mean():.2f}%")

print("\n" + "="*80)
print("Results saved to: k_anonymity_summary_all_months.csv")
print("="*80)
