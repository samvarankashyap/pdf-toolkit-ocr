# PDF Toolkit - Complete Setup Guide

This guide will help you set up the PDF Toolkit repository from scratch, whether for development or deployment.

## Table of Contents

- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Repository Structure](#repository-structure)
- [Git Configuration](#git-configuration)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Quick Start

### For Users

```bash
# Clone the repository
git clone https://github.com/samvarankashyap/pdf-toolkit-ocr.git
cd pdf-toolkit-ocr

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
pytest test_pdf_toolkit.py -v

# Use the tool
python pdf_toolkit.py --help
```

### For Developers

```bash
# Clone and setup
git clone https://github.com/samvarankashyap/pdf-toolkit-ocr.git
cd pdf-toolkit-ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest test_pdf_toolkit.py -v --cov=pdf_toolkit

# Start developing!
```

## Detailed Setup

### Prerequisites

#### Required Software

1. **Python 3.8+**
   ```bash
   # Check Python version
   python --version
   ```

2. **Git**
   ```bash
   # Check Git version
   git --version
   ```

3. **poppler-utils** (for PDF processing)

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install poppler-utils
   ```

   **macOS:**
   ```bash
   brew install poppler
   ```

   **Windows:**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract and add to PATH

#### Optional Software

- **Google Cloud Account** (for OCR functionality)
- **Code Editor** (VS Code, PyCharm, etc.)
- **Docker** (for containerized deployment)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
# Via HTTPS
git clone https://github.com/samvarankashyap/pdf-toolkit-ocr.git

# Via SSH (recommended for contributors)
git clone git@github.com:samvarankashyap/pdf-toolkit-ocr.git

cd pdf-toolkit-ocr
```

#### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
# Linux/macOS
source venv/bin/activate

# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies

```bash
# For users (minimal installation)
pip install -r requirements.txt

# For developers (includes testing and linting tools)
pip install -r requirements-dev.txt

# For package installation
pip install -e .  # Editable install
```

#### 4. Verify Installation

```bash
# Run tests
pytest test_pdf_toolkit.py -v

# Check coverage
pytest test_pdf_toolkit.py --cov=pdf_toolkit --cov-report=html

# Test CLI
python pdf_toolkit.py --help
```

## Repository Structure

```
pdf-toolkit-ocr/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
│       ├── tests.yml        # Automated testing
│       ├── lint.yml         # Code quality checks
│       └── release.yml      # Release automation
│
├── venv/                    # Virtual environment (not in git)
├── htmlcov/                 # Coverage reports (not in git)
│
├── pdf_toolkit.py           # Main application
├── test_pdf_toolkit.py      # Test suite
│
├── .gitignore               # Git ignore rules
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml           # Modern Python config
├── setup.py                 # Package setup
├── MANIFEST.in              # Package manifest
│
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
│
├── README.md                # User documentation
├── SETUP_GUIDE.md           # This file
├── CONTRIBUTING.md          # Contribution guidelines
├── CHANGELOG.md             # Version history
├── TEST_DOCUMENTATION.md    # Testing guide
├── LICENSE                  # MIT License
│
├── run_tests.sh             # Unix test runner
└── run_tests.bat            # Windows test runner
```

## Git Configuration

### Initial Setup

```bash
# Configure Git user
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Enable colored output
git config --global color.ui auto
```

### Working with Remotes

```bash
# View remotes
git remote -v

# Add remote (if not already added)
git remote add origin https://github.com/samvarankashyap/pdf-toolkit-ocr.git

# Push initial commit
git push -u origin main
```

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Create bugfix branch
git checkout -b fix/bug-description

# Create development branch
git checkout -b develop
```

## Development Workflow

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify pre-commit setup
pre-commit run --all-files
```

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit:

- **trailing-whitespace**: Remove trailing spaces
- **end-of-file-fixer**: Ensure files end with newline
- **black**: Format Python code
- **isort**: Sort imports
- **flake8**: Lint code
- **mypy**: Type checking
- **bandit**: Security checks

### Running Tests

```bash
# Run all tests
pytest test_pdf_toolkit.py -v

# Run specific test class
pytest test_pdf_toolkit.py::TestPDFToImageConverter -v

# Run with coverage
pytest test_pdf_toolkit.py --cov=pdf_toolkit --cov-report=html

# Run in parallel (faster)
pytest test_pdf_toolkit.py -n auto

# Run with verbose output
pytest test_pdf_toolkit.py -vv -s
```

### Code Quality Checks

```bash
# Format code
black pdf_toolkit.py test_pdf_toolkit.py

# Sort imports
isort pdf_toolkit.py test_pdf_toolkit.py

# Lint
flake8 pdf_toolkit.py test_pdf_toolkit.py

# Type check
mypy pdf_toolkit.py --ignore-missing-imports

# Security check
bandit pdf_toolkit.py
```

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Run tests
pytest test_pdf_toolkit.py -v

# 4. Stage changes
git add .

# 5. Commit (pre-commit hooks run automatically)
git commit -m "feat: Add new feature"

# 6. Push to remote
git push origin feature/my-feature

# 7. Create Pull Request on GitHub
```

### Commit Message Format

Use conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
perf: Performance improvement
chore: Maintenance tasks
```

## Deployment

### Installing as Package

```bash
# Install from source
pip install .

# Install in editable mode (for development)
pip install -e .

# Install with extras
pip install .[dev]
pip install .[docs]
```

### Using as Command-Line Tool

```bash
# After installation, use as command
pdf-toolkit convert input.pdf
pdf-toolkit ocr input.pdf
pdf-toolkit ocr-batch --dir ./documents
```

### Building Distribution

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (requires account)
twine upload dist/*
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY pdf_toolkit.py .

# Set entrypoint
ENTRYPOINT ["python", "pdf_toolkit.py"]
```

Build and run:

```bash
# Build image
docker build -t pdf-toolkit .

# Run container
docker run -v $(pwd):/data pdf-toolkit convert /data/input.pdf
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Problem: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 2. Poppler Not Found

```bash
# Problem: pdf2image can't find poppler
# Solution: Install poppler and add to PATH

# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from https://github.com/oschwartz10612/poppler-windows/releases/
# Add bin/ directory to PATH
```

#### 3. Google Drive Authentication Errors

```bash
# Problem: credentials.json not found
# Solution: Download credentials from Google Cloud Console
# Place in project root as credentials.json
```

#### 4. Test Failures

```bash
# Problem: Tests fail
# Solution: Ensure all dependencies installed
pip install -r requirements-dev.txt

# Run with verbose output
pytest test_pdf_toolkit.py -vv
```

#### 5. Pre-commit Hook Failures

```bash
# Problem: Pre-commit hooks fail
# Solution: Install hooks and run manually
pre-commit install
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Getting Help

1. **Check Documentation**: Read [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Search Issues**: Look for similar issues on GitHub
3. **Create Issue**: Open new issue with details
4. **Ask Community**: Join discussions

## Next Steps

After setup:

1. **Read Documentation**: Familiarize yourself with [README.md](README.md)
2. **Run Examples**: Try example commands
3. **Explore Code**: Review [pdf_toolkit.py](pdf_toolkit.py)
4. **Run Tests**: Verify everything works
5. **Start Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Resources

- **Documentation**: [README.md](README.md)
- **Testing Guide**: [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **License**: [LICENSE](LICENSE)

---

**Happy Coding! 🚀**
