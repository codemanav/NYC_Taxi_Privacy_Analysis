# Privacy Vulnerabilities in NYC Taxi Trip Data
## Systematic Deanonymization Attacks and Privacy Metric Evaluation

**Project Progress Discussion**

---

# Slide 1: Motivation

## Why This Matters

**The Open Data Dilemma:**
- Cities publish transportation data for transparency and research
- Assumption: Removing names = Privacy protected
- Reality: "Anonymous" data can be re-identified

**Real-World Impact:**
- 2014: NYC taxi data exposed celebrity movements, mosque visitors
- 2019: Researchers linked "anonymized" location data to individuals
- **Our Goal**: Quantify how easily re-identification occurs

**Research Question:**
> How vulnerable is published taxi data to deanonymization attacks, and can we measure the privacy risk?

---

# Slide 2: Problem Statement

## Privacy at Risk

**Dataset:**
- NYC Yellow Taxi Trip Records (3.5M+ trips, Jan 2025)
- Published openly with "identifying information removed"
- Contains: locations, timestamps, fares, tips, payment methods

**The Challenge:**
Combinations of seemingly harmless attributes can uniquely identify individuals:
- "Someone took a taxi from Location 186 → 163 at 8 PM"
- How many people match this? Often just ONE person!

**Privacy Threats:**
1. **Background Knowledge Attacks**: Minimal info → Full trip details
2. **Pattern Inference**: Reveal home/work locations, habits
3. **Sensitive Data Exposure**: Financial behavior, lifestyle patterns

**Our Mission:** Prove the vulnerability exists and measure its severity

---

# Slide 3: Proposed Approach - Overview

## Four-Pillar Methodology

### 1. **Privacy Metrics Evaluation** (20%)
- K-anonymity: Are records indistinguishable in groups?
- L-diversity: Do groups have diverse sensitive values?
- T-closeness: Are sensitive distributions protected?

### 2. **Attack Simulation** (40%)
- Background knowledge attacks
- Temporal correlation attacks
- Location-based re-identification
- Financial pattern matching

### 3. **Risk Quantification** (25%)
- Earth Mover's Distance for attribute distributions
- Re-identification confidence scores
- Success rate metrics across attack scenarios

### 4. **Visualization & Recommendations** (15%)
- Privacy vulnerability heatmaps
- Attack success rate analysis
- Data publishing guidelines

---

# Slide 4: Proposed Approach - Technical Details

## Privacy Metrics Implementation

**K-Anonymity Testing:**
- **Quasi-Identifiers (QI)**: Pickup/dropoff locations, time, distance, passenger count
- **Sensitive Attributes (SA)**: Tip amount, payment type, total fare
- **Target**: Each QI combination should have ≥k identical records (k≥5 safe)

**L-Diversity Analysis:**
- Ensure each k-anonymous group has ≥ℓ distinct sensitive values
- Prevents homogeneity attacks (all in group have same tip behavior)

**T-Closeness Evaluation:**
- Distance between sensitive attribute distribution in group vs. overall dataset
- Use Earth Mover's Distance (EMD) to measure ≤t threshold
- Prevents probabilistic inference attacks

---

# Slide 5: Proposed Approach - Attack Scenarios

## Simulated Deanonymization Attacks

### Attack 1: Minimal Background Knowledge
- **Attacker knows**: Approximate pickup location, time window
- **Goal**: Identify exact trip record
- **Exposed**: Tip amount, payment method, exact route

### Attack 2: Temporal Pattern Exploitation
- **Attacker observes**: Regular morning trips (e.g., commute pattern)
- **Goal**: Infer home and work locations
- **Exposed**: Daily schedule, lifestyle indicators

### Attack 3: Rare Event Targeting
- **Attacker focuses**: Low-volume times (3-5 AM) or uncommon routes
- **Goal**: Exploit uniqueness for re-identification
- **Exposed**: Complete trip metadata, financial behavior

### Attack 4: Financial Pattern Matching
- **Attacker knows**: Tipping behavior or payment preference
- **Goal**: Link multiple trips to same individual
- **Exposed**: Movement patterns over time

---

# Slide 6: Progress Thus Far

## Completed Work & Findings

### ✅ Large-Scale Data Analysis
- **Dataset**: **290.8 MILLION trips** across **80 months** (Jan 2019 - Aug 2025)
- **Files Analyzed**: 80 parquet files, 80 EDA reports, 80 k-anonymity analyses
- **Temporal Coverage**: Pre-COVID, COVID lockdown, recovery, current period
- **Location Granularity**: 254-263 unique pickup/dropoff zones per month

### ✅ Comprehensive K-Anonymity Analysis

