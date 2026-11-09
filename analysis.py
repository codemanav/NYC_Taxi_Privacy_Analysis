import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Set up plotting
plt.style.use('default')
sns.set_palette("husl")

# Load and prepare data
print("=== LOADING NYC TAXI DATA ===")
df = pd.read_parquet('yellow_taxi_data/yellow_tripdata_2025-01.parquet')
print(f"Original dataset: {len(df):,} records")

# Sample for analysis (adjust as needed)
SAMPLE_SIZE = 50000
if len(df) > SAMPLE_SIZE:
    df = df.sample(n=SAMPLE_SIZE, random_state=42)
    print(f"Using sample: {len(df):,} records")

# Clean and engineer features
print("\n=== DATA PREPROCESSING ===")
df = df.dropna(subset=['tpep_pickup_datetime', 'fare_amount', 'tip_amount'])
df = df[(df['fare_amount'] > 0) & (df['trip_distance'] > 0) & (df['fare_amount'] < 200)]
df = df[df['tip_amount'] >= 0]  # Remove negative tips

# Feature engineering
df['pickup_hour'] = pd.to_datetime(df['tpep_pickup_datetime']).dt.hour
df['pickup_day'] = pd.to_datetime(df['tpep_pickup_datetime']).dt.dayofweek
df['tip_percentage'] = (df['tip_amount'] / df['fare_amount'] * 100).round(1)
df['fare_per_mile'] = (df['fare_amount'] / df['trip_distance']).round(2)
df['trip_duration'] = ((pd.to_datetime(df['tpep_dropoff_datetime']) - 
                       pd.to_datetime(df['tpep_pickup_datetime'])).dt.total_seconds() / 60).round(1)

# Remove outliers
df = df[df['trip_duration'] > 0]
df = df[df['trip_duration'] < 300]  # Remove trips > 5 hours
df = df[df['tip_percentage'] <= 50]  # Remove extreme tips

# Create behavioral patterns
df['is_generous_tipper'] = df['tip_percentage'] > 20
df['is_regular_schedule'] = df['pickup_hour'].isin([7,8,9,17,18,19])  # Commute hours
df['is_weekend'] = df['pickup_day'].isin([5,6])
df['is_cash_payment'] = df['payment_type'] == 2

print(f"Clean dataset: {len(df):,} records")
print(f"Date range: {df['tpep_pickup_datetime'].min()} to {df['tpep_pickup_datetime'].max()}")

# =============================================================================
# EXPLORATORY DATA ANALYSIS
# =============================================================================

