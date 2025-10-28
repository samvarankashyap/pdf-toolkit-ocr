#!/usr/bin/env python3
"""
Setup script for PDF Toolkit
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="pdf-toolkit-ocr",
    version="1.0.0",
    author="Samvaran Kashyap",
    author_email="samvarankashyap@users.noreply.github.com",
    description="Unified tool for PDF to Image conversion and Google Drive OCR processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samvarankashyap/pdf-toolkit-ocr",
    py_modules=["pdf_toolkit"],
    python_requires=">=3.10",
    install_requires=[
        "pdf2image>=1.17.0",
        "Pillow>=12.0.0",
        "img2pdf>=0.6.1",
        "google-api-python-client>=2.185.0",
        "oauth2client>=4.1.3",
        "PyPDF2>=3.0.1",
        "packaging>=25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.2",
            "pytest-cov>=7.0.0",
            "coverage>=7.11.0",
            "black>=24.10.0",
            "flake8>=7.1.1",
            "mypy>=1.13.0",
            "pylint>=3.3.1",
        ],
        "docs": [
            "sphinx>=8.1.3",
            "sphinx-rtd-theme>=3.0.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-toolkit=pdf_toolkit:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Telugu",
    ],
    keywords="pdf ocr telugu google-drive image-conversion document-processing",
    project_urls={
        "Bug Reports": "https://github.com/samvarankashyap/pdf-toolkit-ocr/issues",
        "Source": "https://github.com/samvarankashyap/pdf-toolkit-ocr",
        "Documentation": "https://github.com/samvarankashyap/pdf-toolkit-ocr/blob/main/README.md",
    },
)
