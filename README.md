# NYC Taxi Privacy Analysis

An empirical privacy analysis of NYC Yellow Taxi trip data. The project
measures re-identification risk in publicly released trip records using
k-anonymity, l-diversity, t-closeness, exploratory analysis, attack scenarios,
and privacy visualizations.

## Research questions

- How easily can trip records be re-identified from quasi-identifiers?
- How do location, time, distance, and passenger count affect anonymity?
- Which sensitive attributes become exposed after re-identification?
- How does privacy risk change across months, years, and unusual events?

## Data

The analysis downloads Yellow Taxi Parquet files from the NYC TLC public data
endpoint for January 2019 through August 2025. Raw Parquet files are not
included in this folder because the full dataset is several gigabytes.

Download the source data before running the batch analyses:

```bash
python download_data.py
```

The scripts expect the downloaded files under `yellow_taxi_data/`. This
directory is ignored by Git. The included CSV summaries, sample data, plots,
and reports are derived outputs from prior runs.

## Analysis workflow

```text
download_data.py
        |
        +--> batch_eda.py
        |
        +--> batch_k_anonymity.py
        |
        +--> analysis.py / k_anonymity_analysis.py
        |
        +--> fare_lattice.py --> heatmap.py
```

- `batch_eda.py` summarizes monthly trip distributions and trends.
- `batch_k_anonymity.py` evaluates anonymity across all downloaded months.
- `analysis.py` contains the broader EDA, privacy metrics, and attack examples.
- `k_anonymity_analysis.py` runs a focused single-file analysis.
- `fare_lattice.py` evaluates privacy-aware fare generalization.
- `heatmap.py` visualizes fare-lattice results.
- `presentation_slides.md` and the analysis summaries document findings.

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The scripts use pandas, PyArrow, NumPy, SciPy, scikit-learn, matplotlib,
seaborn, requests, and tqdm.

## Key findings

The included reports identify severe privacy risk: many combinations of
pickup/drop-off location, time, distance, and passenger count produce
anonymity groups below a k=5 threshold. Financial and behavioral fields such
as fares, tips, payment type, and trip duration can then become exposed.

See:

- `COMPREHENSIVE_ANALYSIS_SUMMARY.md` - full multi-year results.
- `ANALYSIS_SUMMARY.md` - focused analysis summary.
- `presentation_slides.md` - presentation-ready narrative.

## Responsible use

This project is for privacy research and defensive analysis. Do not use it to
identify, track, or target real people. The reports describe risks in
aggregate; raw trip records and regenerated outputs should be handled under
applicable privacy, legal, and data-governance requirements.

## Reproducibility notes

Results depend on the downloaded TLC files and the versions of the Python
libraries used. Record the data download date and dependency versions when
regenerating results. The scripts use relative paths and should be run from
this project directory.
