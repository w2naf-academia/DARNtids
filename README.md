# DARNtids

**SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit**

A Python package for detecting and characterizing Medium-Scale Traveling Ionospheric Disturbances (MSTIDs) using data from the SuperDARN (Super Dual Auroral Radar Network) global network of coherent scatter radars.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Project History

DARNtids was originally developed by **Dr. Nathaniel A. Frissell** to support the analysis published in:

> Frissell, N. A., J. B. H. Baker, J. M. Ruohoniemi, R. A. Greenwald, A. J. Gerrard, E. S. Miller, and M. L. West (2016), Sources and characteristics of medium-scale traveling ionospheric disturbances observed by high-frequency radars in the North American sector, *J. Geophys. Res. Space Physics*, 121, doi:[10.1002/2015JA022168](https://doi.org/10.1002/2015JA022168).

This foundational work used SuperDARN radar observations to study the relationship between MSTIDs and polar vortex dynamics, demonstrating that polar atmospheric processes, rather than space weather activity, are primarily responsible for controlling MSTID occurrence.

The codebase has evolved through two major modernization efforts:

**Python 3 Migration (2023)** - **Francis Hassan Tholley** updated the original Python 2 codebase to Python 3 and migrated from the deprecated DaViTpy library to the actively developed PyDARN library. This work drastically reduced analysis runtime and ensured compatibility with modern Python environments. This work was completed as part of his MS Software Engineering thesis:

> Tholley, F. H. (2023), PyDARNMUSIC/PyDARNMUSICWeb: Software for SuperDARN Medium Scale Traveling Ionospheric Disturbance Visualization and Analysis, *MS Thesis, University of Scranton*, [https://archives.scranton.edu/digital/collection/p15111coll1/id/1403/rec/1](https://archives.scranton.edu/digital/collection/p15111coll1/id/1403/rec/1).

**HDF5 Data Format Migration (2025)** - **Nicholas J. Guerra** replaced the legacy pickle file storage system with the HDF5 file format, addressing critical issues with portability, interoperability, testability, and maintainability. This migration provides hierarchical data organization, improved compression, cross-platform compatibility, and enhanced data security while following FAIR (Findable, Accessible, Interoperable, and Reusable) data principles. This work was completed as part of his MS Software Engineering thesis:

> Guerra, N. J. (2025), Migrating From Legacy Pickle Files to HDF5 in PyDARN-MUSIC & DARNtids and Implementing a Comprehensive Testing Suite, *MS Thesis, University of Scranton*, [https://archives.scranton.edu/digital/collection/p15111coll1/id/1487/rec/2](https://archives.scranton.edu/digital/collection/p15111coll1/id/1487/rec/2).

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
- **HDF5 Storage**: Modern, efficient data persistence using HDF5 format following FAIR data principles
  - Hierarchical organization for complex SuperDARN datasets
  - Cross-platform portability and language interoperability
  - Efficient compression and fast I/O performance
  - Self-describing metadata for enhanced reproducibility
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

If you use DARNtids in your research, please cite the original paper and software:

**Original Research:**
```bibtex
@article{frissell2016sources,
  author = {Frissell, N. A. and Baker, J. B. H. and Ruohoniemi, J. M. and Greenwald, R. A. and Gerrard, A. J. and Miller, E. S. and West, M. L.},
  title = {Sources and characteristics of medium-scale traveling ionospheric disturbances observed by high-frequency radars in the North American sector},
  journal = {Journal of Geophysical Research: Space Physics},
  volume = {121},
  year = {2016},
  doi = {10.1002/2015JA022168}
}
```

**Software:**
```bibtex
@software{darntids,
  author = {Frissell, Nathaniel A. and Tholley, Francis Hassan and Guerra, Nicholas J.},
  title = {DARNtids: SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit},
  url = {https://github.com/w2naf/DARNtids},
  year = {2025}
}
```

**Related Theses:**
```bibtex
@mastersthesis{tholley2023pydarnmusic,
  author = {Tholley, Francis Hassan},
  title = {PyDARNMUSIC/PyDARNMUSICWeb: Software for SuperDARN Medium Scale Traveling Ionospheric Disturbance Visualization and Analysis},
  school = {University of Scranton},
  year = {2023},
  type = {MS Thesis},
  url = {https://archives.scranton.edu/digital/collection/p15111coll1/id/1403/rec/1}
}

@mastersthesis{guerra2025hdf5,
  author = {Guerra, Nicholas J.},
  title = {Migrating From Legacy Pickle Files to HDF5 in PyDARN-MUSIC \& DARNtids and Implementing a Comprehensive Testing Suite},
  school = {University of Scranton},
  year = {2025},
  type = {MS Thesis},
  url = {https://archives.scranton.edu/digital/collection/p15111coll1/id/1487/rec/2}
}
```

**Example Science Applications:**

The following works demonstrate scientific applications of DARNtids:

```bibtex
@article{frissell2016sources,
  author = {Frissell, N. A. and Baker, J. B. H. and Ruohoniemi, J. M. and Greenwald, R. A. and Gerrard, A. J. and Miller, E. S. and West, M. L.},
  title = {Sources and characteristics of medium-scale traveling ionospheric disturbances observed by high-frequency radars in the North American sector},
  journal = {Journal of Geophysical Research: Space Physics},
  volume = {121},
  year = {2016},
  doi = {10.1002/2015JA022168},
  note = {Original DARNtids application studying MSTID correlation with polar vortex dynamics}
}

@bachelorsthesis{fox2025interhemispheric,
  author = {Fox, James P.},
  title = {Interhemispheric Comparison of the MSTID Response to Sudden Stratospheric Warmings Observed by SuperDARN Radars},
  school = {University of Scranton},
  year = {2025},
  type = {Magis Honors Thesis in STEM},
  url = {https://archives.scranton.edu/digital/collection/p15111coll1/id/1515/rec/4},
  note = {Extended DARNtids for Southern Hemisphere analysis of SSW events}
}

@bachelorsthesis{molzen2025investigation,
  author = {Molzen, Michael},
  title = {Investigation of North American SuperDARN Observations of Medium-Scale Traveling Ionospheric Disturbances During January 2016},
  school = {University of Scranton},
  year = {2025},
  type = {BS Thesis in Physics},
  url = {https://archives.scranton.edu/digital/collection/p15111coll1/id/1530/rec/5},
  note = {Used DARNtids for continental-scale multi-radar MSTID analysis}
}
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Authors and Contributors

**Principal Investigator:**
- **Nathaniel A. Frissell, PhD** - Original developer, project lead
  - Email: nathaniel.frissell@scranton.edu
  - Website: https://hamsci.org

**Major Contributors:**
- **Francis Hassan Tholley, MS** - Python 3 migration and PyDARN library integration (2023)
  - Reimplemented MUSIC algorithm for Python 3 compatibility
  - Migrated from deprecated DaViTpy to PyDARN library
  - Developed PyDARNMUSICWeb interface

- **Nicholas J. Guerra, MS** - HDF5 data format migration and testing framework (2025)
  - Replaced pickle file storage with HDF5 format
  - Implemented FAIR data principles
  - Developed comprehensive testing suite

**Additional Contributors:**
- **James P. Fox, BS** - HDF5 implementation testing and validation (2025)
  - Collaborated with Guerra to test and validate HDF5 implementation
  - Adapted DARNtids for Southern Hemisphere SuperDARN data analysis

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
