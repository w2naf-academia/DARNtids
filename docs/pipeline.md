# DARNtids Processing Pipeline

This document describes the complete data processing pipeline for MSTID detection and analysis.

## Overview

The DARNtids pipeline consists of 7 main stages that transform raw SuperDARN radar data into classified MSTID events with extracted wave properties:

```
Raw fitacf data → Event Lists → Quality Filter → Data Interpolation →
FFT Analysis → Classification → MUSIC Detection → Visualization
```

## Stage 1: Event List Generation

**Purpose**: Create a database of 2-hour event windows covering the analysis period.

**Function**: `mstid.mongo_tools.generate_mongo_list()`

**Process**:
1. Define date range and radar(s)
2. Create 2-hour sliding windows
3. Calculate solar local time (SLT) for each window
4. Filter events by SLT range (default: 6-18 hours, daylight only)
5. Store events in MongoDB collection

**Output**: MongoDB collection with fields:
- `sDatetime`, `fDatetime`: Event start/end times
- `radar`: Radar code (e.g., 'bks', 'wal')
- `slt`, `mlt`: Solar/magnetic local times
- `lat`, `lon`: Radar location
- `category`: Initial classification ('unclassified')

**Example**:
```python
import mstid
import datetime

mstid.mongo_tools.generate_mongo_list(
    radar='bks',
    sDate=datetime.datetime(2015, 1, 1),
    eDate=datetime.datetime(2015, 12, 31),
    slt_range=[6, 18],
    db_name='mstid_2015',
    mstid_list='guc_bks_20150101_20151231'
)
```

**Typical Output**: For 1 year, 1 radar: ~3,285 events (365 days × 18 hours ÷ 2 hours)

---

## Stage 2: Data Quality Filtering

**Purpose**: Remove events with insufficient data or poor quality.

**Function**: `mstid.classify.classify_none_events()`

**Quality Checks**:
1. **Data Availability**: Check if fitacf files exist
2. **Radar Uptime**: Verify radar operational time (default: ≥110 minutes of 120)
3. **Data Coverage**: Calculate fraction of beam-gate-time cells with data
4. **Daylight Fraction**: Ensure sufficient daylight (default: 100% daylight required)

**Thresholds**:
- `rti_fraction_threshold`: Minimum data coverage (0.25 = 25% or 0.675 = 67.5%)
- `terminator_fraction_threshold`: Maximum nighttime allowed (1.0 = no nighttime)

**Process**:
1. Load each event from MongoDB
2. Check data file existence
3. Create temporary musicArray to assess coverage
4. Calculate `orig_rti_fraction`
5. Compute terminator (day/night) fraction
6. Mark as 'None' if failing thresholds, 'unclassified' if passing

**Output**: Updated MongoDB records with:
- `category`: 'None' (bad) or 'unclassified' (good)
- `no_data`: Boolean flag
- `good_period`: Boolean for radar uptime
- `orig_rti_fraction`: Data coverage metric
- `terminator_fraction`: Daylight percentage
- `reject_message`: List of failure reasons

**Example**:
```python
mstid.classify.classify_none_events(
    mstid_list='guc_bks_20150101_20151231',
    db_name='mstid_2015',
    rti_fraction_threshold=0.25,
    terminator_fraction_threshold=1.0
)
```

**Typical Retention**: ~60-70% of events pass quality checks

---

## Stage 3: Data Interpolation (RTI_INTERP Level)

**Purpose**: Create uniformly gridded radar data suitable for spectral analysis.

**Function**: `mstid.more_music.run_music()` with `process_level='rti_interp'`

**Process**:
1. **Load Raw Data**: Read fitacf files using pydarn
2. **Create musicArray**: Initialize FOV (Field of View) model
   - `fovModel='GS'`: Ground scatter mapping
   - `fovModel='IS'`: Ionospheric standard mapping
3. **Apply Filters**:
   - Beam limits (e.g., beams 0-15)
   - Gate limits (e.g., gates 10-75)
   - Ground scatter flag (gscat: 0=ionospheric, 1=ground, 3=all)
4. **Interpolation**:
   - Create uniform beam-gate-time grid
   - Fill missing data using nearest neighbor or linear methods
   - Apply hanning window (optional, for spatial smoothing)
5. **Quality Validation**: Check interpolated data fraction
6. **Save to HDF5**: Store processed array and metadata

**Key Parameters**:
- `beam_limits`: `[min_beam, max_beam]`
- `gate_limits`: `[min_gate, max_gate]`
- `gscat`: Ground scatter selection (0, 1, or 3)
- `bad_range_km`: Minimum range for GS mode (default: 500 km)
- `interp_resolution`: Grid spacing

**Output**:
- HDF5 file: `mstid_data/[db_name]/mstid_index/[radar]/[date]/[radar]_[sDatetime]_[fDatetime].hdf5`
- Updated MongoDB: `process_level='rti_interp'`