def comprehensive_eda():
    """Comprehensive exploratory data analysis"""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE EXPLORATORY DATA ANALYSIS")
    print("="*60)
    
    # Basic statistics
    print("\n--- BASIC DATASET STATISTICS ---")
    print(f"Total records: {len(df):,}")
    print(f"Date range: {pd.to_datetime(df['tpep_pickup_datetime']).min().date()} to {pd.to_datetime(df['tpep_pickup_datetime']).max().date()}")
    print(f"Unique pickup locations: {df['PULocationID'].nunique():,}")
    print(f"Unique dropoff locations: {df['DOLocationID'].nunique():,}")
    print(f"Unique vendors: {df['VendorID'].nunique()}")
    
    # Trip patterns
    print("\n--- TRIP PATTERNS ---")
    print(f"Average trip distance: {df['trip_distance'].mean():.2f} miles")
    print(f"Average trip duration: {df['trip_duration'].mean():.1f} minutes")
    print(f"Average fare: ${df['fare_amount'].mean():.2f}")
    print(f"Average tip: ${df['tip_amount'].mean():.2f} ({df['tip_percentage'].mean():.1f}%)")
    
    # Payment patterns
    payment_dist = df['payment_type'].value_counts()
    print(f"\n--- PAYMENT PATTERNS ---")
    for payment_type, count in payment_dist.head().items():
        pct = count / len(df) * 100
        payment_name = {1: 'Credit card', 2: 'Cash', 3: 'No charge', 4: 'Dispute'}.get(payment_type, f'Type {payment_type}')
        print(f"{payment_name}: {count:,} ({pct:.1f}%)")
    
    # Temporal patterns
    print(f"\n--- TEMPORAL PATTERNS ---")
    hourly_trips = df.groupby('pickup_hour').size()
    peak_hour = hourly_trips.idxmax()
    print(f"Peak hour: {peak_hour}:00 with {hourly_trips[peak_hour]:,} trips")
    
    daily_trips = df.groupby('pickup_day').size()
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    print(f"Trips by day:")
    for day_num, count in daily_trips.items():
        print(f"  {days[day_num]}: {count:,}")
    
    # Location hotspots
    print(f"\n--- LOCATION HOTSPOTS ---")
    top_pickups = df['PULocationID'].value_counts().head()
    print(f"Top pickup locations:")
    for loc_id, count in top_pickups.items():
        pct = count / len(df) * 100
        print(f"  Location {loc_id}: {count:,} trips ({pct:.2f}%)")
    
    # Tipping behavior analysis
    print(f"\n--- TIPPING BEHAVIOR ---")
    tip_stats = df['tip_percentage'].describe()
    print(f"Tip percentage statistics:")
    for stat, value in tip_stats.items():
        print(f"  {stat.capitalize()}: {value:.2f}%")
    
    no_tip_pct = (df['tip_amount'] == 0).mean() * 100
    generous_tip_pct = (df['tip_percentage'] > 20).mean() * 100
    print(f"No tip trips: {no_tip_pct:.1f}%")
    print(f"Generous tippers (>20%): {generous_tip_pct:.1f}%")

