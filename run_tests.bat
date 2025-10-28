@echo off
REM Quick test runner for Windows
echo ========================================
echo Running PDF Toolkit Tests
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found
    echo Please run: python -m venv venv
)

echo.
echo Running tests with coverage...
echo.

python -m pytest test_pdf_toolkit.py -v --cov=pdf_toolkit --cov-report=html --cov-report=term-missing

echo.
echo ========================================
echo Test Results Summary
echo ========================================
echo HTML coverage report: htmlcov\index.html
echo.
echo To view coverage report, open: htmlcov\index.html
echo.

pause
