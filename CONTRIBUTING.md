# Contributing to PDF Toolkit

Thank you for your interest in contributing to PDF Toolkit! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/samvarankashyap/pdf-toolkit-ocr.git
   cd pdf-toolkit-ocr
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/pdf-toolkit-ocr.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- poppler-utils (for PDF processing)

### Setting Up Development Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv venv

   # Activate (Windows)
   venv\Scripts\activate

   # Activate (Linux/macOS)
   source venv/bin/activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install the package in editable mode**:
   ```bash
   pip install -e .
   ```

4. **Verify installation**:
   ```bash
   python -m pytest test_pdf_toolkit.py -v
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**
- **New features**
- **Documentation improvements**
- **Test coverage improvements**
- **Code refactoring**
- **Performance optimizations**

### Contribution Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following our coding standards

3. **Write or update tests** for your changes

4. **Run tests** to ensure everything works:
   ```bash
   pytest test_pdf_toolkit.py -v --cov=pdf_toolkit
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: Maximum 127 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized with `isort`
- **Formatting**: Use `black` for consistent formatting

### Code Formatting

Before submitting, format your code:

```bash
# Format with black
black pdf_toolkit.py test_pdf_toolkit.py

# Sort imports
isort pdf_toolkit.py test_pdf_toolkit.py

# Check with flake8
flake8 pdf_toolkit.py test_pdf_toolkit.py --max-line-length=127
```

### Type Hints

Use type hints for function parameters and return values:

```python
def convert_pdf(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """Convert PDF with proper type hints"""
    pass
```

### Documentation

- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain "why", not "what"
- **README updates**: Update documentation for new features

Example docstring:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
    pass
```

## Testing Guidelines

### Writing Tests

1. **Test coverage**: Aim for >80% coverage for new code
2. **Test isolation**: Each test should be independent
3. **Descriptive names**: Use clear test method names
4. **AAA pattern**: Arrange, Act, Assert

Example test:

```python
def test_convert_pdf_with_custom_dpi(self):
    """Test PDF conversion with custom DPI setting"""
    # Arrange
    converter = PDFToImageConverter(dpi=200)
    test_pdf = Path("test.pdf")

    # Act
    output = converter.convert(test_pdf)

    # Assert
    self.assertTrue(output.exists())
    self.assertEqual(converter.dpi, 200)
```

### Running Tests

```bash
# Run all tests
pytest test_pdf_toolkit.py -v

# Run specific test class
pytest test_pdf_toolkit.py::TestPDFToImageConverter -v

# Run with coverage
pytest test_pdf_toolkit.py --cov=pdf_toolkit --cov-report=html

# Run in parallel
pytest test_pdf_toolkit.py -n auto
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** for any new features
2. **Add tests** for bug fixes and new features
3. **Update CHANGELOG.md** with your changes
4. **Ensure all tests pass** on your branch
5. **Request review** from maintainers

### Pull Request Title Format

Use conventional commit format:

- `feat: Add new OCR batch processing feature`
- `fix: Resolve PDF chunking issue`
- `docs: Update README with new examples`
- `test: Add tests for edge cases`
- `refactor: Improve error handling`
- `perf: Optimize image conversion`

### Pull Request Description

Include:

- **What**: What changes did you make?
- **Why**: Why were these changes necessary?
- **How**: How did you implement the changes?
- **Testing**: How did you test the changes?
- **Screenshots**: If applicable, add screenshots

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Collect information** about your environment

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With input file '...'
3. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Windows 10, Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Package version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Who would benefit and how?

**Proposed Solution**
Your suggested implementation approach

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Mock-ups, examples, or references
```

## Development Tips

### Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Profiling

```bash
# Profile code execution
python -m cProfile -o profile.stats pdf_toolkit.py convert test.pdf

# View profile results
python -m pstats profile.stats
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Profile memory usage
python -m memory_profiler pdf_toolkit.py
```

## Release Process

For maintainers:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will create release automatically

## Questions?

- **Documentation**: Check [README.md](README.md) and [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)
- **Discussions**: Start a discussion on GitHub
- **Email**: Contact maintainers directly

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PDF Toolkit! 🎉
