# DARNtids
SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit

## Installation

### Option 1: Using Conda/Mamba (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DARNtids.git
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
git clone https://github.com/yourusername/DARNtids.git
cd DARNtids
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Usage

After installation, you can import the package in Python:
```python
import mstid
```

## Requirements

- Python >= 3.8
- pandas
- sshtunnel
- sh
- ephem
- pymongo

## Author

Nathaniel A. Frissell (nathaniel.frissell@scranton.edu)

## Website

https://hamsci.org