| Scenario | Avg K-Value | Avg Unique k=1 | Avg Violation k<5 | Worst Period |
|----------|-------------|----------------|-------------------|--------------|
| **Location Only** | 1 | **27.71%** | 54.68% | 2020-04 (37%) |
| **Location + Time** | 1 | **39.28%** | 63.66% | 2020-04 (53%) |
| **Location + Time + Distance** | 1 | **43.10%** | 68.13% | 2020-04 (57%) |
| **Location + Time + Passenger** | 1 | **44.81%** | 72.23% | 2020-05 (52%) |

### 🚨 **Critical Findings**:
- **ALL 80 months show k=1** - complete privacy failure across 6+ years
- **COVID period (2020)**: 96.3% trip reduction → 53% unique identifiability (WORST)
- **Privacy worsening**: 2025 shows 42.65% unique vs 35.90% in 2019 (19% increase)
- **Never safe**: Even highest volume months (7M+ trips) show 32%+ unique records

---

# Slide 6.5: Key Insights from 80-Month Analysis

## Breakthrough Findings

### 1. COVID-19 Privacy Impact (NEW!)
- **Pre-COVID** (Jan-Feb 2020): 6.35M trips/month, 34-36% unique
- **Lockdown** (Apr-May 2020): 293K trips/month (-96.3%), **53% unique**
- **Insight**: Low volume = Catastrophic privacy loss

### 2. Temporal Privacy Degradation
| Period | Avg Trips/Month | Unique k=1 % | Trend |
|--------|----------------|--------------|-------|
| 2019 | 7.1M | 35.90% | Baseline |
| 2020 | 2.2M | 45.13% | **+25% worse** |
| 2022 | 3.3M | 34.95% | Recovery |
| 2025 | 3.9M | 42.65% | **+19% worse than 2019** |

### 3. Volume Paradox
- **Highest volume** (2019-03: 7.9M trips) → Still 32.66% unique ❌
- **Lowest volume** (2020-04: 238K trips) → 53.17% unique ❌❌❌
- **Conclusion**: Volume helps, but NEVER reaches safety threshold

### 4. Real-World Attack Validation
- NYC 2014 leak: Confirmed celebrities/mosque visitors tracked
- Our analysis: **27-43% direct re-identification possible**
- Attack feasibility: **PROVEN at scale over 6+ years**

---

# Slide 7: Next Steps - Phase 1

## Immediate Next Steps (Weeks 1-2)

### 1. **L-Diversity Implementation**
- Analyze sensitive attribute diversity within k-anonymous groups
- Test different ℓ values (ℓ=2, 3, 5)
- Identify homogeneity vulnerabilities

### 2. **T-Closeness Evaluation**
- Calculate Earth Mover's Distance for tip amounts
- Test payment type distribution similarity
- Measure fare amount distribution protection
- Threshold testing: t=0.1, 0.2, 0.3

### 3. **Advanced Attack Simulations**
- Implement concrete attack algorithms with success rate metrics
- Test background knowledge with 1, 2, 3 known attributes
- Measure confidence scores for re-identification
- Cross-reference with external data sources (if available)

---

# Slide 8: Next Steps - Phase 2

## Future Work (Weeks 3-4)

### 4. **Comprehensive Visualization Suite**
- Privacy risk heatmaps by location and time
- Attack success rate graphs across scenarios
- Privacy-utility tradeoff curves
- Vulnerable demographic identification

### 5. **Anonymization Testing**
- Apply generalization techniques (location coarsening, time binning)
- Implement suppression for rare combinations
- Test differential privacy noise addition
- Measure utility loss vs. privacy gain

### 6. **Final Deliverables**
- Complete technical report with all metrics
- Interactive dashboard for privacy analysis
- Data publishing recommendations document
- Presentation of findings and policy implications

---

# Slide 9: Questions for Feedback

## Discussion Points

### 1. **Scope & Methodology**
- Are our attack scenarios realistic and comprehensive?
- Should we prioritize certain privacy metrics over others?
- Any additional quasi-identifier combinations we should test?

### 2. **Technical Approach**
- Is our Earth Mover's Distance implementation appropriate for t-closeness?
- Should we include synthetic data generation in our evaluation?
- What threshold values (k, ℓ, t) should we target?

### 3. **Project Direction**
- ✅ Already analyzed 80 months (2019-2025) - should we go deeper into specific periods?
- Interest in comparing with other cities' taxi data (Chicago, SF)?
- Focus more on attack development vs. defense mechanisms?
- Should we simulate real-world linkage with external datasets (POIs, social media)?

### 4. **Deliverables**
- What visualization formats would be most impactful?
- Should we develop an automated privacy audit tool?

**We welcome any feedback on our approach and findings so far!**
