# Installing Poppler on Windows

Poppler is required for the `pdf2image` library to convert PDFs to images. Follow these steps to install and configure Poppler on Windows.

## Option 1: Manual Installation (Recommended)

### Step 1: Download Poppler

1. Visit the latest release page:
   - https://github.com/oschwartz10612/poppler-windows/releases/latest

2. Download the **Release-25.07.0-0.zip** (or latest version)
   - Look for the file that says "Release-XX.XX.X-X.zip"
   - This contains pre-built binaries for Windows

### Step 2: Extract to Permanent Location

1. Extract the downloaded ZIP file to a permanent location:
   ```
   C:\Program Files\poppler-25.07.0
   ```

   Or if you don't have admin rights:
   ```
   C:\Users\samva\poppler-25.07.0
   ```

2. After extraction, you should have a folder structure like:
   ```
   C:\Program Files\poppler-25.07.0\
   ├── Library\
   │   └── bin\        <- This contains the executables
   │       ├── pdfinfo.exe
   │       ├── pdfimages.exe
   │       ├── pdftoppm.exe  <- Used by pdf2image
   │       └── ... (other tools)
   └── ...
   ```

### Step 3: Add to Windows PATH

#### Method A: Using System Properties (GUI)

1. **Open System Properties**:
   - Press `Win + R`
   - Type `sysdm.cpl` and press Enter
   - Or: Right-click "This PC" → Properties → Advanced system settings

2. **Edit Environment Variables**:
   - Click "Environment Variables" button
   - Under "System variables" (or "User variables" if no admin rights)
   - Find and select "Path"
   - Click "Edit"

3. **Add Poppler Path**:
   - Click "New"
   - Add: `C:\Program Files\poppler-25.07.0\Library\bin`
   - Click "OK" on all windows

4. **Restart your terminal** or IDE for changes to take effect

#### Method B: Using PowerShell (Current User Only)

```powershell
# Run this in PowerShell (as Administrator for system-wide, or normal for user-only)
$popplerPath = "C:\Program Files\poppler-25.07.0\Library\bin"

# Add to User PATH (no admin required)
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";$popplerPath",
    "User"
)
```

#### Method C: Using Command Prompt (System-wide, requires Admin)

```cmd
setx /M PATH "%PATH%;C:\Program Files\poppler-25.07.0\Library\bin"
```

### Step 4: Verify Installation

1. **Close and reopen your terminal/PowerShell/CMD**

2. **Test the installation**:
   ```bash
   pdftoppm -v
   ```

   You should see output like:
   ```
   pdftoppm version 25.07.0
   ```

3. **Test with Python**:
   ```bash
   python -c "from pdf2image import convert_from_path; print('pdf2image can find poppler!')"
   ```

## Option 2: Using Chocolatey (Package Manager)

If you have Chocolatey installed:

```powershell
choco install poppler
```

This automatically handles PATH configuration.

## Option 3: Using winget (Windows Package Manager)

If you have winget (Windows 10 1809+ or Windows 11):

```powershell
winget install oschwartz10612.Poppler
```

## Troubleshooting

### Issue: "Unable to find pdftoppm"

**Solution**: Ensure the PATH includes the `bin` folder specifically:
- NOT: `C:\Program Files\poppler-25.07.0`
- BUT: `C:\Program Files\poppler-25.07.0\Library\bin`

### Issue: PATH not updating

**Solution**:
1. Close ALL terminal windows and IDE instances
2. Reopen and test again
3. If still not working, restart your computer

### Issue: Permission denied when adding to System PATH

**Solution**:
- Use "User variables" instead of "System variables"
- Or run PowerShell/CMD as Administrator

### Issue: pdf2image still can't find poppler

**Solution**: Specify poppler path directly in code:

```python
from pdf2image import convert_from_path

# Windows
poppler_path = r"C:\Program Files\poppler-25.07.0\Library\bin"
images = convert_from_path('document.pdf', poppler_path=poppler_path)
```

Or set in `pdf_toolkit.py`:
```python
# Add at the top of pdf_toolkit.py
import os
POPPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin"

# Then in PDFToImageConverter.convert() method:
images = convert_from_path(
    str(input_path),
    dpi=self.dpi,
    poppler_path=POPPLER_PATH  # Add this parameter
)
```

## Quick Verification Commands

After installation, verify with these commands:

```bash
# Check if pdftoppm is accessible
where pdftoppm

# Check version
pdftoppm -v

# Check pdfinfo (another poppler tool)
pdfinfo -v

# Test with your virtual environment activated
cd c:\Users\samva\OneDrive\Desktop\telugu_ocr
venv\Scripts\activate
python -c "from pdf2image import convert_from_path; print('Success!')"
```

## Next Steps

Once Poppler is installed and verified:

1. Activate your virtual environment:
   ```bash
   cd c:\Users\samva\OneDrive\Desktop\telugu_ocr
   venv\Scripts\activate
   ```

2. Test the PDF toolkit:
   ```bash
   python pdf_toolkit.py convert test.pdf test_output.pdf --dpi 200
   ```

## Additional Resources

- Poppler Windows GitHub: https://github.com/oschwartz10612/poppler-windows
- pdf2image documentation: https://github.com/Belval/pdf2image
- Poppler official site: https://poppler.freedesktop.org/