**Example**:
```python
mstid.more_music.run_music(
    radar='bks',
    sTime=datetime.datetime(2015, 1, 1, 14, 0),
    eTime=datetime.datetime(2015, 1, 1, 16, 0),
    process_level='rti_interp',
    data_path='mstid_data/mstid_2015',
    fitacf_dir='/data/sd-data',
    fovModel='GS',
    gscat=1
)
```

---

## Stage 4: FFT Analysis (FFT Level)

**Purpose**: Compute frequency spectrum to enable spectral classification.

**Function**: `mstid.more_music.run_music()` with `process_level='fft'`

**Process**:
1. **Load RTI Data**: Read HDF5 from Stage 3
2. **Temporal FFT**: Compute Fast Fourier Transform along time axis
3. **Integrated Power Spectral Density (PSD)**:
   - Calculate PSD for each beam-gate cell
   - Integrate over frequency bands relevant to MSTIDs (typically 0.25-1.0 mHz)
   - Compute statistics: sum, mean, max across FOV
4. **Save Results**: Store FFT arrays and PSD metrics to HDF5

**Output**:
- HDF5 file: Updated with FFT arrays
- Updated MongoDB:
  - `process_level='fft'`
  - `intpsd_sum`, `intpsd_mean`, `intpsd_max`: PSD metrics

**Example**:
```python
mstid.more_music.run_music(
    radar='bks',
    sTime=datetime.datetime(2015, 1, 1, 14, 0),
    eTime=datetime.datetime(2015, 1, 1, 16, 0),
    process_level='fft',
    data_path='mstid_data/mstid_2015'
)
```

---

## Stage 5: Spectral Classification

**Purpose**: Distinguish MSTID events from quiet periods based on spectral power.

**Function**: `mstid.classify.run_mstid_classification()`

**Process**:
1. **Load FFT Results**: Read integrated PSD metrics from MongoDB
2. **Statistical Thresholding**:
   - Compute distribution of PSD across all events
   - Identify outliers (high power = MSTID candidates)
   - Apply percentile-based thresholds
3. **Classification**:
   - `intpsd_sum > threshold`: Mark as 'mstid'
   - `intpsd_sum ≤ threshold`: Mark as 'quiet'
4. **Generate Spectral Plots**: Visualization of PSD distributions
5. **Update Database**: Set `category_manu` field

**Output**:
- Updated MongoDB: `category_manu` set to 'mstid' or 'quiet'
- PNG plots: `output/classify/[radar]_[date]_spectral.png`

**Example**:
```python
mstid.classify.run_mstid_classification(
    dct_list,
    db_name='mstid_2015',
    output_dir='output/classify',
    multiproc=True,
    nprocs=5
)
```

**Typical Classification**: ~10-30% of events classified as MSTID (varies by season/location)

---

## Stage 6: MUSIC Signal Detection (MUSIC Level)

**Purpose**: Extract wave properties (wavelength, frequency, velocity, azimuth) using the MUSIC algorithm.

**Function**: `mstid.more_music.run_music()` with `process_level='music'`

**MUSIC Algorithm Steps**:

1. **K-Array Calculation**:
   - Delay-sum beamforming in wavenumber-frequency (k-ω) space
   - Create 2D spectrum of wave energy vs. wavenumber and frequency
   - Search k_x, k_y space (horizontal wavenumbers in x/y directions)

2. **Eigenvalue Decomposition**:
   - Compute covariance matrix of spatial array response
   - Decompose into signal and noise subspaces
   - MUSIC pseudospectrum highlights coherent signals

3. **Peak Detection**:
   - Identify local maxima in k-ω space
   - Filter peaks by power threshold
   - Rank signals by eigenvalue separation

4. **Wave Property Extraction**:
   For each detected signal:
   - **Wavenumber**: k = √(k_x² + k_y²)
   - **Wavelength**: λ = 2π/k (km)
   - **Azimuth**: θ = arctan2(k_y, k_x) (degrees)
   - **Frequency**: ω (rad/s) or f (mHz)
   - **Period**: T = 1/f (minutes)
   - **Phase Velocity**: v = ω/k (m/s)

**Key Parameters**:
- `kxMax`, `kyMax`: Wavenumber search limits
- `numFreqs`: Number of FFT frequencies to analyze
- `music_angles`: Azimuthal search angles
- `filter_cutoff`: Temporal filter settings

**Output**:
- HDF5 file: K-array, detected signals, wave properties
- Updated MongoDB:
  - `process_level='music'`
  - `music_analysis_status=True`
  - Signal properties (wavelength, frequency, velocity, azimuth)
- PNG plots: K-array visualizations with detected signals

**Example**:
```python
mstid.more_music.run_music(
    radar='bks',
    sTime=datetime.datetime(2015, 1, 1, 14, 0),
    eTime=datetime.datetime(2015, 1, 1, 16, 0),
    process_level='music',
    data_path='mstid_data/mstid_2015'
)
```

