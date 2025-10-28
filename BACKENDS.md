# PDF Rendering Backends Guide

PDF Toolkit now supports **multiple PDF rendering backends**, giving you flexibility to choose the best option for your needs without external dependencies like Poppler.

## Available Backends

### 1. pypdfium2 (RECOMMENDED) ⭐

**Status:** Default choice, auto-selected if available

**Advantages:**
- ✅ No external dependencies (fully self-contained)
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ MIT License (permissive, commercial-friendly)
- ✅ Good performance
- ✅ Uses Google's PDFium library
- ✅ Easy installation

**Installation:**
```bash
pip install pypdfium2
```

**When to use:**
- **Recommended for most users**
- When you want easy, hassle-free setup
- When you need a permissive license
- For Windows users (no Poppler installation needed!)

---

### 2. PyMuPDF (fitz)

**Status:** Available as alternative

**Advantages:**
- ✅ Very fast performance (often fastest option)
- ✅ No external dependencies
- ✅ Rich feature set
- ✅ Cross-platform

**Disadvantages:**
- ⚠️ AGPL License (copyleft, requires source disclosure)

**Installation:**
```bash
pip install PyMuPDF
```

**When to use:**
- When you need maximum performance
- For open-source projects compatible with AGPL
- When processing large batches of PDFs

---

### 3. pdf2image + Poppler

**Status:** Legacy option (previously required)

**Advantages:**
- ✅ Mature and stable
- ✅ Wide community support

**Disadvantages:**
- ❌ Requires external Poppler installation
- ❌ Complex setup on Windows
- ❌ Additional system dependencies

**Installation:**
```bash
pip install pdf2image

# Plus Poppler system installation:
# Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
# Ubuntu: sudo apt-get install poppler-utils
# macOS: brew install poppler
```

**When to use:**
- When you already have Poppler installed
- For legacy compatibility
- When other backends don't work in your environment

---

## Quick Start

### Automatic Backend Selection

PDF Toolkit automatically selects the best available backend:

```bash
# Auto-selects pypdfium2, then PyMuPDF, then pdf2image
python pdf_toolkit.py convert input.pdf output.pdf
```

Priority order:
1. pypdfium2 (if installed)
2. PyMuPDF (if installed)
3. pdf2image (if installed + Poppler available)

### Manual Backend Selection

You can explicitly choose a backend:

```bash
# Use pypdfium2
python pdf_toolkit.py convert input.pdf output.pdf --backend pypdfium2

# Use PyMuPDF
python pdf_toolkit.py convert input.pdf output.pdf --backend pymupdf

# Use pdf2image (requires Poppler)
python pdf_toolkit.py convert input.pdf output.pdf --backend pdf2image
```

Works with all commands:
```bash
# OCR with specific backend
python pdf_toolkit.py ocr document.pdf -o output.txt --backend pypdfium2

# Batch processing with specific backend
python pdf_toolkit.py ocr-batch --dir ./pdfs --backend pymupdf
```

---

## Installation Scenarios

### Scenario 1: Easy Setup (Recommended)

**For most users, especially Windows:**

```bash
pip install pypdfium2 pillow img2pdf
```

✅ No system dependencies needed!

### Scenario 2: Maximum Performance

**If you need the fastest processing:**

```bash
pip install PyMuPDF pillow img2pdf
```

⚠️ Note: AGPL license applies

### Scenario 3: Multiple Options

**Install multiple backends for flexibility:**

```bash
pip install pypdfium2 PyMuPDF pillow img2pdf
```

The tool will use pypdfium2 by default, but you can override with `--backend`.

### Scenario 4: Legacy Setup

**If you already have Poppler:**

```bash
pip install pdf2image pillow img2pdf
```

Plus ensure Poppler is in your PATH.

---

## Comparison Table

| Feature | pypdfium2 | PyMuPDF | pdf2image |
|---------|-----------|---------|-----------|
| External Dependencies | None | None | Poppler |
| License | MIT | AGPL | MIT |
| Performance | Good | Excellent | Good |
| Windows Setup | Easy | Easy | Complex |
| Installation Size | ~3 MB | ~10 MB | ~1 MB + Poppler (~15 MB) |
| Recommended For | General use | Speed-critical | Legacy systems |

---

## Troubleshooting

### Check Available Backends

```bash
python -c "from pdf_toolkit import PYPDFIUM2_AVAILABLE, PYMUPDF_AVAILABLE, PDF2IMAGE_AVAILABLE; print(f'pypdfium2: {PYPDFIUM2_AVAILABLE}'); print(f'PyMuPDF: {PYMUPDF_AVAILABLE}'); print(f'pdf2image: {PDF2IMAGE_AVAILABLE}')"
```

Or run our test script:
```bash
python test_backend.py
```

### Error: "No PDF rendering backend available"

**Solution:** Install at least one backend:

```bash
# Easiest option:
pip install pypdfium2

# Or choose another:
pip install PyMuPDF
# or
pip install pdf2image  # + install Poppler separately
```

### Error: "Backend 'X' not available"

**Solution:** Either:
1. Install the requested backend: `pip install pypdfium2` (or `PyMuPDF`, or `pdf2image`)
2. Or omit `--backend` flag to auto-select available backend

### pdf2image Error: "Unable to find pdftoppm"

**Solution:** This means Poppler is not installed or not in PATH.

**Options:**
1. **Switch to pypdfium2** (recommended):
   ```bash
   pip install pypdfium2
   # No Poppler needed!
   ```

2. Or install Poppler:
   - Windows: See [POPPLER_INSTALLATION_WINDOWS.md](POPPLER_INSTALLATION_WINDOWS.md)
   - Ubuntu: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

---

## Performance Comparison

Based on community benchmarks:

**Converting 100-page PDF at 200 DPI:**

| Backend | Time | Notes |
|---------|------|-------|
| PyMuPDF | ~25s | Fastest |
| pypdfium2 | ~30s | Slightly slower, but good |
| pdf2image | ~35s | Depends on Poppler version |

*Results vary by document complexity and system specs.*

---

## License Considerations

### For Commercial/Proprietary Projects

✅ **Use pypdfium2** - MIT license allows commercial use without source disclosure

⚠️ **Avoid PyMuPDF** - AGPL requires you to open-source your entire application

✅ **pdf2image OK** - MIT license, but Poppler is GPL (dynamic linking exception applies)

### For Open Source Projects

✅ All backends are suitable

PyMuPDF might be preferred for performance if AGPL is compatible with your project license.

---

## Migration Guide

### From pdf2image to pypdfium2

**Old code (pdf2image):**
```python
from pdf2image import convert_from_path
images = convert_from_path('document.pdf', dpi=200)
```

**New code (auto-select, prefers pypdfium2):**
```python
from pdf_toolkit import PDFToImageConverter
converter = PDFToImageConverter(dpi=200)
converter.convert('document.pdf', 'output.pdf')
```

**Command line:**
```bash
# Old way (required Poppler):
# Had to install Poppler separately first

# New way (no Poppler needed):
pip install pypdfium2  # One time
python pdf_toolkit.py convert document.pdf output.pdf
```

---

## API Examples

### Python API

```python
from pdf_toolkit import PDFToImageConverter
from pathlib import Path

# Auto-select best backend
converter = PDFToImageConverter(dpi=200, jpeg_quality=95)
output = converter.convert(Path('input.pdf'), Path('output.pdf'))

# Explicitly use pypdfium2
converter = PDFToImageConverter(dpi=200, backend='pypdfium2')
output = converter.convert(Path('input.pdf'), Path('output.pdf'))

# Explicitly use PyMuPDF
converter = PDFToImageConverter(dpi=200, backend='pymupdf')
output = converter.convert(Path('input.pdf'), Path('output.pdf'))
```

### Command Line

```bash
# Convert with auto-selected backend
python pdf_toolkit.py convert input.pdf output.pdf --dpi 200 --quality 95

# Convert with specific backend
python pdf_toolkit.py convert input.pdf output.pdf --backend pypdfium2 --dpi 200

# OCR with specific backend
python pdf_toolkit.py ocr document.pdf -o text.txt --backend pypdfium2

# Batch OCR with specific backend
python pdf_toolkit.py ocr-batch --dir ./documents --backend pymupdf --dpi 300
```

---

## FAQ

**Q: Which backend should I choose?**

A: For most users: **pypdfium2**. It's easy to install, has no external dependencies, and has a permissive license.

**Q: Can I install multiple backends?**

A: Yes! Install all three and switch between them using `--backend` flag as needed.

**Q: Is pypdfium2 as accurate as pdf2image/Poppler?**

A: Yes. pypdfium2 uses Google's PDFium, which is the same PDF rendering engine used in Google Chrome.

**Q: Why was pdf2image the default before?**

A: pypdfium2 is relatively new to Python. pdf2image was the standard for years, but required Poppler installation which was complex on Windows.

**Q: Can I uninstall Poppler now?**

A: Yes, if you switch to pypdfium2 or PyMuPDF, you no longer need Poppler.

**Q: Does this affect OCR quality?**

A: No. All backends render PDFs to images with the same DPI and quality settings. OCR quality depends on the image resolution, not the rendering backend.

---

## Summary

🎯 **Recommendation:** Install pypdfium2 for the easiest, most hassle-free experience:

```bash
pip install pypdfium2 pillow img2pdf google-api-python-client oauth2client PyPDF2 packaging
```

Then use the tool without worrying about external dependencies:

```bash
python pdf_toolkit.py convert document.pdf output.pdf
python pdf_toolkit.py ocr document.pdf -o text.txt
```

No Poppler installation required! 🎉
