# Installation Guide

Complete installation instructions for DARNtids.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Database Setup](#database-setup)
4. [Data Access](#data-access)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows (Linux recommended for large-scale processing)
- **Python**: 3.8 or higher
- **RAM**: 8 GB minimum, 16+ GB recommended
- **Disk Space**:
  - 500 MB for package and dependencies
  - 10-100 GB per radar-year for processed data
  - External storage for raw fitacf files (varies)
- **CPU**: Multi-core processor recommended for parallel processing

### Recommended Setup

- **OS**: Linux (Ubuntu 20.04+ or CentOS 7+)
- **Python**: 3.9-3.11
- **RAM**: 32+ GB for multi-radar processing
- **Disk**: SSD for `data_path`, HDD acceptable for `fitacf_dir`
- **CPU**: 16+ cores for efficient multiprocessing
- **Network**: High-speed connection for MongoDB (if remote)

---

## Installation Methods

### Method 1: Conda/Mamba (Recommended)

Conda provides better dependency management for scientific packages.

#### Step 1: Install Conda/Mamba

If you don't have conda installed:

**Option A: Miniconda** (minimal installation)
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

**Option B: Mamba** (faster than conda)
```bash
# Install mamba in base environment
conda install -c conda-forge mamba
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/w2naf-academia/DARNtids.git
cd DARNtids
```

#### Step 3: Create Environment

Using conda:
```bash
conda env create -f environment.yml
```

Or using mamba (faster):
```bash
mamba env create -f environment.yml
```

#### Step 4: Activate Environment

```bash
conda activate mstid
```

#### Step 5: Install Package

```bash
pip install -e .
```

The `-e` flag installs in "editable" mode, allowing you to modify the code without reinstalling.

#### Verification

```bash
python -c "import mstid; print('DARNtids installed successfully!')"
```

---

### Method 2: pip with Virtual Environment

For users who prefer pip-only installation.

#### Step 1: Clone Repository

```bash
git clone https://github.com/w2naf-academia/DARNtids.git
cd DARNtids
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv mstid_env
source mstid_env/bin/activate  # On Windows: mstid_env\Scripts\activate
```

#### Step 3: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

#### Step 4: Install Package

```bash
pip install -e .
```

This will automatically install all dependencies from `pyproject.toml`.

#### Verification

```bash
python -c "import mstid; print('DARNtids installed successfully!')"
```

---

### Method 3: Development Installation

For contributors who need additional development tools.

```bash
# Clone and navigate
git clone https://github.com/w2naf-academia/DARNtids.git
cd DARNtids

# Create environment
conda env create -f environment.yml
conda activate mstid

# Install with development dependencies (when available)
pip install -e .[dev]

# Install testing/documentation tools
pip install pytest pytest-cov sphinx sphinx-rtd-theme
```

---

## Database Setup

### MongoDB Installation

DARNtids uses MongoDB for event catalog storage.

#### Option 1: Local Installation (Recommended for Development)

**On Ubuntu/Debian:**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod
```

**On macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Verify installation:**
```bash
mongosh  # MongoDB shell
# Should connect to localhost:27017
```

#### Option 2: Remote MongoDB (Production)

For cluster or remote server:

```python
# In your Python code
from mstid.mongo_tools import setup_mongo_connection

# SSH tunnel to remote server
connection = setup_mongo_connection(
    ssh_server='remote.server.edu',
    ssh_username='your_username',
    mongo_host='localhost',
    mongo_port=27017
)
```

#### Option 3: Docker (Isolated Environment)

```bash
# Run MongoDB in Docker container
docker run -d \
  --name mstid-mongo \
  -p 27017:27017 \
  -v /path/to/data:/data/db \
  mongo:6.0

# Verify
docker ps
```

---

## Data Access

### SuperDARN fitacf Files

You need access to SuperDARN fitacf data files.

#### Option 1: Direct Download (if you have access)

Contact SuperDARN data distributors for access credentials.

#### Option 2: Use Existing Data Directory

If your institution has SuperDARN data:

```python
# Set fitacf_dir to your data location
fitacf_dir = '/data/superdarn/fitacf'  # Example path
```

Expected directory structure:
```
fitacf_dir/
├── bks/
│   ├── 2015/
│   │   ├── 20150101.*.fitacf.gz
│   │   ├── 20150102.*.fitacf.gz
│   │   └── ...
│   └── 2016/
├── wal/
│   └── 2015/
└── ...
```

#### Option 3: Test with Sample Data

For testing, create a small sample dataset:

```bash
mkdir -p test_data/bks/2015
# Copy a few fitacf files for testing
```

---

## Verification

### Test Installation

Create a test script `test_install.py`:

```python
import mstid
import datetime

# Test imports
from mstid import run_helper, mongo_tools, classify, more_music

print("✓ All modules imported successfully")

# Test basic functionality
params = {
    'radars': ['bks'],
    'list_sDate': datetime.datetime(2015, 1, 1),
    'list_eDate': datetime.datetime(2015, 1, 2),
    'db_name': 'test_db'
}

try:
    dct_list = run_helper.create_music_run_list(**params)
    print("✓ Run list creation successful")
except Exception as e:
    print(f"✗ Run list creation failed: {e}")

print("\nDARNtids installation verified!")
```

Run the test:
```bash
python test_install.py
```

### Check Dependencies

```bash
# Verify all dependencies are installed
pip list | grep -E "pandas|pymongo|numpy|scipy|matplotlib|h5py"
```

Expected output should show all packages installed.

---

## Troubleshooting

### Common Issues

#### Issue 1: `ModuleNotFoundError: No module named 'mstid'`

**Solution:**
```bash
# Ensure you're in the correct environment
conda activate mstid

# Reinstall package
pip install -e .
```

#### Issue 2: MongoDB Connection Error

**Solution:**
```bash
# Check MongoDB is running
sudo systemctl status mongod

# Or for macOS
brew services list

# Restart if needed
sudo systemctl restart mongod
```

#### Issue 3: HDF5 Library Errors

**Solution:**
```bash
# Reinstall h5py
pip uninstall h5py
pip install --no-binary=h5py h5py

# Or use conda version
conda install h5py
```

#### Issue 4: Matplotlib Display Errors on Headless Server

**Solution:**
```python
# Add to top of your scripts
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
```

#### Issue 5: Permission Denied for Data Directories

**Solution:**
```bash
# Create directories with proper permissions
mkdir -p mstid_data/test
chmod 755 mstid_data/test
```

#### Issue 6: Out of Memory Errors

**Solution:**
- Reduce `nprocs` parameter
- Process smaller date ranges
- Use a machine with more RAM
- Add swap space:
  ```bash
  sudo fallocate -l 16G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

### Getting Help

If you encounter issues:

1. **Check Documentation**: Review [README.md](../README.md) and other docs
2. **Search Issues**: Check [GitHub Issues](https://github.com/w2naf-academia/DARNtids/issues)
3. **Ask Questions**: Post in [GitHub Discussions](https://github.com/w2naf-academia/DARNtids/discussions)
4. **Email Support**: nathaniel.frissell@scranton.edu

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Error message (full traceback)
- Steps to reproduce

---

## Upgrading

### Update to Latest Version

```bash
# Navigate to repository
cd DARNtids

# Pull latest changes
git pull origin main

# Update environment (if environment.yml changed)
conda env update -f environment.yml

# Reinstall package
pip install -e .
```

### Check for Updates

```bash
# View recent changes
git log --oneline -10

# Check current version
python -c "import mstid; print(mstid.__version__)"
```

---

## Uninstallation

### Remove Package

```bash
# Deactivate environment
conda deactivate

# Remove conda environment
conda env remove -n mstid

# Or, if using pip virtualenv
deactivate
rm -rf mstid_env
```

### Remove Data (optional)

```bash
# Remove processed data (be careful!)
rm -rf mstid_data/

# Remove MongoDB data
# On Linux
sudo rm -rf /var/lib/mongodb/

# On macOS
rm -rf /usr/local/var/mongodb/
```

---

## Next Steps

After successful installation:

1. Review [Quick Start](../README.md#quick-start) in README
2. Follow [Pipeline Guide](pipeline.md) for processing workflow
3. Try [Examples](examples.md) for specific use cases
4. Configure parameters using [Configuration Guide](configuration.md)

---

## Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Conda/mamba or virtualenv set up
- [ ] DARNtids repository cloned
- [ ] Environment created and activated
- [ ] Package installed (`pip install -e .`)
- [ ] MongoDB installed and running
- [ ] SuperDARN data access configured
- [ ] Installation verified with test script
- [ ] Documentation reviewed

Congratulations! You're ready to use DARNtids.
