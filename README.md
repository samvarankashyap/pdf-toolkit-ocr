# PDF Toolkit

A unified command-line tool that combines PDF to Image conversion and Google Drive OCR functionality. Perfect for processing Telugu and other language PDFs.

## Features

### 1. Multiple PDF Rendering Backends 🆕
- **No Poppler installation required!** (when using pypdfium2 or PyMuPDF)
- Choose from 3 backends: pypdfium2 (recommended), PyMuPDF, or pdf2image
- Auto-selects best available backend
- See [BACKENDS.md](BACKENDS.md) for detailed comparison

### 2. PDF to Image PDF Conversion
- Converts text-based PDFs to high-quality image-based PDFs
- Configurable DPI (default: 200) and JPEG quality (default: 95)
- Useful for PDFs with text extraction/copy-paste issues
- Automatic file size reporting

### 3. Google Drive OCR Processing with Automatic Image Conversion
- **Automatically converts PDFs to high-quality image PDFs before OCR for better accuracy**
- Performs OCR using Google Drive API
- Automatic PDF chunking for large files (default: 10 pages per chunk)
- Organized folder structure for all outputs
- Batch processing with timestamped folders
- Support for PDF, JPG, PNG, GIF, BMP, and DOC files

### 4. Organized Output Structure
- Each PDF gets its own processing folder: `<filename>_processing/`
- Batch operations create timestamped folders: `batch_processing_YYYYMMDD_HHMMSS/`
- All intermediate files (chunks, converted PDFs) organized in dedicated folders
- Final OCR text output clearly labeled and easy to find

## Installation

### Quick Start (Recommended)

**No external dependencies needed with pypdfium2!**

```bash
# Install with pypdfium2 backend (easiest, no Poppler needed)
pip install pypdfium2 pillow img2pdf google-api-python-client oauth2client PyPDF2 packaging

# Or install from requirements.txt
pip install -r requirements.txt
```

### Alternative Backends

**Option 1: pypdfium2 (Recommended)** ⭐
```bash
pip install pypdfium2 pillow img2pdf
```
- No system dependencies
- Works on Windows without Poppler
- MIT license

**Option 2: PyMuPDF (Fastest)**
```bash
pip install PyMuPDF pillow img2pdf
```
- Very fast performance
- No system dependencies
- AGPL license (requires source disclosure)

**Option 3: pdf2image (Legacy)**
```bash
pip install pdf2image pillow img2pdf
```
Plus system dependencies:

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install poppler-utils
  ```

- **macOS:**
  ```bash
  brew install poppler
  ```

- **Windows:**
  Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH.

### Google Drive API Setup

For OCR functionality, you need Google Drive API credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download credentials and save as `credentials.json` in the project directory

## Usage

### Command Structure

```bash
python pdf_toolkit.py <command> [options]
```

### Commands

#### 1. Convert PDF to Image PDF (Manual Conversion Only)

Convert a text-based PDF to an image-based PDF without OCR:

```bash
# Basic conversion (auto-selects best backend, 200 DPI, 95% quality)
python pdf_toolkit.py convert input.pdf

# Specify output file
python pdf_toolkit.py convert input.pdf -o output.pdf

# Use specific backend
python pdf_toolkit.py convert input.pdf --backend pypdfium2
python pdf_toolkit.py convert input.pdf --backend pymupdf
python pdf_toolkit.py convert input.pdf --backend pdf2image

# Custom DPI and quality
python pdf_toolkit.py convert input.pdf --dpi 150 --quality 85

# Full example with all options
python pdf_toolkit.py convert telugu_book.pdf -o telugu_image.pdf --backend pypdfium2 --dpi 200 --quality 95
```

**Options:**
- `-o, --output`: Output PDF file (default: `<input>_image.pdf`)
- `--dpi`: Resolution in DPI (default: 200)
- `--quality`: JPEG quality 1-100 (default: 95)
- `--backend`: PDF backend (pypdfium2/pymupdf/pdf2image, default: auto-select)

#### 2. OCR Single File (Automatic High-Quality Conversion + OCR)

**By default, PDFs are automatically converted to high-quality image PDFs (200 DPI, 95% quality) before OCR for best results.**

Perform OCR on a single file using Google Drive:

```bash
# OCR a PDF file (automatically converts to image PDF first)
python pdf_toolkit.py ocr input.pdf

# The tool will:
# 1. Create a processing folder: input_processing/
# 2. Convert PDF to high-quality image PDF (200 DPI)
# 3. Split into 10-page chunks
# 4. Perform OCR on each chunk
# 5. Combine results into input_ocr_text.txt
# 6. Clean up intermediate files

