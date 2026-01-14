# DARNtids Examples

This document provides practical examples for common use cases.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Single Event Processing](#single-event-processing)
3. [Batch Processing](#batch-processing)
4. [Classification Examples](#classification-examples)
5. [Visualization Examples](#visualization-examples)
6. [Advanced Usage](#advanced-usage)

---

## Quick Start Examples

### Example 1: Process One Month of Data

```python
import darntids
import datetime

# Configuration
params = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 6, 1),
    'list_eDate': datetime.datetime(2015, 6, 30),
    'db_name': 'mstid_june2015',
    'data_path': 'data/june2015',
    'fitacf_dir': '/data/sd-data',
    'fovModel': 'GS',
    'rti_fraction_threshold': 0.25
}

# Create run list
dct_list = darntids.run_helper.create_music_run_list(**params)

# Process through RTI interpolation
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='rti_interp',
    new_list=True,
    multiproc=True,
    nprocs=4
)

print("Processing complete! Check data/june2015/mstid_index/ for results.")
```

### Example 2: Complete Pipeline for Test Dataset

```python
import darntids
import datetime

# Small test dataset: 1 week
params = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 6, 15),
    'list_eDate': datetime.datetime(2015, 6, 21),
    'db_name': 'mstid_test_week',
    'data_path': 'test_data',
    'fitacf_dir': '/data/sd-data',
    'fovModel': 'GS',
    'rti_fraction_threshold': 0.25,
    'terminator_fraction_threshold': 1.0
}

dct_list = darntids.run_helper.create_music_run_list(**params)

# Step 1-3: Generate events and interpolate
darntids.run_helper.get_events_and_run(
    dct_list, process_level='rti_interp', new_list=True
)

# Step 4: FFT analysis
darntids.run_helper.get_events_and_run(
    dct_list, process_level='fft'
)

# Step 5: Classification
darntids.classify.run_mstid_classification(dct_list)

# Step 6: MUSIC detection (only on MSTID events)
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='music',
    category_filter={'category_manu': 'mstid'}
)

print("Complete pipeline finished!")
```

---

## Single Event Processing

### Example 3: Process One Event Manually

```python
import darntids
import datetime

# Define single event
radar = 'bks'
sTime = datetime.datetime(2015, 6, 21, 14, 0)
eTime = datetime.datetime(2015, 6, 21, 16, 0)

# Create data object with RTI interpolation
dataObj = darntids.more_music.create_music_obj(
    radar=radar,
    sTime=sTime,
    eTime=eTime,
    fitacf_dir='/data/sd-data',
    fovModel='GS',
    gscat=1,
    beam_limits=None,
    gate_limits=[10, 75],
    bad_range_km=500.0
)

print(f"Data object created: {dataObj}")
print(f"Data coverage: {dataObj.metadata['orig_rti_fraction']:.2%}")

# Run FFT
dataObj_fft = darntids.more_music.run_music(
    radar=radar,
    sTime=sTime,
    eTime=eTime,
    process_level='fft',
    data_path='single_event_test'
)

# Run MUSIC detection
dataObj_music = darntids.more_music.run_music(
    radar=radar,
    sTime=sTime,
    eTime=eTime,
    process_level='music',
    data_path='single_event_test'
)

print(f"MUSIC analysis complete!")
print(f"Signals detected: {len(dataObj_music.signals)}")
```

### Example 4: Inspect Event Data

```python
import darntids
import datetime
from darntids import hdf5_api

# Load processed HDF5 file
radar = 'bks'
sTime = datetime.datetime(2015, 6, 21, 14, 0)
fTime = datetime.datetime(2015, 6, 21, 16, 0)

filepath = f'data/mstid_index/{radar}/{sTime.strftime("%Y%m%d")}/{radar}_{sTime:%Y%m%d_%H%M}_{fTime:%Y%m%d_%H%M}.hdf5'

# Read metadata
with hdf5_api.open_hdf5(filepath, 'r') as hf:
    metadata = hdf5_api.read_metadata(hf)
    print(f"Process level: {metadata['process_level']}")
    print(f"RTI fraction: {metadata['orig_rti_fraction']:.2%}")

    # Read arrays if MUSIC processed
    if metadata['process_level'] == 'music':
        signals = hdf5_api.read_signals(hf)
        print(f"Detected {len(signals)} signals:")
        for i, sig in enumerate(signals):
            print(f"  Signal {i+1}: λ={sig['wavelength']:.0f} km, "
                  f"v={sig['velocity']:.0f} m/s, "
                  f"azim={sig['azimuth']:.1f}°")
```

---

## Batch Processing

### Example 5: Multi-Radar, Multi-Year Processing

```python
import darntids
import datetime

# Large-scale configuration
params = {
    'radars': ['bks', 'wal', 'fhw', 'fhe', 'cvw', 'cve'],
    'list_sDate': datetime.datetime(2012, 1, 1),
    'list_eDate': datetime.datetime(2017, 12, 31),
    'db_name': 'mstid_multiradar_2012_2017',
    'data_path': '/data/mstid/multi_2012_2017',
    'fitacf_dir': '/data/sd-data_fitexfilter',
    'fovModel': 'GS',
    'gscat': 1,
    'rti_fraction_threshold': 0.25,
    'terminator_fraction_threshold': 1.0
}

dct_list = darntids.run_helper.create_music_run_list(**params)

# Process in stages with high parallelization
# Stage 1: RTI interpolation
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='rti_interp',
    new_list=True,
    multiproc=True,
    nprocs=60
)

# Stage 2: FFT
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='fft',
    multiproc=True,
    nprocs=60
)

# Stage 3: Classification
darntids.classify.run_mstid_classification(
    dct_list,
    multiproc=True,
    nprocs=10
)

# Stage 4: MUSIC (only on MSTID events to save time)
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='music',
    category_filter={'category_manu': 'mstid'},
    multiproc=True,
    nprocs=60
)

print(f"Multi-year, multi-radar processing complete!")
```

### Example 6: Process Specific Radars Sequentially

```python
import darntids
import datetime

radars = ['bks', 'wal', 'fhw', 'cve']

for radar in radars:
    print(f"\n{'='*50}")
    print(f"Processing {radar}...")
    print(f"{'='*50}\n")

    params = {
        'radars': [radar],
        'list_sDate': datetime.datetime(2015, 1, 1),
        'list_eDate': datetime.datetime(2015, 12, 31),
        'db_name': f'mstid_{radar}_2015',
        'data_path': f'data/{radar}_2015',
        'fitacf_dir': '/data/sd-data',
        'fovModel': 'GS',
        'rti_fraction_threshold': 0.25
    }

    dct_list = darntids.run_helper.create_music_run_list(**params)

    # Full pipeline
    for level in ['rti_interp', 'fft']:
        darntids.run_helper.get_events_and_run(
            dct_list,
            process_level=level,
            new_list=(level == 'rti_interp'),
            multiproc=True,
            nprocs=20
        )

    # Classification
    darntids.classify.run_mstid_classification(dct_list)

    # MUSIC on classified events
    darntids.run_helper.get_events_and_run(
        dct_list,
        process_level='music',
        category_filter={'category_manu': 'mstid'},
        multiproc=True,
        nprocs=20
    )

    print(f"{radar} complete!\n")
```

---

## Classification Examples

### Example 7: Manual Quality Filtering

```python
import darntids
import datetime

# Process events
params = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 6, 1),
    'list_eDate': datetime.datetime(2015, 6, 30),
    'db_name': 'mstid_june2015',
    'data_path': 'data/june2015',
    'fitacf_dir': '/data/sd-data'
}

dct_list = darntids.run_helper.create_music_run_list(**params)

# Generate event list
darntids.run_helper.get_events_and_run(
    dct_list,
    process_level='rti_interp',
    new_list=True
)

# Apply strict quality filter
darntids.classify.classify_none_events(
    mstid_list='guc_bks_20150601_20150630',
    db_name='mstid_june2015',
    rti_fraction_threshold=0.675,  # Strict: 67.5%
    terminator_fraction_threshold=1.0  # 100% daylight
)

# Check results
from darntids.mongo_tools import events_from_mongo

events = events_from_mongo(
    db_name='mstid_june2015',
    mstid_list='guc_bks_20150601_20150630',
    query={'category': {'$ne': 'None'}}
)

print(f"Good quality events: {len(events)}")
```

### Example 8: Custom Classification Query

```python
import darntids
from darntids.mongo_tools import events_from_mongo

# Query MongoDB for specific criteria
events = events_from_mongo(
    db_name='mstid_2015',
    mstid_list='guc_bks_20150101_20151231',
    query={
        'category_manu': 'mstid',
        'orig_rti_fraction': {'$gt': 0.5},  # >50% coverage
        'intpsd_sum': {'$gt': 1000}  # High spectral power
    },
    sort_key='intpsd_sum',
    sort_order=-1  # Descending
)

print(f"Found {len(events)} high-quality MSTID events")

# Process these specific events
for event in events[:10]:  # Top 10
    print(f"{event['sDatetime']}: PSD={event['intpsd_sum']:.1f}, "
          f"coverage={event['orig_rti_fraction']:.2%}")
```

---

## Visualization Examples

### Example 9: Generate Calendar Plots

```python
import darntids
import datetime

# Configuration
params = {
    'radars': ['bks', 'wal', 'fhw'],
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 12, 31),
    'db_name': 'mstid_2015',
    'data_path': 'data/mstid_2015'
}

dct_list = darntids.run_helper.create_music_run_list(**params)

# Generate calendar plots
darntids.calendar_plot(
    dct_list,
    db_name='mstid_2015',
    output_dir='calendars/2015',
    plot_type='occurrence'  # Or 'wavelength', 'velocity'
)

print("Calendar plots saved to calendars/2015/")
```

### Example 10: Plot Single Event RTI

```python
import darntids
import datetime
from darntids import music_support

# Load processed event
radar = 'bks'
sTime = datetime.datetime(2015, 6, 21, 14, 0)
fTime = datetime.datetime(2015, 6, 21, 16, 0)

# Plot RTI with MUSIC overlay
music_support.plot_music_rti(
    radar=radar,
    sTime=sTime,
    fTime=fTime,
    data_path='data/mstid_index',
    output_path=f'plots/rti_{radar}_{sTime:%Y%m%d_%H%M}.png',
    plot_overlay=True  # Show detected signals
)

print("RTI plot saved!")
```

---

## Advanced Usage

### Example 11: Custom Parameter File

```python
import darntids
import datetime
import json

# Create custom parameter dictionary
custom_params = {
    'radar': 'bks',
    'sTime': datetime.datetime(2015, 6, 21, 14, 0),
    'eTime': datetime.datetime(2015, 6, 21, 16, 0),
    'beam_limits': [5, 15],
    'gate_limits': [20, 60],
    'fovModel': 'GS',
    'gscat': 1,
    'bad_range_km': 500.0,
    'hanning_window_space': True,
    'filter_cutoff': 0.0003,  # 0.3 mHz high-pass
    'filterNumtaps': 151,
    'numFreqs': 1024
}

# Save to JSON
json_path = 'init_params/custom_event.json'
with open(json_path, 'w') as f:
    json.dump(custom_params, f, indent=2, default=str)

# Process using parameter file
darntids.more_music.run_music_init_param_file(
    json_path,
    process_level='music',
    data_path='custom_analysis'
)
```

### Example 12: Analyze Multi-Radar Event

```python
import darntids
import datetime

# Same event time for multiple radars
sTime = datetime.datetime(2015, 6, 21, 15, 0)
eTime = datetime.datetime(2015, 6, 21, 17, 0)
radars = ['bks', 'wal', 'fhw', 'cve']

results = {}

for radar in radars:
    print(f"Processing {radar}...")

    dataObj = darntids.more_music.run_music(
        radar=radar,
        sTime=sTime,
        eTime=eTime,
        process_level='music',
        data_path='multi_radar_event'
    )

    if dataObj and hasattr(dataObj, 'signals'):
        results[radar] = {
            'num_signals': len(dataObj.signals),
            'signals': dataObj.signals
        }

# Compare results
print("\n" + "="*60)
print("Multi-Radar Comparison")
print("="*60)
for radar, data in results.items():
    print(f"\n{radar.upper()}:")
    print(f"  Signals detected: {data['num_signals']}")
    if data['num_signals'] > 0:
        sig = data['signals'][0]  # Strongest signal
        print(f"  Primary wavelength: {sig['wavelength']:.0f} km")
        print(f"  Primary velocity: {sig['velocity']:.0f} m/s")
        print(f"  Primary azimuth: {sig['azimuth']:.1f}°")
```

### Example 13: Export Results to CSV

```python
import darntids
from darntids.mongo_tools import events_from_mongo
import pandas as pd

# Query MSTID events
events = events_from_mongo(
    db_name='mstid_2015',
    mstid_list='guc_bks_20150101_20151231',
    query={'category_manu': 'mstid'}
)

# Convert to DataFrame
df = pd.DataFrame(events)

# Select relevant columns
columns = [
    'sDatetime', 'fDatetime', 'radar',
    'orig_rti_fraction', 'intpsd_sum',
    'category_manu'
]

df_export = df[columns]

# Save to CSV
df_export.to_csv('mstid_events_2015.csv', index=False)

print(f"Exported {len(df_export)} events to mstid_events_2015.csv")
```

---

## Troubleshooting Examples

### Example 14: Check Data Availability

```python
import darntids
import datetime
import os

radar = 'bks'
date = datetime.datetime(2015, 6, 21)
fitacf_dir = '/data/sd-data'

# Check if fitacf files exist
fitacf_pattern = f"{fitacf_dir}/{radar}/{date.year}/"
if os.path.exists(fitacf_pattern):
    files = os.listdir(fitacf_pattern)
    fitacf_files = [f for f in files if date.strftime('%Y%m%d') in f]
    print(f"Found {len(fitacf_files)} files for {radar} on {date:%Y-%m-%d}")
else:
    print(f"Directory not found: {fitacf_pattern}")
```

### Example 15: Debug Single Event Failure

```python
import darntids
import datetime
import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

try:
    dataObj = darntids.more_music.create_music_obj(
        radar='bks',
        sTime=datetime.datetime(2015, 6, 21, 14, 0),
        eTime=datetime.datetime(2015, 6, 21, 16, 0),
        fitacf_dir='/data/sd-data',
        fovModel='GS'
    )

    if dataObj:
        print(f"Success! Coverage: {dataObj.metadata['orig_rti_fraction']:.2%}")
    else:
        print("Failed to create data object - check logs above")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

## Next Steps

- See [pipeline.md](pipeline.md) for detailed workflow
- See [configuration.md](configuration.md) for parameter reference
- See [api.md](api.md) for function documentation
- Check `run_DARNtids.py` for production script examples
