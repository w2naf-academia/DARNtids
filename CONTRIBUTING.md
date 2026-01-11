# Contributing to DARNtids

Thank you for your interest in contributing to DARNtids! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DARNtids.git
   cd DARNtids
   ```

3. **Create development environment**:
   ```bash
   conda env create -f environment.yml
   conda activate mstid
   ```

4. **Install in editable mode**:
   ```bash
   pip install -e .
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Repository Structure

```
DARNtids/
├── mstid/              # Main package code
├── webserver/          # Web interface components
├── docs/               # Documentation
├── tests/              # Unit tests (to be developed)
├── examples/           # Example scripts
└── run_*.py           # Main execution scripts
```

---

## Development Workflow

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/w2naf-academia/DARNtids/issues)
- Comment on the issue you want to work on
- Ask questions if anything is unclear

### 2. Make Changes

- Keep changes focused and atomic
- Write clear, descriptive commit messages
- Test your changes thoroughly

### 3. Commit Guidelines

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example**:
```
feat: add wavelength filtering to MUSIC detection

Implements min/max wavelength thresholds in run_music() to filter
unrealistic wave detections. Adds validation to ensure thresholds
are physically reasonable.

Closes #123
```

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

- Go to GitHub and create a Pull Request
- Fill out the PR template
- Link related issues
- Request review from maintainers

---

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) style guidelines:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters (120 for long strings/URLs)
- **Imports**: Group standard library, third-party, and local imports
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

### Code Organization

```python
# Standard library imports
import os
import datetime

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
import mstid
from mstid.mongo_tools import generate_mongo_list
```

### Documentation

Use **NumPy-style docstrings**:

```python
def run_music(radar, sTime, eTime, process_level='music', **kwargs):
    """
    Execute MUSIC algorithm on SuperDARN radar data.

    Parameters
    ----------
    radar : str
        SuperDARN radar code (e.g., 'bks', 'wal').
    sTime : datetime.datetime
        Event start time.
    eTime : datetime.datetime
        Event end time.
    process_level : str, optional
        Processing stage: 'rti_interp', 'fft', or 'music'.
        Default is 'music'.
    **kwargs : dict
        Additional processing parameters.

    Returns
    -------
    dataObj : musicArray or None
        Processed data object, or None if processing failed.

    Raises
    ------
    ValueError
        If radar code is invalid or dates are out of order.
    FileNotFoundError
        If required fitacf files are missing.

    Examples
    --------
    >>> import mstid
    >>> import datetime
    >>> dataObj = mstid.run_music(
    ...     radar='bks',
    ...     sTime=datetime.datetime(2015, 1, 1, 14, 0),
    ...     eTime=datetime.datetime(2015, 1, 1, 16, 0),
    ...     process_level='music'
    ... )
    """
    # Implementation here
```

### Type Hints

Use type hints for new code:

```python
from typing import Optional, List, Dict
import datetime

def create_event_list(
    radar: str,
    sDate: datetime.datetime,
    eDate: datetime.datetime,
    slt_range: Optional[List[float]] = None
) -> Dict[str, any]:
    """Create event list with type-safe parameters."""
    ...
```

---

## Testing

### Writing Tests

Create tests in `tests/` directory:

```python
# tests/test_mongo_tools.py
import unittest
import datetime
from mstid.mongo_tools import generate_mongo_list

class TestMongoTools(unittest.TestCase):

    def test_generate_mongo_list(self):
        """Test event list generation."""
        result = generate_mongo_list(
            radar='bks',
            sDate=datetime.datetime(2015, 1, 1),
            eDate=datetime.datetime(2015, 1, 2),
            db_name='test_db'
        )
        self.assertIsNotNone(result)
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests/test_mongo_tools.py

# Run with coverage
pip install pytest pytest-cov
pytest --cov=mstid tests/
```

---

## Documentation

### Code Documentation

- **All public functions** must have docstrings
- **Complex algorithms** should have inline comments explaining logic
- **Configuration parameters** should be documented in `docs/configuration.md`

### User Documentation

When adding features:

1. Update relevant docs in `docs/`
2. Add examples to `docs/examples.md`
3. Update `README.md` if adding major features
4. Add usage examples in docstrings

### Building Documentation

```bash
# Install Sphinx (future)
pip install sphinx sphinx-rtd-theme

# Build HTML docs
cd docs/
make html
```

---

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Tests pass (when available)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Closes #(issue number)

## Changes Made
- Item 1
- Item 2

## Testing
How were these changes tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Commit messages are clear
```

### Review Process

1. **Automated Checks**: CI/CD will run tests (when implemented)
2. **Code Review**: Maintainer will review code
3. **Revisions**: Address feedback from reviewers
4. **Approval**: Once approved, PR will be merged

---

## Areas for Contribution

### High Priority

- **Unit Tests**: Add comprehensive test coverage
- **Documentation**: Expand examples and tutorials
- **Performance**: Optimize MUSIC algorithm
- **Error Handling**: Improve error messages and logging

### Feature Ideas

- **Automated Quality Control**: Machine learning for event classification
- **Real-Time Processing**: Stream processing for recent data
- **Interactive Visualization**: Web-based event browser
- **Cross-Radar Analysis**: Automated multi-radar correlation
- **Export Formats**: NetCDF, CSV output options

### Documentation Needs

- Video tutorials for new users
- Jupyter notebook examples
- API reference with Sphinx
- Troubleshooting guide

---

## Communication

### Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: nathaniel.frissell@scranton.edu for direct contact

### Asking Questions

When asking questions:

1. Check existing issues and documentation first
2. Provide context and code examples
3. Include error messages and logs
4. Describe expected vs. actual behavior

---

## Recognition

Contributors will be:

- Listed in `README.md` contributors section
- Acknowledged in release notes
- Credited in scientific publications using contributed code (when applicable)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Additional Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [NumPy Docstring Guide](https://numpydoc.readthedocs.io/)
- [Git Workflow Tutorial](https://guides.github.com/introduction/flow/)
- [SuperDARN Documentation](http://vt.superdarn.org/)

---

Thank you for contributing to DARNtids! Your efforts help advance ionospheric research.
