# PDF Toolkit - Test Documentation

## Overview

Comprehensive unit and integration tests for [pdf_toolkit.py](pdf_toolkit.py) with **74% code coverage** and **39 passing tests**.

## Test Coverage Summary

```
Name             Stmts   Miss  Cover   Missing
----------------------------------------------
pdf_toolkit.py     329     86    74%
----------------------------------------------
TOTAL              329     86    74%
```

## Running Tests

### Prerequisites

Install testing dependencies:

```bash
pip install pytest pytest-cov coverage
```

### Run All Tests

```bash
# Run tests with coverage report
python -m pytest test_pdf_toolkit.py -v --cov=pdf_toolkit --cov-report=html --cov-report=term-missing

# Or run directly with unittest
python test_pdf_toolkit.py
```

### View HTML Coverage Report

After running tests, open the HTML coverage report:

```bash
# Coverage report is generated in htmlcov/index.html
# Open in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Structure

### Test Classes

#### 1. TestConstants (2 tests)
Tests module-level constants and configuration.

- ✅ `test_constants_exist` - Verify all required constants are defined
- ✅ `test_mime_types_complete` - Verify MIME types dictionary is complete

#### 2. TestPDFToImageConverter (8 tests)
Tests PDF to image PDF conversion functionality.

- ✅ `test_init_without_dependencies` - Missing dependencies error handling
- ✅ `test_init_with_default_params` - Default DPI and quality initialization
- ✅ `test_init_with_custom_params` - Custom DPI and quality initialization
- ✅ `test_convert_file_not_found` - File not found error handling
- ✅ `test_convert_success` - Successful PDF conversion
- ✅ `test_convert_with_image_mode_conversion` - Image mode handling
- ✅ `test_convert_cleanup_on_failure` - Cleanup on conversion failure
- ✅ `test_convert_custom_output_path` - Custom output path handling

#### 3. TestGoogleDriveOCR (11 tests)
Tests Google Drive OCR functionality.

- ✅ `test_init_without_dependencies` - Missing dependencies error handling
- ✅ `test_init_with_defaults` - Default parameter initialization
- ✅ `test_init_with_custom_params` - Custom parameter initialization
- ✅ `test_authenticate_missing_credentials` - Missing credentials error
- ✅ `test_authenticate_new_credentials` - New credentials authentication flow
- ✅ `test_split_pdf` - PDF splitting into chunks
- ✅ `test_split_pdf_to_folder` - PDF splitting to specific folder
- ✅ `test_ocr_file_unsupported_type` - Unsupported file type handling
- ✅ `test_ocr_file_not_authenticated` - Unauthenticated error handling
- ✅ `test_ocr_file_success` - Successful file OCR
- ✅ `test_ocr_pdf_chunked_creates_folder` - Processing folder creation

#### 4. TestArgumentParser (8 tests)
Tests command-line argument parsing.

- ✅ `test_parser_creation` - Parser instantiation
- ✅ `test_convert_command` - Convert command parsing
- ✅ `test_convert_command_with_options` - Convert with all options
- ✅ `test_ocr_command` - OCR command parsing
- ✅ `test_ocr_command_with_all_options` - OCR with all options
- ✅ `test_ocr_batch_command` - Batch OCR command parsing
- ✅ `test_ocr_batch_with_options` - Batch OCR with options
- ✅ `test_no_command_provided` - No command handling

#### 5. TestMainFunction (5 tests)
Tests main function and CLI integration.

- ✅ `test_main_no_command` - No command prints help
- ✅ `test_main_convert_command` - Convert command execution
- ✅ `test_main_ocr_without_image_deps` - OCR without image dependencies
- ✅ `test_main_file_not_found` - File not found error handling
- ✅ `test_main_missing_dependencies` - Missing dependencies handling

#### 6. TestEdgeCases (4 tests)
Tests edge cases and boundary conditions.

- ✅ `test_split_pdf_single_page` - Single-page PDF splitting
- ✅ `test_split_pdf_exact_chunk_size` - Exact chunk size handling
- ✅ `test_convert_empty_pdf` - Empty PDF conversion
- ✅ `test_ocr_with_special_characters_in_filename` - Special characters in filenames

#### 7. TestIntegration (1 test)
End-to-end integration tests.

- ✅ `test_full_convert_then_ocr_workflow` - Complete convert→OCR workflow

## Code Coverage Details

### Covered Areas (74%)

1. **PDFToImageConverter Class** - Nearly 100% coverage
   - Initialization with various parameters
   - PDF conversion with different image modes
   - Error handling and cleanup
   - File size reporting

2. **GoogleDriveOCR Class** - ~70% coverage
   - Authentication flow
   - PDF splitting (both methods)
   - OCR file processing
   - Folder creation and organization

3. **Argument Parsing** - 100% coverage
   - All three commands (convert, ocr, ocr-batch)
   - All command-line options
   - Default values

4. **Main Function** - ~60% coverage
   - Command routing
   - Error handling
   - Basic integration flows

### Uncovered Areas (26%)

The following areas have limited or no test coverage (intentional for now):

1. **Batch Processing Directory Scanning** (lines 433-511)
   - `scan_and_process_directory()` method
   - Timestamp-based folder creation
   - File type organization
   - Batch OCR workflow

   *Reason*: Requires complex mocking of filesystem operations and Google Drive API

2. **Auto-Convert Feature** (lines 326-338)
   - Automatic PDF to image conversion before OCR
   - Fallback to original PDF on conversion failure

   *Reason*: Requires integration of both PDFToImageConverter and GoogleDriveOCR with real file operations

3. **Chunk File Combination** (lines 346-363, 368-374)
   - Text file reading and combining
   - Chunk separator insertion
   - File cleanup

   *Reason*: Requires mocking file I/O operations

4. **Deprecated API Warnings** (lines 23-24, 35-36)
   - Import error handling branches

   *Reason*: Test environment has all dependencies installed

## Test Categories

### Unit Tests
Tests individual functions and methods in isolation:
- Constants verification
- Class initialization
- Argument parsing
- Error handling

### Integration Tests
Tests interaction between components:
- Convert then OCR workflow
- Main function command routing
- File operations

### Mock Objects
Extensive use of mocking for external dependencies:
- `pdf2image.convert_from_path`
- `img2pdf.convert`
- `PyPDF2.PdfReader/PdfWriter`
- Google Drive API services
- File I/O operations

## Example Test Cases

### Testing PDF Conversion

```python
@patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
@patch('pdf_toolkit.convert_from_path')
@patch('pdf_toolkit.img2pdf.convert')
def test_convert_success(self, mock_img2pdf, mock_convert_from_path):
    """Test successful PDF to image conversion"""
    # Setup
    test_pdf = Path(self.temp_dir) / "test.pdf"
    test_pdf.touch()

    mock_image = MagicMock()
    mock_image.mode = 'RGB'
    mock_convert_from_path.return_value = [mock_image]
    mock_img2pdf.return_value = b'fake pdf bytes'

    # Execute
    converter = PDFToImageConverter(dpi=200, jpeg_quality=95)
    output_path = converter.convert(test_pdf)

    # Verify
    self.assertTrue(output_path.exists())
    self.assertTrue(output_path.name.endswith('_image.pdf'))
