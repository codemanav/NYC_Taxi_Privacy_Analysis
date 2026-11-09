# NYC Taxi Data Privacy Analysis - Summary

## Dataset Overview
- **Dataset**: Yellow Taxi Trip Data (January 2025)
- **Total Records**: 3,475,226 trips
- **Unique Pickup Locations**: 261
- **Unique Dropoff Locations**: 260
- **Date Range**: Dec 31, 2024 - Feb 1, 2025

## Identified Attributes

### Quasi-Identifiers (QI)
Attributes that can be used to identify individuals when combined:
1. **PULocationID** - Pickup location
2. **DOLocationID** - Dropoff location
3. **tpep_pickup_datetime** - Pickup timestamp (analyzed as hour)
4. **trip_distance** - Distance traveled (binned)
5. **passenger_count** - Number of passengers

### Sensitive Attributes (SA)
Private information to protect:
1. **tip_amount** - Tipping behavior ($2.96 average)
2. **total_amount** - Spending patterns ($25.61 average)
3. **payment_type** - Payment preference (70% credit card)
4. **fare_amount** - Fare paid ($17.08 average)

## K-Anonymity Analysis Results

### Scenario 1: Location-Based (PULocationID + DOLocationID)
- **k-value**: 1 (CRITICAL RISK)
- **Unique identifiable groups**: 8,675 (26.45%)
- **Groups with k<5**: 55.67%
- **Finding**: Many origin-destination pairs are unique, allowing easy re-identification

### Scenario 2: Location + Time (PU + DO + Hour)
- **k-value**: 1 (CRITICAL RISK)
- **Unique identifiable groups**: 88,299 (42.58%)
- **Groups with k<5**: 66.56%
- **Finding**: Adding temporal dimension significantly increases vulnerability

### Scenario 3: Location + Time + Distance
- **k-value**: 0 (EXTREME RISK)
- **Groups with k<5**: 98.94%
- **Finding**: Almost complete loss of anonymity with distance granularity

### Scenario 4: Location + Time + Passenger Count
- **k-value**: 1 (CRITICAL RISK)
- **Unique identifiable groups**: 135,689 (44.81%)
- **Groups with k<5**: 72.23%
- **Finding**: Passenger count is highly identifying

### Scenario 5: Temporal (Date + Hour + Pickup Location)
- **k-value**: 1 (CRITICAL RISK)
- **Unique identifiable groups**: 27,209 (28.04%)
- **Groups with k<5**: 53.58%
- **Finding**: Even temporal patterns alone enable identification

## Key Privacy Vulnerabilities

### 1. High Re-identification Risk
- All scenarios show k=1 or k=0, meaning individual records are uniquely identifiable
- 26-45% of quasi-identifier combinations are completely unique
- Over 50% of groups fail basic k=5 anonymity threshold

### 2. Location Privacy Issues
- 261 pickup locations create fine-grained tracking capability
- Popular routes (e.g., Penn Station → Times Square) are heavily used but still vulnerable
- Rare routes are immediately identifying

### 3. Temporal Correlation
- Pickup time adds significant identifying power
- Early morning trips (3-5 AM) are especially vulnerable due to low volume
- Peak hours (5-7 PM) offer better anonymity but still insufficient

### 4. Sensitive Attribute Exposure
Once re-identified, attackers can learn:
- Financial behavior (tip amounts reveal generosity/income)
- Regular travel patterns (home/work locations)
- Payment preferences (cash vs credit)
- Lifestyle indicators (late night trips, airport usage)

## Attack Scenarios

### Attack 1: Background Knowledge Attack
**Attacker knows**: "John takes taxi from Location 186 to 163 around 8 PM"
**Result**: Can narrow down to small group and potentially identify exact trip
**Exposed**: John's tip amount ($2.52), total spent ($15.12), exact timestamp

### Attack 2: Home-Work Inference
**Attacker observes**: Regular morning trips from Location A to Location B
**Result**: Can infer home and work locations
**Exposed**: Daily schedule, income level (from fares), lifestyle

### Attack 3: Rare Event Identification
**Attacker knows**: Someone took taxi at 3 AM from rare location
**Result**: Likely unique record (k=1)
**Exposed**: Complete trip details, payment info

## EDA Key Findings

### Trip Patterns
- Peak hours: 5-7 PM (253K-268K trips)
- Low volume: 3-5 AM (20K-28K trips) - HIGH RISK
- Most common passenger count: 1 (79% of trips)
- Average trip: 5.86 miles

### Payment Behavior
- 70% use credit cards (payment_type=1)
- 11% use cash (payment_type=2)
- Tip amounts range $0-$20+ (mean: $2.96)

### Location Hotspots
- Top pickup: Location 161 (169,977 trips)
- Top dropoff: Location 236 (161,376 trips)
- Top route: 237→236 (likely major transportation hub)

## Recommendations for Privacy Enhancement

### Immediate Actions
1. **Generalize locations**: Use zone-level (boroughs) instead of specific location IDs
2. **Bin temporal data**: Use 4-hour windows instead of exact hours
3. **Suppress rare combinations**: Remove records with k<5
4. **Add noise**: Differential privacy techniques for counts

### Advanced Techniques
1. **Apply l-diversity**: Ensure diverse sensitive attribute values in each group
2. **Implement t-closeness**: Match distribution of tip amounts across groups
3. **Geographic aggregation**: Merge adjacent location zones
4. **Temporal smoothing**: Broader time windows for low-volume periods

### Data Publishing Guidelines
1. Never publish exact timestamps
2. Aggregate rare locations (fewer than 1000 trips/month)
3. Remove outlier trips (very long/short distances)
4. Consider synthetic data generation for public releases

## Next Steps for Project

1. **L-Diversity Analysis**: Check if groups have diverse tip amounts/payment types
2. **T-Closeness Evaluation**: Calculate EMD for sensitive attribute distributions
3. **Deanonymization Attacks**: Simulate specific attack scenarios with background knowledge
4. **Anonymization Testing**: Apply generalization and measure utility vs privacy tradeoff
5. **Visualization**: Create attack success rate graphs and privacy-utility curves

## Files Generated
- `eda_yellow_tripdata.py` - Exploratory data analysis script
- `k_anonymity_analysis.py` - K-anonymity evaluation script
- `eda_yellow_tripdata.png` - Visualization charts (9 plots)
- `ANALYSIS_SUMMARY.md` - This summary document