# Specify custom output location
python pdf_toolkit.py ocr input.pdf -o /path/to/output.txt

# OCR an image file (JPG, PNG, etc.)
python pdf_toolkit.py ocr document.jpg

# Custom chunk size for large PDFs
python pdf_toolkit.py ocr large.pdf --chunk-size 20

# Keep all intermediate chunk files for inspection
python pdf_toolkit.py ocr input.pdf --keep-chunks
```

**Options:**
- `-o, --output`: Output text file (default: `<input>_processing/<input>_ocr_text.txt`)
- `--credentials`: Google credentials file (default: `credentials.json`)
- `--token`: OAuth token file (default: `token.json`)
- `--chunk-size`: Pages per chunk for PDFs (default: 10)
- `--keep-chunks`: Keep intermediate chunk files
- `--delete-original`: Delete original file after processing
- `--no-convert`: **Skip automatic image PDF conversion** and process original PDF directly
- `--dpi`: DPI for image conversion (default: 200, only used if converting)
- `--quality`: JPEG quality 1-100 for conversion (default: 95, only used if converting)

**Output Structure for Single File:**
```
input.pdf
input_processing/
  ├── input.pdf (copy of original)
  ├── input_image.pdf (high-quality converted PDF)
  ├── input_image_chunk_1.pdf
  ├── input_image_chunk_2.pdf
  ├── ... (temporary chunks, deleted unless --keep-chunks)
  └── input_ocr_text.txt (final OCR output)
```

#### 3. Batch OCR Directory (Organized Batch Processing)

Scan a directory and OCR all supported files with organized folder structure:

```bash
# Process all files in current directory
python pdf_toolkit.py ocr-batch

# Process specific directory
python pdf_toolkit.py ocr-batch --dir ./my_pdfs

# Process only specific file types
python pdf_toolkit.py ocr-batch --types pdf jpg png

# Custom chunk size
python pdf_toolkit.py ocr-batch --chunk-size 15
```

**Options:**
- `--dir`: Directory to scan (default: current directory)
- `--credentials`: Google credentials file (default: `credentials.json`)
- `--token`: OAuth token file (default: `token.json`)
- `--chunk-size`: Pages per chunk for PDFs (default: 10)
- `--types`: File types to process (default: all supported)
- `--no-convert`: **Skip automatic image PDF conversion** and process original PDFs directly
- `--dpi`: DPI for image conversion (default: 200, only used if converting)
- `--quality`: JPEG quality 1-100 for conversion (default: 95, only used if converting)

**Output Structure for Batch Processing:**
```
./my_pdfs/
  ├── file1.pdf
  ├── file2.pdf
  ├── document.jpg
  └── batch_processing_20250228_143022/
      ├── file1/
      │   ├── file1.pdf (original copy)
      │   ├── file1_processing/
      │   │   ├── file1_image.pdf
      │   │   └── file1_ocr_text.txt
      ├── file2/
      │   ├── file2.pdf (original copy)
      │   ├── file2_processing/
      │   │   ├── file2_image.pdf
      │   │   └── file2_ocr_text.txt
      └── jpg_files/
          └── document/
              ├── document.jpg (original copy)
              └── document_ocr_text.txt
```

## Examples

### Example 1: Convert Telugu PDF to Image PDF

```bash
# Convert with high quality settings
python pdf_toolkit.py convert telugu_document.pdf --dpi 200 --quality 95
```

This creates `telugu_document_image.pdf` with high-resolution images.

### Example 2: OCR a Large PDF (with automatic conversion)

```bash
# Process a large PDF with custom chunk size (default: converts to image PDF first)
python pdf_toolkit.py ocr large_telugu_book.pdf --chunk-size 20 -o book_text.txt
```

This converts to high-quality image PDF, splits into 20-page chunks, processes each, and combines results.

### Example 2b: OCR without Automatic Conversion

```bash
# Process PDF directly without converting to image PDF first (faster but may have lower accuracy)
python pdf_toolkit.py ocr document.pdf --no-convert
```

This skips the image conversion step and processes the original PDF directly.

### Example 3: Batch Process Multiple Files (with automatic conversion)

```bash
# Process all PDFs and images in a folder (default: converts PDFs to image PDFs first)
python pdf_toolkit.py ocr-batch --dir ./documents --types pdf jpg png
```

### Example 3b: Batch Process without Conversion (faster)

```bash
# Process multiple PDFs directly without image conversion
python pdf_toolkit.py ocr-batch --dir ./documents --no-convert
```

### Example 4: Custom Quality Settings

```bash
# OCR with custom DPI and quality settings
python pdf_toolkit.py ocr document.pdf --dpi 150 --quality 85
```

### Example 5: Complete Manual Workflow

```bash
# Step 1: Manually convert text-based PDF to image PDF
python pdf_toolkit.py convert original.pdf -o image_version.pdf --dpi 200