```

### Testing Error Handling

```python
@patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
def test_convert_file_not_found(self):
    """Test conversion fails when input file doesn't exist"""
    converter = PDFToImageConverter()
    non_existent = Path(self.temp_dir) / "nonexistent.pdf"

    with self.assertRaises(FileNotFoundError) as context:
        converter.convert(non_existent)
    self.assertIn("Input file not found", str(context.exception))
```

### Testing CLI Arguments

```python
def test_ocr_command_with_all_options(self):
    """Test OCR command with all options"""
    parser = create_parser()
    args = parser.parse_args([
        'ocr', 'input.pdf',
        '-o', 'output.txt',
        '--chunk-size', '20',
        '--no-convert',
        '--dpi', '150'
    ])

    self.assertEqual(args.output, 'output.txt')
    self.assertEqual(args.chunk_size, 20)
    self.assertTrue(args.no_convert)
    self.assertEqual(args.dpi, 150)
```

## Continuous Integration

### Recommended CI Configuration

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov coverage
          pip install google-api-python-client oauth2client PyPDF2
      - name: Run tests
        run: pytest test_pdf_toolkit.py -v --cov=pdf_toolkit --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Future Testing Improvements

### Increase Coverage to 85%+

1. **Add Batch Processing Tests**
   - Mock directory scanning
   - Test timestamp folder creation
   - Verify file organization by type

2. **Add Auto-Convert Integration Tests**
   - Test successful auto-conversion
   - Test fallback on conversion failure
   - Verify DPI and quality settings

3. **Add File I/O Tests**
   - Test chunk combination
   - Test separator insertion
   - Test cleanup operations

4. **Add Performance Tests**
   - Large PDF processing
   - Memory usage monitoring
   - Processing time benchmarks

### Additional Test Types

1. **Regression Tests**
   - Add tests for known bugs
   - Prevent future regressions

2. **Stress Tests**
   - Very large PDFs (1000+ pages)
   - Very small PDFs (1 page)
   - Unusual file formats

3. **Security Tests**
   - Path traversal attacks
   - Malformed PDFs
   - Invalid credentials handling

## Testing Best Practices Used

✅ **Isolation**: Each test is independent with its own temp directory
✅ **Mocking**: External dependencies are mocked to avoid API calls
✅ **Cleanup**: Temp files and directories are cleaned up after each test
✅ **Descriptive Names**: Test names clearly describe what is being tested
✅ **Arrange-Act-Assert**: Tests follow AAA pattern
✅ **Edge Cases**: Boundary conditions and error cases are tested
✅ **Coverage Tracking**: HTML and terminal coverage reports generated

## Known Test Warnings

1. **PyPDF2 Deprecation**: PyPDF2 is deprecated, consider migrating to pypdf
2. **datetime.utcnow()**: Should use timezone-aware datetime objects

These warnings don't affect functionality but should be addressed in future updates.

## Running Specific Test Classes

```bash
# Run only PDFToImageConverter tests
pytest test_pdf_toolkit.py::TestPDFToImageConverter -v

# Run only a specific test
pytest test_pdf_toolkit.py::TestPDFToImageConverter::test_convert_success -v

# Run with verbose output and show print statements
pytest test_pdf_toolkit.py -v -s
```

## Test Execution Time

Total test execution time: **~1.5-2 seconds**
- Fast unit tests: ~0.5s
- Integration tests: ~1s
- Coverage calculation: ~0.5s

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Aim for >80% coverage for new code
3. Include both success and failure cases
4. Add edge case tests
5. Update this documentation

## License

Tests are provided as-is for quality assurance of the pdf_toolkit.py module.
