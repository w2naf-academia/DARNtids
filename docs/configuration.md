# Configuration Guide

This document provides detailed descriptions of all configuration parameters used in the DARNtids pipeline.

## Table of Contents

1. [Event List Parameters](#event-list-parameters)
2. [Data Processing Parameters](#data-processing-parameters)
3. [Quality Thresholds](#quality-thresholds)
4. [MUSIC Algorithm Parameters](#music-algorithm-parameters)
5. [Database Configuration](#database-configuration)
6. [Execution Control](#execution-control)

---

## Event List Parameters

### Required Parameters

#### `radar` or `radars`
- **Type**: `str` or `list[str]`
- **Description**: SuperDARN radar code(s) to process
- **Valid Values**: 'bks', 'wal', 'fhw', 'fhe', 'cvw', 'cve', 'kap', 'sas', 'pgr', 'gbr', 'han', 'pyk'
- **Example**: `'bks'` or `['bks', 'wal', 'fhw']`

#### `list_sDate` / `sDate`
- **Type**: `datetime.datetime`
- **Description**: Start date for event list generation
- **Example**: `datetime.datetime(2015, 1, 1)`

#### `list_eDate` / `eDate`
- **Type**: `datetime.datetime`
- **Description**: End date for event list generation
- **Example**: `datetime.datetime(2015, 12, 31)`

#### `db_name`
- **Type**: `str`
- **Description**: MongoDB database name for storing events and results
- **Example**: `'mstid_2015'`
- **Naming Convention**: Use descriptive names including year and processing variant
- **Example**: `'mstid_GSMR_fitexfilter_HDF5_2015'`

### Optional Parameters

#### `slt_range`
- **Type**: `list[float, float]`
- **Default**: `[6, 18]`
- **Description**: Solar Local Time range (hours) for event selection
- **Purpose**: Restrict to daylight hours when MSTIDs are most observable
- **Example**: `[8, 20]` for extended daylight analysis

#### `step_days`
- **Type**: `int`
- **Default**: `1`
- **Description**: Day increment for event generation
- **Example**: `1` for daily events, `7` for weekly

#### `step_hours`
- **Type**: `int`
- **Default**: `2`
- **Description**: Hour increment for event windows
- **Standard**: `2` (2-hour windows)
- **Note**: MUSIC algorithm optimized for 2-hour windows

#### `height_km`
- **Type**: `float`
- **Default**: `300.0`
- **Description**: Assumed ionospheric reflection height (km)
- **Purpose**: Used for ground scatter range mapping

---

## Data Processing Parameters

### File Paths

#### `data_path`
- **Type**: `str`
- **Description**: Root directory for HDF5 output files
- **Structure**: `data_path/mstid_index/[radar]/[date]/`
- **Example**: `'mstid_data/mstid_2015'`

#### `fitacf_dir`
- **Type**: `str`
- **Description**: Directory containing raw SuperDARN fitacf files
- **Example**: `'/data/sd-data'` or `'/data/sd-data_fitexfilter'`
- **Note**: Requires proper directory structure: `[radar]/[year]/`

#### `output_dir`
- **Type**: `str`
- **Default**: `'output'`
- **Description**: Directory for PNG plots and visualizations

### Field of View Model

#### `fovModel`
- **Type**: `str`
- **Default**: `'GS'`
- **Valid Values**:
  - `'GS'`: Ground Scatter model (uses reflection point mapping)
  - `'IS'`: Ionospheric Standard model (assumes direct ionospheric backscatter)
- **Description**: Determines how beam-gate cells are mapped to geographic coordinates
- **Recommendation**: Use 'GS' for ground scatter studies, 'IS' for ionospheric backscatter

#### `gscat`
- **Type**: `int`
- **Default**: `1`
- **Valid Values**:
  - `0`: Ionospheric scatter only
  - `1`: Ground scatter only
  - `3`: All scatter types
- **Description**: Filter data by scatter type flag
- **Recommendation**: Use `1` for MSTID studies (ground scatter shows TID signatures)

### Beam and Gate Selection

#### `beam_limits`
- **Type**: `list[int, int]` or `None`
- **Default**: `None` (use all beams)
- **Description**: `[min_beam, max_beam]` range of beams to include
- **Example**: `[0, 15]` for beams 0-15
- **Purpose**: Focus on specific azimuthal sectors

#### `gate_limits`
- **Type**: `list[int, int]` or `None`
- **Default**: `None` (use all gates)
- **Description**: `[min_gate, max_gate]` range of range gates to include
- **Example**: `[10, 75]`
- **Purpose**: Exclude near-field and far-field contamination

#### `bad_range_km`
- **Type**: `float`
- **Default**: `500.0` (for GS mode)
- **Description**: Minimum acceptable range (km) to avoid FOV distortion
- **Purpose**: Ground scatter mapping becomes unreliable at short ranges

### Interpolation

#### `interp_resolution`
- **Type**: `float` or `None`
- **Default**: `None` (use default spacing)
- **Description**: Grid spacing for beam-gate interpolation
- **Units**: Dependent on FOV model

#### `hanning_window_space`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Apply Hanning window taper in beam-gate dimensions
- **Purpose**: Reduce edge effects in spatial domain
- **Recommendation**: Enable for smoother spatial spectra

---

## Quality Thresholds

### Data Coverage

#### `rti_fraction_threshold`
- **Type**: `float`
- **Default**: `0.675` (standard) or `0.25` (relaxed)
- **Range**: `0.0` to `1.0`
- **Description**: Minimum fraction of beam-gate-time cells with valid data
- **Calculation**: `valid_cells / total_cells`
- **Examples**:
  - `0.675`: 67.5% coverage required (strict)
  - `0.25`: 25% coverage required (relaxed)
- **Recommendation**: Use 0.25 for extended radar coverage, 0.675 for high-quality studies

### Daylight Requirement

#### `terminator_fraction_threshold`
- **Type**: `float`
- **Default**: `1.0`
- **Range**: `0.0` to `1.0`
- **Description**: Minimum fraction of event duration in daylight
- **Calculation**: `daylight_minutes / total_minutes`
- **Examples**:
  - `1.0`: 100% daylight required (strict)
  - `0.5`: 50% daylight acceptable (relaxed)
- **Purpose**: MSTIDs are primarily daytime phenomena

### Radar Operational Time

#### `good_period_threshold`
- **Type**: `int`
- **Default**: `110` minutes (for 2-hour window)
- **Description**: Minimum radar operational time (minutes) required
- **Purpose**: Ensure sufficient temporal coverage
- **Calculation**: Total minutes with data transmissions

---

## MUSIC Algorithm Parameters

### Wavenumber Search Space

#### `kxMax`, `kyMax`
- **Type**: `float`
- **Default**: Auto-calculated based on array geometry
- **Units**: rad/km
- **Description**: Maximum wavenumber in x (magnetic east) and y (magnetic north)
- **Purpose**: Define k-space search limits
- **Typical Range**: `0.001` to `0.01` rad/km

### Frequency Selection

#### `numFreqs`
- **Type**: `int`
- **Default**: `512`
- **Description**: Number of FFT frequency bins to analyze
- **Purpose**: Determine frequency resolution
- **Tradeoff**: Higher = better resolution but slower computation

### Azimuthal Resolution

#### `music_angles`
- **Type**: `list[float]` or `int`
- **Default**: 360 angles (1-degree spacing)
- **Description**: Azimuthal angles (degrees) to search for wave propagation
- **Example**: `list(range(0, 360))` or `[0, 45, 90, 135, 180, 225, 270, 315]`

### Temporal Filtering

#### `filter_cutoff`
- **Type**: `float` or `None`
- **Default**: `None` (no filtering)
- **Units**: Frequency (Hz)
- **Description**: High-pass filter cutoff to remove low-frequency trends
- **Purpose**: Isolate MSTID frequencies (typically 0.25-1.0 mHz)

#### `filterNumtaps`
- **Type**: `int`
- **Default**: `101`
- **Description**: Number of filter taps for FIR filter design
- **Purpose**: Control filter sharpness and computational cost

---

## Database Configuration

### MongoDB Connection

#### `mongo_port`
- **Type**: `int`
- **Default**: `27017`
- **Description**: MongoDB server port

#### `mongo_host`
- **Type**: `str`
- **Default**: `'localhost'`
- **Description**: MongoDB server hostname

### SSH Tunneling

#### `ssh_server`
- **Type**: `str` or `None`
- **Default**: `None`
- **Description**: SSH server for remote MongoDB access
- **Example**: `'remote.server.edu'`

#### `ssh_port`
- **Type**: `int`
- **Default**: `22`
- **Description**: SSH port for tunnel

#### `ssh_username`
- **Type**: `str` or `None`
- **Default**: `None`
- **Description**: SSH username for authentication

### Collection Naming

#### `mstid_list`
- **Type**: `str`
- **Auto-generated**: `'guc_{radar}_{sDate}_{eDate}'`
- **Description**: MongoDB collection name for event list
- **Example**: `'guc_bks_20150101_20151231'`

---

## Execution Control

### Processing Level

#### `process_level`
- **Type**: `str`
- **Required**: Yes
- **Valid Values**:
  - `'rti_interp'`: Data interpolation
  - `'fft'`: FFT analysis
  - `'music'`: MUSIC signal detection
- **Description**: Stage of processing pipeline to execute
- **Note**: Must process levels sequentially

### Multiprocessing

#### `multiproc`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Enable parallel processing of events

#### `nprocs`
- **Type**: `int`
- **Default**: `1`
- **Description**: Number of parallel processes
- **Recommendation**: Set to number of CPU cores minus 2
- **Example**: `60` for high-performance cluster, `4` for desktop

### Recomputation

#### `new_list`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Drop existing MongoDB collection and regenerate
- **Warning**: Destroys previous results

#### `recompute`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Reprocess events even if HDF5 files exist
- **Purpose**: Force reanalysis with new parameters

### Filtering

#### `category_filter`
- **Type**: `dict` or `None`
- **Default**: `None` (process all)
- **Description**: MongoDB query to select events for processing
- **Examples**:
  - `{'category_manu': 'mstid'}`: Only MSTID-classified events
  - `{'orig_rti_fraction': {'$gt': 0.5}}`: High data coverage only
  - `{'good_period': True}`: Only quality-passed events

---

## Example Configuration Dictionary

```python
import datetime

# Complete configuration for production run
config = {
    # Event List
    'radars': ['bks', 'wal', 'fhw', 'cve'],
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 12, 31),
    'slt_range': [6, 18],
    'step_hours': 2,

    # Database
    'db_name': 'mstid_GSMR_2015',

    # File Paths
    'data_path': 'mstid_data/mstid_GSMR_2015',
    'fitacf_dir': '/data/sd-data_fitexfilter',
    'output_dir': 'output/mstid_2015',

    # FOV Model
    'fovModel': 'GS',
    'gscat': 1,
    'height_km': 300.0,

    # Array Selection
    'beam_limits': None,  # Use all beams
    'gate_limits': [10, 75],  # Exclude near/far gates
    'bad_range_km': 500.0,

    # Interpolation
    'hanning_window_space': False,

    # Quality Thresholds
    'rti_fraction_threshold': 0.25,
    'terminator_fraction_threshold': 1.0,

    # MUSIC Parameters
    'numFreqs': 512,
    'filterNumtaps': 101,

    # Execution
    'multiproc': True,
    'nprocs': 60
}
```

---

## Parameter Validation

DARNtids performs automatic validation:

1. **Date Range**: Ensures `list_eDate > list_sDate`
2. **Thresholds**: Checks `0 ≤ threshold ≤ 1`
3. **Array Limits**: Validates beam/gate ranges against radar capabilities
4. **File Paths**: Checks directory existence (with warnings)
5. **Radar Codes**: Verifies against known SuperDARN radars

---

## Performance Tuning

### Memory Optimization

- **Large Arrays**: Reduce `numFreqs` or limit beam/gate ranges
- **HDF5 Chunking**: Automatically optimized by package

### Compute Optimization

- **Multiprocessing**: Set `nprocs` to `min(events, cpu_cores - 2)`
- **I/O**: Use local SSD for `data_path`, networked storage for `fitacf_dir`
- **Database**: Run MongoDB locally or use SSH tunnel for remote

### Quality vs. Quantity

- **Strict**: `rti_fraction_threshold=0.675` → fewer, higher-quality events
- **Relaxed**: `rti_fraction_threshold=0.25` → more events, lower average quality
- **Recommendation**: Start strict, relax if insufficient event counts

---

## Common Configuration Scenarios

### Scenario 1: Single Radar, One Year, High Quality

```python
config = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 12, 31),
    'db_name': 'mstid_bks_2015_strict',
    'data_path': 'data/bks_2015',
    'fitacf_dir': '/data/sd-data',
    'fovModel': 'GS',
    'gscat': 1,
    'rti_fraction_threshold': 0.675,
    'terminator_fraction_threshold': 1.0,
    'multiproc': True,
    'nprocs': 20
}
```

### Scenario 2: Multi-Radar, Extended Coverage

```python
config = {
    'radars': ['bks', 'wal', 'fhw', 'fhe', 'cvw', 'cve'],
    'list_sDate': datetime.datetime(2012, 1, 1),
    'list_eDate': datetime.datetime(2017, 12, 31),
    'db_name': 'mstid_multiradar_2012_2017',
    'data_path': 'data/multi_2012_2017',
    'fitacf_dir': '/data/sd-data_fitexfilter',
    'fovModel': 'GS',
    'gscat': 1,
    'rti_fraction_threshold': 0.25,  # Relaxed
    'terminator_fraction_threshold': 0.75,  # Allow some nighttime
    'multiproc': True,
    'nprocs': 60
}
```

### Scenario 3: Test/Development

```python
config = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 6, 1),
    'list_eDate': datetime.datetime(2015, 6, 30),  # One month
    'db_name': 'mstid_test',
    'data_path': 'test_data',
    'fitacf_dir': '/data/sd-data',
    'fovModel': 'GS',
    'gscat': 1,
    'rti_fraction_threshold': 0.25,
    'multiproc': False,  # Easier debugging
    'nprocs': 1
}
```

---

## Next Steps

- See [pipeline.md](pipeline.md) for processing workflow
- See [examples.md](examples.md) for usage examples
- See [api.md](api.md) for function reference