# Step 2: Perform OCR on the image PDF (skip auto-conversion since already converted)
python pdf_toolkit.py ocr image_version.pdf --no-convert -o extracted_text.txt
```

## When to Use --no-convert Flag

### Use `--no-convert` (skip image conversion) when:
- Your PDF is **already an image-based PDF**
- You want **faster processing** and file size is a concern
- You're processing **simple documents** with clear, machine-readable text
- Your source PDF is **high quality** and doesn't have font rendering issues

### Don't use `--no-convert` (use default auto-conversion) when:
- Processing **Telugu or complex script PDFs** with text extraction issues
- Your PDF has **font rendering problems** or copy-paste doesn't work correctly
- You need **maximum OCR accuracy** (image-based OCR often works better)
- Processing **scanned documents** or documents with unusual fonts
- The PDF has **text selection/copying issues**

### Performance vs. Quality Trade-off:
- **With auto-conversion (default)**: Slower but higher accuracy, especially for complex scripts
- **With --no-convert**: Faster processing but may have lower accuracy on problematic PDFs

## Code Improvements

The unified tool provides several optimizations over the original files:

### Modularization
- **Separation of Concerns**: Two main classes (`PDFToImageConverter`, `GoogleDriveOCR`)
- **Reusable Components**: Each function has a single, clear responsibility
- **Type Hints**: Better code documentation and IDE support

### Error Handling
- **Graceful Degradation**: Clear error messages for missing dependencies
- **Input Validation**: File existence and type checking
- **Cleanup on Failure**: Automatic removal of partial output files

### Performance
- **Efficient Memory Usage**: In-memory image buffers instead of temporary files
- **Batch Processing**: Optimized directory scanning
- **Smart Chunking**: Configurable PDF splitting for large files

### Usability
- **Unified CLI**: Single tool with subcommands using argparse
- **Flexible Options**: Configurable DPI, quality, chunk size, etc.
- **Progress Feedback**: Clear status messages throughout processing
- **Auto-generated Filenames**: Sensible defaults with override options

### Maintainability
- **Constants**: Centralized configuration values
- **Documentation**: Comprehensive docstrings
- **Clean Code**: PEP 8 compliant, readable structure
- **Path Handling**: Using `pathlib.Path` for cross-platform compatibility

## Troubleshooting

### PDF to Image Issues

**Error: "Poppler not found"**
- Install poppler-utils for your OS (see Installation section)
- On Windows, ensure poppler bin directory is in PATH

**Large output files**
- Reduce `--dpi` value (try 100 or 120)
- Reduce `--quality` value (try 75 or 80)

### Google Drive OCR Issues

**Error: "credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in project directory

**Token expired**
- Delete `token.json` and re-authenticate
- The tool will automatically refresh tokens within 7 days of expiry

**OCR fails on large PDFs**
- Reduce `--chunk-size` to process smaller chunks
- Check Google Drive API quota limits

## Supported File Types

- **PDF**: Portable Document Format
- **JPG/JPEG**: JPEG images
- **PNG**: Portable Network Graphics
- **GIF**: Graphics Interchange Format
- **BMP**: Bitmap images
- **DOC**: Microsoft Word documents

## Testing

The toolkit includes comprehensive unit and integration tests with **74% code coverage**.

### Run Tests

```bash
# Quick test run
python run_tests.bat  # Windows
bash run_tests.sh     # Linux/macOS

# Or manually
python -m pytest test_pdf_toolkit.py -v --cov=pdf_toolkit --cov-report=html
```

### Test Coverage

- **39 passing tests** covering all major functionality
- **74% code coverage** with detailed HTML reports
- Tests for PDF conversion, OCR, CLI arguments, error handling, and edge cases

See [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md) for detailed testing information.

## License

This tool is provided as-is for educational and personal use.

## Original Files

This unified tool replaces and improves upon:
- `truepdf_to_imagepdf.py` - PDF to Image conversion
- `telugu_ocr_processor.py` - Google Drive OCR processing

Both original files are preserved for reference.
