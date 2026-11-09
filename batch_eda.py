import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime

# Find all parquet files
data_dir = 'yellow_taxi_data'
parquet_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.parquet')])

print("="*80)
print(f"BATCH EDA ANALYSIS - {len(parquet_files)} FILES")
print("="*80)

# Store summary results
all_results = []

for filename in parquet_files:
    filepath = os.path.join(data_dir, filename)
    year_month = filename.replace('yellow_tripdata_', '').replace('.parquet', '')

    print(f"\n{'='*80}")
    print(f"Processing: {year_month}")
    print(f"{'='*80}")

    try:
        df = pd.read_parquet(filepath)

        # Basic stats
        stats = {
            'year_month': year_month,
            'total_records': len(df),
            'total_columns': len(df.columns),
            'memory_mb': df.memory_usage(deep=True).sum() / (1024**2),
            'date_range_start': str(df['tpep_pickup_datetime'].min()),
            'date_range_end': str(df['tpep_pickup_datetime'].max()),
            'unique_pickup_locations': df['PULocationID'].nunique(),
            'unique_dropoff_locations': df['DOLocationID'].nunique(),
            'mean_trip_distance': float(df['trip_distance'].mean()),
            'median_trip_distance': float(df['trip_distance'].median()),
            'mean_fare': float(df['fare_amount'].mean()),
            'mean_tip': float(df['tip_amount'].mean()),
            'mean_total': float(df['total_amount'].mean()),
            'zero_distance_trips': int((df['trip_distance'] == 0).sum()),
            'payment_type_1_pct': float((df['payment_type'] == 1).sum() / len(df) * 100),
        }

        # Passenger count stats (handle missing values)
        if 'passenger_count' in df.columns:
            stats['missing_passenger_count'] = int(df['passenger_count'].isnull().sum())
            stats['single_passenger_pct'] = float((df['passenger_count'] == 1.0).sum() / len(df) * 100)

        # Peak hour
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        hourly_counts = df['pickup_hour'].value_counts()
        stats['peak_hour'] = int(hourly_counts.idxmax())
        stats['peak_hour_trips'] = int(hourly_counts.max())
        stats['low_hour'] = int(hourly_counts.idxmin())
        stats['low_hour_trips'] = int(hourly_counts.min())

        # Top pickup location
        top_pickup = df['PULocationID'].value_counts().head(1)
        stats['top_pickup_location'] = int(top_pickup.index[0])
        stats['top_pickup_count'] = int(top_pickup.values[0])

        all_results.append(stats)

        print(f"Records: {stats['total_records']:,}")
        print(f"Unique locations: PU={stats['unique_pickup_locations']}, DO={stats['unique_dropoff_locations']}")
        print(f"Mean fare: ${stats['mean_fare']:.2f}, Mean tip: ${stats['mean_tip']:.2f}")
        print(f"Peak hour: {stats['peak_hour']}:00 ({stats['peak_hour_trips']:,} trips)")

    except Exception as e:
        print(f"ERROR processing {year_month}: {str(e)}")
        continue

# Save summary results
summary_df = pd.DataFrame(all_results)
summary_df.to_csv('eda_summary_all_months.csv', index=False)

print("\n" + "="*80)
print("SUMMARY STATISTICS ACROSS ALL MONTHS")
print("="*80)
print(summary_df.to_string(index=False))

# Create summary visualizations
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('NYC Yellow Taxi Data - Trends Over Time (2019-2025)', fontsize=16)

# Total records over time
axes[0, 0].plot(summary_df['year_month'], summary_df['total_records'], marker='o')
axes[0, 0].set_title('Total Trips per Month')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Trip Count')
axes[0, 0].tick_params(axis='x', rotation=90)
axes[0, 0].grid(True, alpha=0.3)

# Mean fare over time
axes[0, 1].plot(summary_df['year_month'], summary_df['mean_fare'], marker='o', color='green')
axes[0, 1].set_title('Mean Fare Amount Over Time')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Fare ($)')
axes[0, 1].tick_params(axis='x', rotation=90)
axes[0, 1].grid(True, alpha=0.3)

# Mean tip over time
axes[0, 2].plot(summary_df['year_month'], summary_df['mean_tip'], marker='o', color='orange')
axes[0, 2].set_title('Mean Tip Amount Over Time')
axes[0, 2].set_xlabel('Month')
axes[0, 2].set_ylabel('Tip ($)')
axes[0, 2].tick_params(axis='x', rotation=90)
axes[0, 2].grid(True, alpha=0.3)

# Mean trip distance over time
axes[1, 0].plot(summary_df['year_month'], summary_df['mean_trip_distance'], marker='o', color='red')
axes[1, 0].set_title('Mean Trip Distance Over Time')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Distance (miles)')
axes[1, 0].tick_params(axis='x', rotation=90)
axes[1, 0].grid(True, alpha=0.3)

# Unique pickup locations over time
axes[1, 1].plot(summary_df['year_month'], summary_df['unique_pickup_locations'], marker='o', color='purple')
axes[1, 1].set_title('Unique Pickup Locations Over Time')
axes[1, 1].set_xlabel('Month')
axes[1, 1].set_ylabel('Count')
axes[1, 1].tick_params(axis='x', rotation=90)
axes[1, 1].grid(True, alpha=0.3)

