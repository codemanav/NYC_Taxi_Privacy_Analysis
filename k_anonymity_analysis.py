import pandas as pd
import numpy as np
from datetime import datetime

# Load data
df = pd.read_parquet('yellow_tripdata_2025-01.parquet')

print("="*80)
print("K-ANONYMITY ANALYSIS - NYC TAXI DATA")
print("="*80)

# Create time bins for anonymization
df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
df['pickup_date'] = df['tpep_pickup_datetime'].dt.date

# Create distance bins
df['distance_bin'] = pd.cut(df['trip_distance'],
                             bins=[0, 1, 3, 5, 10, 100],
                             labels=['0-1mi', '1-3mi', '3-5mi', '5-10mi', '10+mi'])

# Function to calculate k-anonymity
def calculate_k_anonymity(df, quasi_identifiers):
    group_sizes = df.groupby(quasi_identifiers).size()
    k_value = group_sizes.min()
    avg_group_size = group_sizes.mean()
    unique_groups = len(group_sizes)

    violations = (group_sizes < 5).sum()
    violation_pct = (violations / len(group_sizes)) * 100

    return {
        'k': k_value,
        'avg_group_size': avg_group_size,
        'unique_groups': unique_groups,
        'groups_k<5': violations,
        'violation_pct': violation_pct,
        'group_size_distribution': group_sizes.describe()
    }

# Scenario 1: Location-based quasi-identifiers
print("\n1. SCENARIO: LOCATION-BASED IDENTIFICATION")
print("Quasi-identifiers: [PULocationID, DOLocationID]")
print("-" * 80)
qi_1 = ['PULocationID', 'DOLocationID']
results_1 = calculate_k_anonymity(df, qi_1)
print(f"k-anonymity: {results_1['k']}")
print(f"Average group size: {results_1['avg_group_size']:.2f}")
print(f"Unique groups: {results_1['unique_groups']:,}")
print(f"Groups with k<5: {results_1['groups_k<5']:,} ({results_1['violation_pct']:.2f}%)")
print("\nGroup size distribution:")
print(results_1['group_size_distribution'])

# Scenario 2: Location + Time
print("\n2. SCENARIO: LOCATION + TIME IDENTIFICATION")
print("Quasi-identifiers: [PULocationID, DOLocationID, pickup_hour]")
print("-" * 80)
qi_2 = ['PULocationID', 'DOLocationID', 'pickup_hour']
results_2 = calculate_k_anonymity(df, qi_2)
print(f"k-anonymity: {results_2['k']}")
print(f"Average group size: {results_2['avg_group_size']:.2f}")
print(f"Unique groups: {results_2['unique_groups']:,}")
print(f"Groups with k<5: {results_2['groups_k<5']:,} ({results_2['violation_pct']:.2f}%)")
print("\nGroup size distribution:")
print(results_2['group_size_distribution'])

# Scenario 3: Location + Time + Distance
print("\n3. SCENARIO: LOCATION + TIME + DISTANCE IDENTIFICATION")
print("Quasi-identifiers: [PULocationID, DOLocationID, pickup_hour, distance_bin]")
print("-" * 80)
qi_3 = ['PULocationID', 'DOLocationID', 'pickup_hour', 'distance_bin']
results_3 = calculate_k_anonymity(df[df['distance_bin'].notna()], qi_3)
print(f"k-anonymity: {results_3['k']}")
print(f"Average group size: {results_3['avg_group_size']:.2f}")
print(f"Unique groups: {results_3['unique_groups']:,}")
print(f"Groups with k<5: {results_3['groups_k<5']:,} ({results_3['violation_pct']:.2f}%)")
print("\nGroup size distribution:")
print(results_3['group_size_distribution'])

# Scenario 4: Location + Time + Passenger Count
print("\n4. SCENARIO: LOCATION + TIME + PASSENGER COUNT")
print("Quasi-identifiers: [PULocationID, DOLocationID, pickup_hour, passenger_count]")
print("-" * 80)
qi_4 = ['PULocationID', 'DOLocationID', 'pickup_hour', 'passenger_count']
results_4 = calculate_k_anonymity(df[df['passenger_count'].notna()], qi_4)
print(f"k-anonymity: {results_4['k']}")
print(f"Average group size: {results_4['avg_group_size']:.2f}")
print(f"Unique groups: {results_4['unique_groups']:,}")
print(f"Groups with k<5: {results_4['groups_k<5']:,} ({results_4['violation_pct']:.2f}%)")
print("\nGroup size distribution:")
print(results_4['group_size_distribution'])

# Scenario 5: Temporal only (pickup date + hour)
print("\n5. SCENARIO: TEMPORAL IDENTIFICATION")
print("Quasi-identifiers: [pickup_date, pickup_hour, PULocationID]")
print("-" * 80)
qi_5 = ['pickup_date', 'pickup_hour', 'PULocationID']
results_5 = calculate_k_anonymity(df, qi_5)
print(f"k-anonymity: {results_5['k']}")
print(f"Average group size: {results_5['avg_group_size']:.2f}")
print(f"Unique groups: {results_5['unique_groups']:,}")
print(f"Groups with k<5: {results_5['groups_k<5']:,} ({results_5['violation_pct']:.2f}%)")
print("\nGroup size distribution:")
print(results_5['group_size_distribution'])

# Find vulnerable records (k=1)
print("\n" + "="*80)
print("PRIVACY VULNERABILITY ANALYSIS")
print("="*80)

for i, (qi, name) in enumerate([
    (qi_1, "Location-based"),
    (qi_2, "Location + Time"),
    (qi_3, "Location + Time + Distance"),
    (qi_4, "Location + Time + Passenger"),
    (qi_5, "Temporal")
], 1):
    df_temp = df if i != 3 else df[df['distance_bin'].notna()]
    df_temp = df_temp if i != 4 else df_temp[df_temp['passenger_count'].notna()]

    group_sizes = df_temp.groupby(qi).size()
    unique_records = (group_sizes == 1).sum()
    unique_pct = (unique_records / len(group_sizes)) * 100

    print(f"\n{name}:")
    print(f"  Unique identifiable groups (k=1): {unique_records:,} ({unique_pct:.2f}%)")
    print(f"  Total records in unique groups: {group_sizes[group_sizes == 1].sum():,}")

# Summary comparison
print("\n" + "="*80)
print("SUMMARY COMPARISON")
print("="*80)
summary_data = {
    'Scenario': ['Location', 'Location+Time', 'Location+Time+Distance',
                 'Location+Time+Passenger', 'Temporal'],
    'k-value': [results_1['k'], results_2['k'], results_3['k'],
                results_4['k'], results_5['k']],
    'Avg Group Size': [f"{results_1['avg_group_size']:.2f}",
                       f"{results_2['avg_group_size']:.2f}",
                       f"{results_3['avg_group_size']:.2f}",
                       f"{results_4['avg_group_size']:.2f}",
                       f"{results_5['avg_group_size']:.2f}"],
    'Groups k<5 (%)': [f"{results_1['violation_pct']:.2f}",
                       f"{results_2['violation_pct']:.2f}",
                       f"{results_3['violation_pct']:.2f}",
                       f"{results_4['violation_pct']:.2f}",
                       f"{results_5['violation_pct']:.2f}"]
}
summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n" + "="*80)
print("KEY FINDINGS:")
print("- Lower k-values indicate higher re-identification risk")
print("- Groups with k<5 are considered vulnerable")
print("- More quasi-identifiers = lower k-anonymity = higher risk")
print("="*80)
