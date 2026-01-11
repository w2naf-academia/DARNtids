# DARNtids

**SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit**

A Python package for detecting and characterizing Medium-Scale Traveling Ionospheric Disturbances (MSTIDs) using data from the SuperDARN (Super Dual Auroral Radar Network) global network of coherent scatter radars.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

DARNtids provides a complete pipeline for MSTID analysis including:

- **Data Processing**: Automated ingestion and quality filtering of SuperDARN fitacf data
- **Signal Detection**: MUSIC (Multiple Signal Classification) algorithm implementation for wave detection
- **Classification**: Spectral analysis to distinguish MSTID events from quiet periods
- **Wave Characterization**: Extraction of wave properties (wavelength, frequency, velocity, azimuth)
- **Multi-Radar Analysis**: Simultaneous processing across radar networks
- **Visualization**: Calendar plots, RTI (Range-Time-Intensity) displays, spectral analysis
- **Database Management**: MongoDB integration for event cataloging and retrieval

### Key Features

- **Automated Pipeline**: Process years of data across multiple radars with minimal manual intervention
- **Quality Assurance**: Built-in data quality checks including radar uptime, data coverage, and daylight fraction
- **HDF5 Storage**: Efficient data persistence with HDF5 format
- **Parallel Processing**: Multi-process support for high-throughput analysis
- **Flexible Configuration**: JSON parameter files for reproducible analysis
- **Web Interface**: Tools for manual event review and classification (in `webserver/`)

## Scientific Background

Traveling Ionospheric Disturbances (TIDs) are wave-like perturbations in ionospheric electron density that propagate as atmospheric gravity waves. MSTIDs have horizontal wavelengths of 50-500 km and periods of 15-60 minutes. SuperDARN radars observe TIDs as quasi-periodic variations in ground scatter patterns.

DARNtids uses the MUSIC algorithm to decompose radar backscatter into wavenumber-frequency space, enabling detection and characterization of MSTID wave properties.

## Installation

### Prerequisites

- Python >= 3.8
- MongoDB (for event database storage)
- SuperDARN fitacf data files

### Option 1: Using Conda/Mamba (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/w2naf/DARNtids.git
cd DARNtids
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate mstid
```

3. Install the package in editable mode:
```bash
pip install -e .
```

### Option 2: Using pip only

1. Clone the repository:
```bash
git clone https://github.com/w2naf/DARNtids.git
cd DARNtids
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
import mstid
import datetime

# Define processing parameters
params = {
    'radars': ['bks', 'wal'],  # Blackstone and Wallops radars
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 1, 31),
    'db_name': 'mstid_2015_jan',
    'data_path': 'mstid_data/2015_jan',
    'fovModel': 'GS',  # Ground Scatter mode
    'fitacf_dir': '/path/to/fitacf/data'
}

# Create run configuration
run_list = mstid.run_helper.create_music_run_list(**params)

# Generate event lists and process
mstid.run_helper.get_events_and_run(
    run_list,
    process_level='rti_interp',
    new_list=True,
    multiproc=True,
    nprocs=4
)
```

### Processing Pipeline

The complete analysis workflow consists of several stages:

1. **Event List Generation**: Create 2-hour event windows
2. **Quality Filtering**: Remove events with insufficient data or radar downtime
3. **Data Interpolation**: Create uniform grids from raw radar data (`rti_interp` level)
4. **FFT Analysis**: Compute frequency spectra (`fft` level)
5. **Spectral Classification**: Identify MSTID vs. quiet events
6. **MUSIC Detection**: Extract wave properties (`music` level)
7. **Visualization**: Generate plots and calendar summaries

See [docs/pipeline.md](docs/pipeline.md) for detailed workflow documentation.

## Documentation

- **[Installation Guide](docs/installation.md)**: Detailed installation instructions
- **[Pipeline Overview](docs/pipeline.md)**: Data processing workflow
- **[API Reference](docs/api.md)**: Module and function documentation
- **[Configuration Guide](docs/configuration.md)**: Parameter descriptions
- **[Examples](docs/examples.md)**: Usage examples and tutorials

## Project Structure

```
DARNtids/
├── mstid/                    # Main package
│   ├── more_music.py         # MUSIC processing core
│   ├── classify.py           # Event classification
│   ├── mongo_tools.py        # Database operations
│   ├── run_helper.py         # Workflow orchestration
│   ├── calendar_plot.py      # Calendar visualizations
│   └── music_support.py      # MUSIC utilities
├── webserver/                # Web interface components
├── run_DARNtids.py          # Master processing script
├── run_single_event.py      # Single-event processor
├── docs/                     # Documentation
├── environment.yml           # Conda environment
└── pyproject.toml           # Package metadata
```

## Supported Radars

**North American:**
- bks (Blackstone)
- wal (Wallops)
- fhw, fhe (Fort Hays - West/East)
- cvw, cve (Clyde River - West/East)

**High Latitude:**
- kap (Kapuskasing)
- sas (Saskatoon)
- pgr (Prince George)
- gbr (Goose Bay)

**European:**
- han (Hankasalmi)
- pyk (Pykkvibær)

## Output Products

### Data Files
- **HDF5 Files**: Processed radar data and MUSIC results (`mstid_data/[db_name]/mstid_index/`)
- **MongoDB Records**: Event metadata, classifications, and wave properties
- **JSON Files**: Processing parameters for each event (`init_params/`)

### Visualizations
- **RTI Plots**: Range-Time-Intensity displays with MUSIC overlays
- **K-Array Plots**: Wavenumber-frequency spectrograms
- **Calendar Plots**: Seasonal heatmaps of MSTID occurrence
- **Spectral Plots**: Power spectral density analysis

## Dependencies

### Core
- `pandas` - Data manipulation
- `pymongo` - MongoDB connectivity
- `sshtunnel` - Remote database access
- `ephem` - Solar calculations
- `sh` - Shell utilities

### Scientific (auto-installed)
- `pydarn` - SuperDARN data utilities
- `pyDARNmusic` - MUSIC algorithm
- `numpy`, `scipy` - Numerical computing
- `matplotlib` - Visualization
- `h5py` - HDF5 file format

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/w2naf/DARNtids.git
cd DARNtids
conda env create -f environment.yml
conda activate mstid
pip install -e .[dev]
```

## Citation

If you use DARNtids in your research, please cite:

```bibtex
@software{darntids,
  author = {Frissell, Nathaniel A.},
  title = {DARNtids: SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit},
  url = {https://github.com/w2naf/DARNtids},
  year = {2025}
}
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Authors

**Nathaniel A. Frissell**
- Email: nathaniel.frissell@scranton.edu
- Website: https://hamsci.org

### Contributors
- Nicholas Guerra (HDF5 API implementation)

## Acknowledgments

- SuperDARN community for radar data and infrastructure
- NSF for funding support
- HamSCI (Ham Radio Science Citizen Initiative)

## Support

- **Issues**: [GitHub Issues](https://github.com/w2naf/DARNtids/issues)
- **Discussions**: [GitHub Discussions](https://github.com/w2naf/DARNtids/discussions)
- **Email**: nathaniel.frissell@scranton.edu

## Related Projects

- [pydarn](https://github.com/SuperDARN/pydarn) - Python library for SuperDARN data
- [pyDARNmusic](https://github.com/w2naf/pyDARNmusic) - MUSIC algorithm implementation
- [SuperDARN](http://vt.superdarn.org/) - Global radar network