# Peak hour trips over time
axes[1, 2].plot(summary_df['year_month'], summary_df['peak_hour_trips'], marker='o', color='brown')
axes[1, 2].set_title('Peak Hour Trip Volume Over Time')
axes[1, 2].set_xlabel('Month')
axes[1, 2].set_ylabel('Trips')
axes[1, 2].tick_params(axis='x', rotation=90)
axes[1, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('eda_trends_all_months.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved: eda_trends_all_months.png")
print("Summary CSV saved: eda_summary_all_months.csv")
print("="*80)

# ============================================================================
# NEW SECTION: Create 3x3 grid visualization using all_results summary data
# ============================================================================

print("\n" + "="*80)
print("CREATING 3x3 GRID VISUALIZATION FROM ALL_RESULTS")
print("="*80)

# Convert all_results to DataFrame for easier plotting
summary_df_viz = pd.DataFrame(all_results)

# Create 3x3 visualization grid
fig2, axes2 = plt.subplots(3, 3, figsize=(15, 12))
fig2.suptitle('NYC Yellow Taxi Data - Batch EDA Summary (All Months)', fontsize=16, y=1.0)

# Row 0, Col 0: Total Records by Month (bar chart)
axes2[0, 0].bar(range(len(summary_df_viz)), summary_df_viz['total_records'])
axes2[0, 0].set_title('Total Records by Month')
axes2[0, 0].set_xlabel('Month Index')
axes2[0, 0].set_ylabel('Trip Count')
axes2[0, 0].grid(True, alpha=0.3)

# Row 0, Col 1: Mean Trip Distance Distribution (histogram-style bar)
axes2[0, 1].bar(range(len(summary_df_viz)), summary_df_viz['mean_trip_distance'], color='orange')
axes2[0, 1].set_title('Mean Trip Distance by Month')
axes2[0, 1].set_xlabel('Month Index')
axes2[0, 1].set_ylabel('Distance (miles)')
axes2[0, 1].grid(True, alpha=0.3)

# Row 0, Col 2: Mean Fare Amount by Month
axes2[0, 2].bar(range(len(summary_df_viz)), summary_df_viz['mean_fare'], color='green')
axes2[0, 2].set_title('Mean Fare Amount by Month')
axes2[0, 2].set_xlabel('Month Index')
axes2[0, 2].set_ylabel('Fare ($)')
axes2[0, 2].grid(True, alpha=0.3)

# Row 1, Col 0: Mean Tip Amount by Month
axes2[1, 0].bar(range(len(summary_df_viz)), summary_df_viz['mean_tip'], color='purple')
axes2[1, 0].set_title('Mean Tip Amount by Month')
axes2[1, 0].set_xlabel('Month Index')
axes2[1, 0].set_ylabel('Tip ($)')
axes2[1, 0].grid(True, alpha=0.3)

# Row 1, Col 1: Payment Type 1 Percentage by Month
axes2[1, 1].bar(range(len(summary_df_viz)), summary_df_viz['payment_type_1_pct'], color='teal')
axes2[1, 1].set_title('Payment Type 1 % by Month')
axes2[1, 1].set_xlabel('Month Index')
axes2[1, 1].set_ylabel('Percentage (%)')
axes2[1, 1].grid(True, alpha=0.3)

# Row 1, Col 2: Single Passenger % by Month (if available)
if 'single_passenger_pct' in summary_df_viz.columns:
    axes2[1, 2].bar(range(len(summary_df_viz)), summary_df_viz['single_passenger_pct'], color='brown')
    axes2[1, 2].set_title('Single Passenger % by Month')
    axes2[1, 2].set_xlabel('Month Index')
    axes2[1, 2].set_ylabel('Percentage (%)')
    axes2[1, 2].grid(True, alpha=0.3)
else:
    axes2[1, 2].text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
    axes2[1, 2].set_title('Single Passenger % by Month')

# Row 2, Col 0: Unique Pickup Locations by Month
axes2[2, 0].barh(range(len(summary_df_viz)), summary_df_viz['unique_pickup_locations'], color='red')
axes2[2, 0].set_title('Unique Pickup Locations by Month')
axes2[2, 0].set_xlabel('Count')
axes2[2, 0].set_ylabel('Month Index')
axes2[2, 0].invert_yaxis()
axes2[2, 0].grid(True, alpha=0.3)

# Row 2, Col 1: Unique Dropoff Locations by Month
axes2[2, 1].barh(range(len(summary_df_viz)), summary_df_viz['unique_dropoff_locations'], color='navy')
axes2[2, 1].set_title('Unique Dropoff Locations by Month')
axes2[2, 1].set_xlabel('Count')
axes2[2, 1].set_ylabel('Month Index')
axes2[2, 1].invert_yaxis()
axes2[2, 1].grid(True, alpha=0.3)

# Row 2, Col 2: Peak Hour Trips by Month
axes2[2, 2].plot(summary_df_viz['year_month'], summary_df_viz['peak_hour_trips'], marker='o', color='darkgreen')
axes2[2, 2].set_title('Peak Hour Trip Volume by Month')
axes2[2, 2].set_xlabel('Month')
axes2[2, 2].set_ylabel('Trips')
axes2[2, 2].tick_params(axis='x', rotation=90)
axes2[2, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('eda_batch_all_results.png', dpi=300, bbox_inches='tight')
print("\n" + "="*80)
print("3x3 Grid Visualization saved to: eda_batch_all_results.png")
print("="*80)