def user_behavior_clustering():
    """Cluster users by behavioral patterns"""
    
    print("\n" + "="*60)
    print("USER BEHAVIOR CLUSTERING ANALYSIS")
    print("="*60)
    
    # Create user profiles
    user_profiles = df.groupby('PULocationID').agg({
        'tip_percentage': ['mean', 'std'],
        'pickup_hour': lambda x: x.mode().iloc[0] if len(x) > 0 else 12,
        'trip_distance': 'mean',
        'fare_amount': 'mean',
        'is_weekend': 'mean',
        'payment_type': lambda x: x.mode().iloc[0] if len(x) > 0 else 1,
        'tpep_pickup_datetime': 'count'
    }).round(2)
    
    # Flatten column names
    user_profiles.columns = ['avg_tip', 'tip_std', 'common_hour', 'avg_distance', 
                           'avg_fare', 'weekend_ratio', 'payment_mode', 'trip_count']
    
    # Filter for users with multiple trips
    user_profiles = user_profiles[user_profiles['trip_count'] >= 5]
    print(f"Users with 5+ trips: {len(user_profiles):,}")
    
    if len(user_profiles) < 10:
        print("Not enough regular users for clustering analysis")
        return
    
    # Prepare features for clustering
    features = ['avg_tip', 'common_hour', 'avg_distance', 'avg_fare', 'weekend_ratio']
    X = user_profiles[features].fillna(user_profiles[features].mean())
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-means clustering
    print(f"\n--- K-MEANS CLUSTERING ---")
    kmeans = KMeans(n_clusters=4, random_state=42)
    user_profiles['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze clusters
    for cluster_id in range(4):
        cluster_data = user_profiles[user_profiles['cluster'] == cluster_id]
        print(f"\nCluster {cluster_id} ({len(cluster_data)} users):")
        print(f"  Avg tip: {cluster_data['avg_tip'].mean():.1f}%")
        print(f"  Common hour: {cluster_data['common_hour'].mean():.0f}:00")
        print(f"  Avg distance: {cluster_data['avg_distance'].mean():.2f} miles")
        print(f"  Weekend ratio: {cluster_data['weekend_ratio'].mean():.2f}")
        print(f"  Avg trips: {cluster_data['trip_count'].mean():.1f}")
    
    # DBSCAN for outlier detection
    print(f"\n--- DBSCAN OUTLIER DETECTION ---")
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    outlier_labels = dbscan.fit_predict(X_scaled)
    
    outliers = user_profiles[outlier_labels == -1]
    print(f"Outlier users detected: {len(outliers)}")
    
    if len(outliers) > 0:
        print(f"Outlier characteristics:")
        print(f"  Extreme tippers: {len(outliers[outliers['avg_tip'] > 30])} users")
        print(f"  Night travelers: {len(outliers[(outliers['common_hour'] < 6) | (outliers['common_hour'] > 22)])} users")
        print(f"  High-value riders: {len(outliers[outliers['avg_fare'] > 50])} users")
    
    return user_profiles

def trip_pattern_analysis():
    """Analyze trip patterns and routes"""
    
    print("\n" + "="*60)
    print("TRIP PATTERN ANALYSIS")
    print("="*60)
    
    # Route analysis
    route_patterns = df.groupby(['PULocationID', 'DOLocationID']).size().sort_values(ascending=False)
    print(f"Total unique routes: {len(route_patterns):,}")
    print(f"Routes used only once: {(route_patterns == 1).sum():,} ({(route_patterns == 1).sum()/len(route_patterns)*100:.1f}%)")
    
    print(f"\nTop 10 most popular routes:")
    for (pickup, dropoff), count in route_patterns.head(10).items():
        pct = count / len(df) * 100
        print(f"  {pickup} → {dropoff}: {count:,} trips ({pct:.2f}%)")
    
    # Distance vs fare analysis
    print(f"\n--- DISTANCE VS FARE ANALYSIS ---")
    correlation = df['trip_distance'].corr(df['fare_amount'])
    print(f"Distance-fare correlation: {correlation:.3f}")
    
    # Identify potential route-based privacy risks
    user_route_diversity = df.groupby('PULocationID')['DOLocationID'].nunique()
    low_diversity = user_route_diversity[user_route_diversity <= 2]
    print(f"\nUsers with ≤2 destinations: {len(low_diversity):,} ({len(low_diversity)/len(user_route_diversity)*100:.1f}%)")
    
    # Temporal clustering
    print(f"\n--- TEMPORAL CLUSTERING ---")
    hour_clusters = df.groupby('pickup_hour').size()
    morning_rush = hour_clusters[7:10].sum()
    evening_rush = hour_clusters[17:20].sum()
    late_night = hour_clusters[22:24].sum() + hour_clusters[0:6].sum()
    
    print(f"Morning rush (7-9 AM): {morning_rush:,} trips ({morning_rush/len(df)*100:.1f}%)")
    print(f"Evening rush (5-7 PM): {evening_rush:,} trips ({evening_rush/len(df)*100:.1f}%)")
    print(f"Late night (10 PM-6 AM): {late_night:,} trips ({late_night/len(df)*100:.1f}%)")

# =============================================================================
# SENSITIVE ATTRIBUTE ANALYSIS
# =============================================================================

def analyze_sensitive_attributes():
    """Analyze distribution and uniqueness of potential sensitive attributes"""
    
    print("\n" + "="*60)
    print("SENSITIVE ATTRIBUTE ANALYSIS")
    print("="*60)
    
    sensitive_attrs = {
        'tip_percentage': 'Tip Percentage (%)',
        'DOLocationID': 'Dropoff Location', 
        'total_amount': 'Total Fare Amount ($)',
        'payment_type': 'Payment Method',
        'trip_distance': 'Trip Distance (miles)',
        'pickup_hour': 'Pickup Hour',
        'passenger_count': 'Passenger Count'
    }
    
    for attr, desc in sensitive_attrs.items():
        if attr in df.columns:
            unique_vals = df[attr].nunique()
            total_records = len(df)
            uniqueness = unique_vals / total_records
            
            print(f"\n{desc}:")
            print(f"  Unique values: {unique_vals:,}")
            print(f"  Uniqueness ratio: {uniqueness:.4f}")
            print(f"  Most common: {df[attr].mode().iloc[0]} ({df[attr].value_counts().iloc[0]:,} times)")
            
            if df[attr].dtype in ['int64', 'float64']:
                print(f"  Range: {df[attr].min():.2f} - {df[attr].max():.2f}")
                print(f"  Mean: {df[attr].mean():.2f} ± {df[attr].std():.2f}")

# =============================================================================
# PRIVACY METRICS IMPLEMENTATION
# =============================================================================

def k_anonymity_analysis(df, quasi_identifiers, k_values=[2, 5, 10]):
    """Comprehensive k-anonymity analysis"""
    
    print(f"\n{'='*60}")
    print("K-ANONYMITY ANALYSIS")
    print("="*60)
    print(f"Quasi-identifiers: {quasi_identifiers}")
    
    # Group by quasi-identifiers
    groups = df.groupby(quasi_identifiers).size()
    
    results = {}
    for k in k_values:
        protected_groups = groups[groups >= k]
        protected_records = protected_groups.sum()
        protection_rate = protected_records / len(df) * 100
        
        results[k] = {
            'protected_records': protected_records,
            'protection_rate': protection_rate,
            'vulnerable_groups': len(groups[groups < k])
        }
        
        print(f"\nK-anonymity (k={k}):")
        print(f"  Protected records: {protected_records:,}/{len(df):,} ({protection_rate:.1f}%)")
        print(f"  Vulnerable groups: {len(groups[groups < k]):,}")
        print(f"  Largest group: {groups.max():,} records")
    
    # Show most vulnerable combinations
    vulnerable = groups[groups == 1].head(10)
    if len(vulnerable) > 0:
        print(f"\nMost vulnerable combinations (unique records): {len(groups[groups == 1])}")
    
    return results, groups

def l_diversity_analysis(df, quasi_identifiers, sensitive_attr, l_values=[2, 3, 5]):
    """L-diversity analysis"""
    
    print(f"\n{'='*60}")
    print("L-DIVERSITY ANALYSIS")
    print("="*60)
    print(f"Sensitive attribute: {sensitive_attr}")
    
    groups = df.groupby(quasi_identifiers)
    results = {}
    
    for l in l_values:
        diverse_groups = 0
        total_groups = 0
        diverse_records = 0
        
        for name, group in groups:
            total_groups += 1
            unique_sensitive = group[sensitive_attr].nunique()
            
            if unique_sensitive >= l:
                diverse_groups += 1
                diverse_records += len(group)
        
        diversity_rate = diverse_groups / total_groups * 100 if total_groups > 0 else 0
        record_protection = diverse_records / len(df) * 100
        
        results[l] = {
            'diverse_groups': diverse_groups,
            'diversity_rate': diversity_rate,
            'protected_records': diverse_records,
            'record_protection': record_protection
        }
        
        print(f"\nL-diversity (l={l}):")
        print(f"  Diverse groups: {diverse_groups:,}/{total_groups:,} ({diversity_rate:.1f}%)")
        print(f"  Protected records: {diverse_records:,}/{len(df):,} ({record_protection:.1f}%)")
    
    return results

def t_closeness_analysis(df, quasi_identifiers, sensitive_attr, t_values=[0.1, 0.2, 0.5]):
    """T-closeness analysis with Earth Mover's Distance"""
    
    print(f"\n{'='*60}")
    print("T-CLOSENESS ANALYSIS") 
    print("="*60)
    
    # For continuous attributes, bin them
    if df[sensitive_attr].dtype in ['int64', 'float64'] and df[sensitive_attr].nunique() > 20:
        df[f'{sensitive_attr}_binned'] = pd.qcut(df[sensitive_attr], q=10, duplicates='drop')
        analysis_attr = f'{sensitive_attr}_binned'
    else:
        analysis_attr = sensitive_attr
    
    global_dist = df[analysis_attr].value_counts(normalize=True).sort_index()
    groups = df.groupby(quasi_identifiers)
    
    results = {}
    for t in t_values:
        close_groups = 0
        total_groups = 0
        close_records = 0
        
        for name, group in groups:
            if len(group) < 5:  # Skip tiny groups
                continue
                
            total_groups += 1
            local_dist = group[analysis_attr].value_counts(normalize=True).sort_index()
            
            # Simple EMD approximation
            all_values = sorted(set(global_dist.index) | set(local_dist.index))
            global_aligned = [global_dist.get(v, 0) for v in all_values]
            local_aligned = [local_dist.get(v, 0) for v in all_values]
            
            # Calculate Earth Mover's Distance approximation
            emd = sum(abs(g - l) for g, l in zip(global_aligned, local_aligned)) / 2
            
            if emd <= t:
                close_groups += 1
                close_records += len(group)
        
        closeness_rate = close_groups / total_groups * 100 if total_groups > 0 else 0
        record_protection = close_records / len(df) * 100
        
        results[t] = {
            'close_groups': close_groups,
            'closeness_rate': closeness_rate,
            'protected_records': close_records,
            'record_protection': record_protection
        }
        
        print(f"\nT-closeness (t={t}):")
        print(f"  T-close groups: {close_groups:,}/{total_groups:,} ({closeness_rate:.1f}%)")
        print(f"  Protected records: {close_records:,}/{len(df):,} ({record_protection:.1f}%)")
    
    return results

# =============================================================================
# DEANONYMIZATION ATTACKS
# =============================================================================

def demonstrate_tip_attack():
    """Demonstrate tip-based deanonymization attack"""
    
    print(f"\n{'='*60}")
    print("DEANONYMIZATION ATTACK: TIP PATTERN ANALYSIS")
    print("="*60)
    
    # Find users with consistent tipping patterns
    user_patterns = df.groupby(['PULocationID']).agg({
        'tip_percentage': ['mean', 'std', 'count'],
        'pickup_hour': lambda x: x.mode().iloc[0] if len(x) > 0 else None,
        'DOLocationID': 'nunique'
    }).round(2)
    
    user_patterns.columns = ['avg_tip', 'tip_std', 'trip_count', 'common_hour', 'unique_destinations']
    user_patterns = user_patterns[user_patterns['trip_count'] >= 3]  # Regular users
    user_patterns = user_patterns.dropna()
    
    if len(user_patterns) == 0:
        print("No users with sufficient trip history for analysis")
        return
    
    # Find users with consistent behavior (low standard deviation in tipping)
    consistent_tippers = user_patterns[user_patterns['tip_std'] < 3.0].head(10)
    
    print("Top consistent tippers (attackable profiles):")
    print(consistent_tippers[['avg_tip', 'tip_std', 'trip_count', 'unique_destinations']])
    
    # Simulate attack on most consistent tipper
    if len(consistent_tippers) > 0:
        target_pickup = consistent_tippers.index[0]
        target_tip_avg = consistent_tippers.loc[target_pickup, 'avg_tip']
        
        print(f"\n--- ATTACK SIMULATION ---")
        print(f"Target: Pickup Location {target_pickup}")
        print(f"Known pattern: ~{target_tip_avg:.1f}% tip")
        
        # Find all trips matching this pattern
        tip_tolerance = 3.0
        matching_trips = df[
            (df['PULocationID'] == target_pickup) & 
            (df['tip_percentage'].between(target_tip_avg - tip_tolerance, 
                                        target_tip_avg + tip_tolerance))
        ]
        
        print(f"Potentially identified trips: {len(matching_trips)}")
        if len(matching_trips) > 0:
            print(f"Revealed destinations: {matching_trips['DOLocationID'].nunique()} unique locations")
            print(f"Revealed time patterns: {sorted(matching_trips['pickup_hour'].unique())}")
            print(f"Total spending revealed: ${matching_trips['total_amount'].sum():.2f}")
            
            # Show some example trips (anonymized output)
            print(f"\nSample identified trips:")
            sample_trips = matching_trips[['pickup_hour', 'DOLocationID', 'tip_percentage', 'total_amount']].head(5)
            print(sample_trips.to_string(index=False))

def location_correlation_attack():
    """Analyze how location patterns can identify individuals"""
    
    print(f"\n{'='*60}")
    print("LOCATION CORRELATION ATTACK")
    print("="*60)
    
    # Find unique pickup->dropoff patterns
    route_patterns = df.groupby(['PULocationID', 'DOLocationID']).size()
    unique_routes = route_patterns[route_patterns == 1]
    
    print(f"Unique routes (appearing exactly once): {len(unique_routes):,}")
    print(f"These represent {len(unique_routes)/len(df)*100:.2f}% of all trips")
    
    # Find users with very specific route patterns
    route_diversity = df.groupby('PULocationID')['DOLocationID'].nunique()
    low_diversity_users = route_diversity[route_diversity <= 2]
    
    print(f"\nUsers with low route diversity (≤2 destinations): {len(low_diversity_users)}")
    if len(low_diversity_users) > 0:
        print(f"Examples of highly identifiable users:")
        for pickup_id in low_diversity_users.head(5).index:
            user_trips = df[df['PULocationID'] == pickup_id]
            destinations = user_trips['DOLocationID'].unique()
            print(f"  Pickup {pickup_id}: {len(destinations)} destinations {list(destinations)}, {len(user_trips)} total trips")

def temporal_pattern_attack():
    """Analyze temporal patterns for identification"""
    
    print(f"\n{'='*60}")
    print("TEMPORAL PATTERN ATTACK")
    print("="*60)
    
    # Find users with very regular schedules
    user_temporal = df.groupby('PULocationID').agg({
        'pickup_hour': lambda x: len(set(x)),
        'pickup_day': lambda x: len(set(x)),
        'tpep_pickup_datetime': 'count'
    })
    
    user_temporal.columns = ['unique_hours', 'unique_days', 'trip_count']
    
    # Users with regular patterns (few unique hours/days but multiple trips)
    regular_users = user_temporal[
        (user_temporal['unique_hours'] <= 3) & 
        (user_temporal['unique_days'] <= 2) & 
        (user_temporal['trip_count'] >= 5)
    ]
    
    print(f"Highly regular users (predictable schedules): {len(regular_users)}")
    
    if len(regular_users) > 0:
        print(f"Examples of predictable users:")
        for pickup_id in regular_users.head(5).index:
            user_trips = df[df['PULocationID'] == pickup_id]
            hours = sorted(user_trips['pickup_hour'].unique())
            days = sorted(user_trips['pickup_day'].unique())
            print(f"  Pickup {pickup_id}: Hours {hours}, Days {days}, {len(user_trips)} trips")
    
    # Overall temporal predictability
    total_users = len(user_temporal[user_temporal['trip_count'] >= 5])
    predictable_pct = len(regular_users) / total_users * 100 if total_users > 0 else 0
    print(f"Predictable users rate: {predictable_pct:.1f}% of regular users")

def payment_behavior_attack():
    """Analyze payment behavior patterns - FIXED VERSION"""
    
    print(f"\n{'='*60}")
    print("PAYMENT BEHAVIOR ATTACK")
    print("="*60)
    
    # Analyze payment consistency - FIXED
    user_payments = df.groupby('PULocationID')['payment_type'].apply(lambda x: x.mode().iloc[0] == x)
    consistent_payers = pd.Series(user_payments).groupby(level=0).all()
    consistent_payers = consistent_payers[consistent_payers].head(10)
    
    print(f"Users with consistent payment methods: {len(consistent_payers)}")
    
    # Combined behavioral fingerprint
    behavioral_fingerprint = df.groupby('PULocationID').agg({
        'tip_percentage': 'std',
        'payment_type': lambda x: (x.mode().iloc[0] == x).mean(),
        'pickup_hour': 'std', 
        'passenger_count': 'std',
        'tpep_pickup_datetime': 'count'
    }).round(2)
    
    behavioral_fingerprint.columns = ['tip_consistency', 'payment_consistency', 'time_consistency', 'passenger_consistency', 'trip_count']
    behavioral_fingerprint = behavioral_fingerprint.fillna(0)
    
    # Find most predictable users
    predictable_users = behavioral_fingerprint[
        (behavioral_fingerprint['tip_consistency'] < 3) &
        (behavioral_fingerprint['payment_consistency'] > 0.8) &
        (behavioral_fingerprint['time_consistency'] < 4) &
        (behavioral_fingerprint['trip_count'] >= 5)
    ].head(10)
    
    print(f"\nMost predictable users (highest attack success probability): {len(predictable_users)}")
    if len(predictable_users) > 0:
        print(predictable_users)

# =============================================================================
# MAIN ANALYSIS EXECUTION
# =============================================================================

def run_comprehensive_analysis():
    """Run complete privacy analysis"""
    
    # Comprehensive EDA
    comprehensive_eda()
    
    # Advanced analysis
    user_profiles = user_behavior_clustering()
    trip_pattern_analysis()
    
    # Basic sensitive attribute analysis
    analyze_sensitive_attributes()
    
    # Define quasi-identifier combinations to test
    qi_combinations = [
        ['PULocationID', 'pickup_hour'],
        ['PULocationID', 'pickup_hour', 'payment_type'],
        ['PULocationID', 'DOLocationID'],
        ['pickup_hour', 'payment_type', 'passenger_count'],
    ]
    
    # Test different sensitive attributes
    sensitive_attributes = ['tip_percentage', 'DOLocationID', 'total_amount']
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PRIVACY METRIC ANALYSIS")
    print("="*80)
    
    # Test each combination
    for qi in qi_combinations:
        print(f"\n{'='*40}")
        print(f"Testing QI combination: {qi}")
        print("="*40)
        
        # K-anonymity
        k_results, groups = k_anonymity_analysis(df, qi)
        
        # L-diversity and T-closeness for each sensitive attribute
        for sensitive_attr in sensitive_attributes:
            if sensitive_attr in df.columns:
                print(f"\n--- Sensitive Attribute: {sensitive_attr} ---")
                l_results = l_diversity_analysis(df, qi, sensitive_attr)
                if len(df) > 100:  # Only run t-closeness for larger datasets
                    t_results = t_closeness_analysis(df, qi, sensitive_attr)
    
    # Deanonymization attacks
    demonstrate_tip_attack()
    location_correlation_attack() 
    temporal_pattern_attack()
    payment_behavior_attack()
    
    # Final summary
    print(f"\n{'='*80}")
    print("PRIVACY VULNERABILITY SUMMARY")
    print("="*80)
    print("Key findings:")
    print("1. Tip percentage creates strong behavioral fingerprints")
    print("2. Location patterns are highly identifying")
    print("3. Temporal regularity enables prediction attacks") 
    print("4. Combined attributes create unique user signatures")
    print("5. Even 'anonymous' data contains re-identification risks")
    print("\nRecommendations:")
    print("- Generalize location data to broader zones")
    print("- Add noise to tip amounts")
    print("- Bin temporal data to broader windows")
    print("- Consider differential privacy for high-risk attributes")

# Run the complete analysis
if __name__ == "__main__":
    run_comprehensive_analysis()