---

## Stage 7: Visualization and Analysis

**Purpose**: Create summary visualizations and statistical analyses.

### Calendar Plots

**Function**: `mstid.calendar_plot()`

Creates seasonal heatmap calendars showing:
- MSTID occurrence frequency by day-of-year and hour-of-day
- Mean wave properties (wavelength, velocity, azimuth)
- Multi-radar comparisons

**Example**:
```python
mstid.calendar_plot(
    dct_list,
    db_name='mstid_2015',
    output_dir='calendar_output'
)
```

### RTI Plots

**Function**: `mstid.music_support.plot_music_rti()`

Generates Range-Time-Intensity plots with:
- Original radar backscatter
- Interpolated data
- MUSIC signal overlays
- Wave property annotations

### Statistical Analysis

Additional analysis tools in `webserver/`:
- Multi-radar correlation analysis
- Logistic regression for classification improvement
- Blob detection and tracking
- Event epoch comparisons

---

## Complete Pipeline Example

```python
import mstid
import datetime

# Configuration
params = {
    'radars': ['bks', 'wal', 'fhw', 'cve'],
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 12, 31),
    'db_name': 'mstid_2015',
    'data_path': 'mstid_data/mstid_2015',
    'fovModel': 'GS',
    'gscat': 1,
    'rti_fraction_threshold': 0.25,
    'terminator_fraction_threshold': 1.0,
    'fitacf_dir': '/data/sd-data_fitexfilter'
}

# Create run list
dct_list = mstid.run_helper.create_music_run_list(**params)

# Stage 1-2: Generate and filter events
mstid.run_helper.get_events_and_run(
    dct_list,
    process_level='rti_interp',
    new_list=True,
    multiproc=True,
    nprocs=60
)

# Stage 3: RTI interpolation (already done above)

# Stage 4: FFT analysis
mstid.run_helper.get_events_and_run(
    dct_list,
    process_level='fft',
    multiproc=True,
    nprocs=60
)

# Stage 5: Spectral classification
mstid.classify.run_mstid_classification(
    dct_list,
    multiproc=True,
    nprocs=5
)

# Stage 6: MUSIC detection (only on classified MSTID events)
mstid.run_helper.get_events_and_run(
    dct_list,
    process_level='music',
    category_filter={'category_manu': 'mstid'},
    multiproc=True,
    nprocs=60
)

# Stage 7: Visualization
mstid.calendar_plot(dct_list, output_dir='calendars')
```

---

## Processing Time Estimates

For a single radar, one year of data (~2,000 good events):

| Stage | Time per Event | Total Time (60 cores) |
|-------|----------------|----------------------|
| Event List | N/A | ~1 minute |
| Quality Filter | 5-10 sec | ~5 minutes |
| RTI Interpolation | 30-60 sec | ~30 minutes |
| FFT | 5-10 sec | ~5 minutes |
| Classification | 2-5 sec | ~2 minutes |
| MUSIC Detection | 60-120 sec | ~1 hour |
| **Total** | - | **~2-3 hours** |

*Note: Times vary based on data density, system performance, and parameter choices.*

---

## Data Storage Requirements

For a single radar, one year:

| Component | Size per Event | Total (2,000 events) |
|-----------|---------------|---------------------|
| Raw fitacf | ~5-20 MB | 10-40 GB (external) |
| HDF5 (RTI) | ~1-5 MB | 2-10 GB |
| HDF5 (FFT) | +500 KB | +1 GB |
| HDF5 (MUSIC) | +2-5 MB | +4-10 GB |
| MongoDB | ~5 KB | 10 MB |
| PNG Plots | ~500 KB | 1 GB |
| **Total** | - | **~8-22 GB** |

---

## Error Handling

Common errors and solutions:

1. **No data available**: Check `fitacf_dir` path and file naming conventions
2. **Low RTI fraction**: Adjust `rti_fraction_threshold` or check radar operational logs
3. **MUSIC fails**: Verify FFT completed successfully, check parameter constraints
4. **Memory errors**: Reduce `nprocs`, process smaller date ranges
5. **MongoDB connection**: Verify SSH tunnel or local MongoDB service

---

## Best Practices

1. **Start Small**: Test pipeline on 1 month before processing full years
2. **Monitor Quality**: Review `orig_rti_fraction` distributions
3. **Validate Classifications**: Manually review spectral plots
4. **Incremental Processing**: Process by level to catch errors early
5. **Backup Data**: HDF5 files are expensive to regenerate
6. **Document Parameters**: Save JSON parameter files for reproducibility

---

## Next Steps

- See [configuration.md](configuration.md) for detailed parameter descriptions
- See [examples.md](examples.md) for specific use cases
- See [api.md](api.md) for function reference
