import os
import requests
from datetime import datetime

# Create data directory
os.makedirs('yellow_taxi_data', exist_ok=True)

# Base URL
base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"

# Generate URLs for 2019-2025
urls_to_download = []

for year in range(2019, 2026):
    # For 2025, only download up to current month (or available data)
    max_month = 8 if year == 2025 else 12

    for month in range(1, max_month + 1):
        url = base_url.format(year=year, month=month)
        filename = f"yellow_taxi_data/yellow_tripdata_{year}-{month:02d}.parquet"
        urls_to_download.append((url, filename, year, month))

print(f"Total files to download: {len(urls_to_download)}")
print("=" * 80)

# Download files
downloaded = 0
skipped = 0
failed = 0

for url, filename, year, month in urls_to_download:
    # Skip if already exists
    if os.path.exists(filename):
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        print(f"SKIP: {year}-{month:02d} (already exists, {file_size:.1f} MB)")
        skipped += 1
        continue

    try:
        print(f"Downloading: {year}-{month:02d}...", end=" ", flush=True)
        response = requests.get(url, timeout=300)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            file_size = len(response.content) / (1024 * 1024)  # MB
            print(f"✓ ({file_size:.1f} MB)")
            downloaded += 1
        else:
            print(f"✗ (HTTP {response.status_code})")
            failed += 1
    except Exception as e:
        print(f"✗ ({str(e)})")
        failed += 1

print("=" * 80)
print(f"Summary: {downloaded} downloaded, {skipped} skipped, {failed} failed")
print("=" * 80)

# List all downloaded files
print("\nDownloaded files:")
files = sorted([f for f in os.listdir('yellow_taxi_data') if f.endswith('.parquet')])
total_size = 0
for f in files:
    size = os.path.getsize(f'yellow_taxi_data/{f}') / (1024 * 1024)
    total_size += size
    print(f"  {f}: {size:.1f} MB")

print(f"\nTotal size: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
