import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_parquet('yellow_taxi_data/yellow_tripdata_2025-01.parquet')

print("="*80)
print("NYC YELLOW TAXI DATA - EXPLORATORY DATA ANALYSIS")
print("="*80)

# Basic info
print("\n1. DATASET OVERVIEW")
print(f"Total records: {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Missing values
print("\n2. MISSING VALUES")
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({'Count': missing, 'Percentage': missing_pct})
print(missing_df[missing_df['Count'] > 0])

# Data types
print("\n3. DATA TYPES")
print(df.dtypes)

# Statistical summary
print("\n4. STATISTICAL SUMMARY - NUMERIC COLUMNS")
print(df.describe())

# Temporal analysis
print("\n5. TEMPORAL PATTERNS")
df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
df['pickup_day'] = df['tpep_pickup_datetime'].dt.day_name()
df['pickup_date'] = df['tpep_pickup_datetime'].dt.date
print(f"Date range: {df['tpep_pickup_datetime'].min()} to {df['tpep_pickup_datetime'].max()}")
print("\nTrips by hour:")
print(df['pickup_hour'].value_counts().sort_index())

# Location analysis
print("\n6. LOCATION PATTERNS")
print(f"Unique pickup locations: {df['PULocationID'].nunique()}")
print(f"Unique dropoff locations: {df['DOLocationID'].nunique()}")
print("\nTop 10 pickup locations:")
print(df['PULocationID'].value_counts().head(10))
print("\nTop 10 dropoff locations:")
print(df['DOLocationID'].value_counts().head(10))

# Trip distance
print("\n7. TRIP DISTANCE ANALYSIS")
print(f"Mean distance: {df['trip_distance'].mean():.2f} miles")
print(f"Median distance: {df['trip_distance'].median():.2f} miles")
print(f"Max distance: {df['trip_distance'].max():.2f} miles")
print(f"Trips with 0 distance: {(df['trip_distance'] == 0).sum():,}")

# Payment analysis
print("\n8. PAYMENT PATTERNS")
print("Payment type distribution:")
print(df['payment_type'].value_counts())
print(f"\nMean tip amount: ${df['tip_amount'].mean():.2f}")
print(f"Median tip amount: ${df['tip_amount'].median():.2f}")
print(f"Mean fare: ${df['fare_amount'].mean():.2f}")
print(f"Mean total: ${df['total_amount'].mean():.2f}")

# Passenger count
print("\n9. PASSENGER COUNT")
print(df['passenger_count'].value_counts().sort_index())

# Rate code
print("\n10. RATE CODE DISTRIBUTION")
print(df['RatecodeID'].value_counts().sort_index())

# Vendor
print("\n11. VENDOR DISTRIBUTION")
print(df['VendorID'].value_counts())

# Create visualizations
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
fig.suptitle('NYC Yellow Taxi Data - EDA Visualizations', fontsize=16, y=1.0)

# Trips by hour
axes[0, 0].bar(df['pickup_hour'].value_counts().sort_index().index,
               df['pickup_hour'].value_counts().sort_index().values)
axes[0, 0].set_title('Trips by Hour of Day')
axes[0, 0].set_xlabel('Hour')
axes[0, 0].set_ylabel('Trip Count')

# Trip distance distribution
axes[0, 1].hist(df[df['trip_distance'] < 20]['trip_distance'], bins=50, edgecolor='black')
axes[0, 1].set_title('Trip Distance Distribution (<20 miles)')
axes[0, 1].set_xlabel('Distance (miles)')
axes[0, 1].set_ylabel('Frequency')

# Fare amount distribution
axes[0, 2].hist(df[df['fare_amount'] < 100]['fare_amount'], bins=50, edgecolor='black')
axes[0, 2].set_title('Fare Amount Distribution (<$100)')
axes[0, 2].set_xlabel('Fare ($)')
axes[0, 2].set_ylabel('Frequency')

# Tip amount distribution
axes[1, 0].hist(df[df['tip_amount'] < 20]['tip_amount'], bins=50, edgecolor='black')
axes[1, 0].set_title('Tip Amount Distribution (<$20)')
axes[1, 0].set_xlabel('Tip ($)')
axes[1, 0].set_ylabel('Frequency')

# Payment type
payment_counts = df['payment_type'].value_counts()
axes[1, 1].bar(payment_counts.index, payment_counts.values)
axes[1, 1].set_title('Payment Type Distribution')
axes[1, 1].set_xlabel('Payment Type')
axes[1, 1].set_ylabel('Count')

# Passenger count
passenger_counts = df['passenger_count'].value_counts().sort_index()
axes[1, 2].bar(passenger_counts.index, passenger_counts.values)
axes[1, 2].set_title('Passenger Count Distribution')
axes[1, 2].set_xlabel('Passengers')
axes[1, 2].set_ylabel('Count')

# Top pickup locations
top_pu = df['PULocationID'].value_counts().head(10)
axes[2, 0].barh(range(len(top_pu)), top_pu.values)
axes[2, 0].set_yticks(range(len(top_pu)))
axes[2, 0].set_yticklabels(top_pu.index)
axes[2, 0].set_title('Top 10 Pickup Locations')
axes[2, 0].set_xlabel('Trip Count')

# Top dropoff locations
top_do = df['DOLocationID'].value_counts().head(10)
axes[2, 1].barh(range(len(top_do)), top_do.values)
axes[2, 1].set_yticks(range(len(top_do)))
axes[2, 1].set_yticklabels(top_do.index)
axes[2, 1].set_title('Top 10 Dropoff Locations')
axes[2, 1].set_xlabel('Trip Count')

# Trips by day
daily_trips = df.groupby('pickup_date').size()
axes[2, 2].plot(daily_trips.index, daily_trips.values)
axes[2, 2].set_title('Daily Trip Volume')
axes[2, 2].set_xlabel('Date')
axes[2, 2].set_ylabel('Trip Count')
axes[2, 2].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('eda_yellow_tripdata.png', dpi=300, bbox_inches='tight')
print("\n" + "="*80)
print("Visualizations saved to: eda_yellow_tripdata.png")
print("="*80)
