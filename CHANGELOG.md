# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add batch processing with progress bars
- Support for additional image formats (TIFF, WebP)
- Parallel processing for large PDFs
- GUI interface option
- Docker container support

## [1.0.0] - 2025-10-28

### Added
- Initial release of unified PDF Toolkit
- PDF to high-quality image PDF conversion
  - Configurable DPI (default: 200)
  - Configurable JPEG quality (default: 95%)
  - Automatic output path generation
- Google Drive OCR integration
  - Automatic authentication flow
  - Token refresh mechanism
  - PDF chunking support (default: 10 pages/chunk)
- Automatic PDF to image conversion before OCR
  - Enabled by default for best accuracy
  - `--no-convert` flag to skip conversion
  - Custom DPI and quality settings
- Organized folder structure for outputs
  - Individual processing folders per PDF
  - Timestamped batch processing folders
  - Automatic cleanup of intermediate files
- Command-line interface with argparse
  - `convert` command for PDF to image conversion
  - `ocr` command for single file OCR
  - `ocr-batch` command for directory processing
- Comprehensive test suite
  - 39 unit and integration tests
  - 74% code coverage
  - pytest and coverage.py integration
- Documentation
  - Complete README with examples
  - Test documentation
  - Contributing guidelines
  - API documentation in docstrings
- GitHub Actions workflows
  - Automated testing on push/PR
  - Multi-OS and multi-Python version testing
  - Code quality checks (linting, formatting)
  - Automated release creation

### Features
- Support for multiple file formats: PDF, JPG, JPEG, PNG, GIF, BMP, DOC
- Automatic chunk cleanup after processing
- File size reporting for conversions
- Progress feedback during operations
- Error handling with helpful messages
- Cross-platform compatibility (Windows, Linux, macOS)

### Technical Details
- Python 3.8+ support
- Type hints throughout codebase
- Modular class-based architecture
  - `PDFToImageConverter` for image conversion
  - `GoogleDriveOCR` for OCR processing
- Extensive use of pathlib for cross-platform paths
- Mocked tests for external dependencies

## [0.2.0] - 2025-10-27 (Pre-release)

### Added
- Separated original scripts into modular classes
- Added automatic image conversion feature
- Created organized folder structure

### Changed
- Improved error handling
- Enhanced progress feedback
- Updated default DPI from 120 to 200
- Updated default quality from 85% to 95%

## [0.1.0] - 2025-10-26 (Initial)

### Added
- Original `truepdf_to_imagepdf.py` script
- Original `telugu_ocr_processor.py` script
- Basic PDF to image conversion
- Basic Google Drive OCR processing

---

## Version History

### Types of Changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

### Links
- [Unreleased]: https://github.com/samvarankashyap/pdf-toolkit-ocr/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/samvarankashyap/pdf-toolkit-ocr/releases/tag/v1.0.0
- [0.2.0]: https://github.com/samvarankashyap/pdf-toolkit-ocr/releases/tag/v0.2.0
- [0.1.0]: https://github.com/samvarankashyap/pdf-toolkit-ocr/releases/tag/v0.1.0
