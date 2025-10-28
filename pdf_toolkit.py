#!/usr/bin/env python3
"""
PDF Toolkit - Unified tool for PDF conversion and OCR processing
Combines PDF to Image PDF conversion and Google Drive OCR functionality.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict
import io
import fnmatch
import datetime


# PDF to Image PDF dependencies
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import img2pdf
    PDF_TO_IMAGE_AVAILABLE = True
except ImportError:
    PDF_TO_IMAGE_AVAILABLE = False

# Google Drive OCR dependencies
try:
    import httplib2
    from apiclient import discovery
    from apiclient.http import MediaFileUpload, MediaIoBaseDownload
    from oauth2client import file as oauth_file, client
    from oauth2client import tools as oauth_tools
    from PyPDF2 import PdfReader, PdfWriter
    GOOGLE_OCR_AVAILABLE = True
except ImportError:
    GOOGLE_OCR_AVAILABLE = False


# Constants
SCOPES = "https://www.googleapis.com/auth/drive"
DEFAULT_DPI = 200  # High DPI for better OCR quality
DEFAULT_JPEG_QUALITY = 95  # High quality for better OCR
PAGES_PER_CHUNK = 10
AUTO_CONVERT_TO_IMAGE = True  # Automatically convert to image PDF before OCR
MIME_TYPES = {
    "pdf": 'application/pdf',
    "jpg": 'image/jpeg',
    "jpeg": 'image/jpeg',
    "png": 'image/png',
    "gif": 'image/gif',
    "bmp": 'image/bmp',
    "doc": 'application/msword'
}


class PDFToImageConverter:
    """Handles conversion of text-based PDFs to image-based PDFs"""

    def __init__(self, dpi: int = DEFAULT_DPI, jpeg_quality: int = DEFAULT_JPEG_QUALITY):
        """
        Initialize the PDF to Image converter.

        Args:
            dpi: Resolution for image conversion
            jpeg_quality: JPEG compression quality (1-100)
        """
        if not PDF_TO_IMAGE_AVAILABLE:
            raise ImportError(
                "PDF to Image conversion requires: pdf2image, pillow, img2pdf\n"
                "Install with: pip install pdf2image pillow img2pdf\n"
                "Note: pdf2image requires poppler-utils:\n"
                "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                "  macOS: brew install poppler\n"
                "  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/"
            )
        self.dpi = dpi
        self.jpeg_quality = jpeg_quality

    def convert(self, input_pdf: Path, output_pdf: Optional[Path] = None) -> Path:
        """
        Convert a text-based PDF to an image-based PDF.

        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path to output PDF file (auto-generated if None)

        Returns:
            Path to the created output PDF

        Raises:
            FileNotFoundError: If input PDF doesn't exist
            Exception: For conversion errors
        """
        input_path = Path(input_pdf)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_pdf}")

        if output_pdf is None:
            output_path = input_path.parent / f"{input_path.stem}_image.pdf"
        else:
            output_path = Path(output_pdf)

        print(f"Converting: {input_path.name}")
        print(f"Output: {output_path.name}")
        print(f"Resolution: {self.dpi} DPI")

        try:
            # Convert PDF pages to images
            images = convert_from_path(str(input_path), dpi=self.dpi)
            print(f"Converted {len(images)} page(s) to images")

            # Convert images to bytes
            image_bytes_list = []
            for i, img in enumerate(images, 1):
                print(f"Processing page {i}/{len(images)}...", end='\r')

                # Ensure compatible color mode
                if img.mode not in ('RGB', 'RGBA', 'L', 'P', 'CMYK'):
                    img = img.convert('RGB')

                # Save to in-memory buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=self.jpeg_quality)
                image_bytes_list.append(img_buffer.getvalue())

            print(f"\nCreating image-based PDF...")

            # Write final PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_bytes_list))

            # Show file size comparison
            input_size = input_path.stat().st_size / (1024 * 1024)
            output_size = output_path.stat().st_size / (1024 * 1024)

            print(f"\nConversion complete!")
            print(f"Input size: {input_size:.2f} MB")
            print(f"Output size: {output_size:.2f} MB")
            print(f"Saved to: {output_path}")

            return output_path

        except Exception as e:
            # Clean up partial output
            if output_path.exists():
                os.remove(output_path)
                print(f"Cleaned up partial output: {output_path}")
            raise Exception(f"Conversion failed: {str(e)}")


class GoogleDriveOCR:
    """Handles OCR processing using Google Drive API"""

    def __init__(self, credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json',
                 pages_per_chunk: int = PAGES_PER_CHUNK):
        """
        Initialize Google Drive OCR processor.

        Args:
            credentials_path: Path to Google credentials JSON
            token_path: Path to store OAuth token
            pages_per_chunk: Number of pages per PDF chunk
        """
        if not GOOGLE_OCR_AVAILABLE:
            raise ImportError(
                "Google Drive OCR requires: google-api-python-client, oauth2client, PyPDF2\n"
                "Install with: pip install google-api-python-client oauth2client PyPDF2"
            )

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.pages_per_chunk = pages_per_chunk
        self.service = None

    def authenticate(self):
        """Authenticate with Google Drive API"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}\n"
                "Please download credentials.json from Google Cloud Console"
            )

        store = oauth_file.Storage(self.token_path)
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(self.credentials_path, SCOPES)
            flow.params['access_type'] = 'offline'
            flow.params['approval_prompt'] = 'force'
            # Use run_flow with empty flags to avoid argparse conflicts
            import argparse
            flags = argparse.Namespace(
                logging_level='ERROR',
                noauth_local_webserver=False,
                auth_host_name='localhost',
                auth_host_port=[8080, 8090]
            )
            creds = oauth_tools.run_flow(flow, store, flags)
            store.put(creds)

        # Refresh token if expiring soon
        if creds.token_expiry:
            days_until_expiry = (creds.token_expiry - datetime.datetime.utcnow()).days
            if days_until_expiry < 7:
                creds.refresh(httplib2.Http())
                store.put(creds)

        http = creds.authorize(httplib2.Http())
        self.service = discovery.build("drive", "v3", http=http)
        print("Authenticated with Google Drive API")

    def split_pdf(self, input_pdf: Path) -> List[Path]:
        """
        Split PDF into smaller chunks.

        Args:
            input_pdf: Path to PDF file

        Returns:
            List of chunk file paths
        """
        print(f"Splitting {input_pdf.name} into {self.pages_per_chunk}-page chunks...")

        reader = PdfReader(str(input_pdf))
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        chunk_files = []
        num_chunks = (total_pages + self.pages_per_chunk - 1) // self.pages_per_chunk

        for chunk_num in range(num_chunks):
            start_page = chunk_num * self.pages_per_chunk
            end_page = min(start_page + self.pages_per_chunk, total_pages)

            writer = PdfWriter()
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            chunk_path = input_pdf.parent / f"{input_pdf.stem}_chunk_{chunk_num + 1}.pdf"
            with open(chunk_path, 'wb') as output_file:
                writer.write(output_file)

            chunk_files.append(chunk_path)
            print(f"Created chunk {chunk_num + 1}/{num_chunks}: {chunk_path.name} "
                  f"(pages {start_page + 1}-{end_page})")

        return chunk_files

    def ocr_file(self, input_file: Path, output_file: Path, file_type: str):
        """
        Perform OCR on a single file using Google Drive.

        Args:
            input_file: Path to input file
            output_file: Path to save OCR text
            file_type: File type (pdf, jpg, png, etc.)
        """
        if self.service is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        mime_type = MIME_TYPES.get(file_type.lower())
        if mime_type is None:
            raise ValueError(f"Unsupported file type: {file_type}")

        file_metadata = {
            'name': input_file.name,
            'mimeType': 'application/vnd.google-apps.document'
        }

        # Upload to Google Drive
        media = MediaFileUpload(str(input_file), mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')
        print(f'Uploaded to Drive (ID: {file_id})')

        # Export as text
        request = self.service.files().export_media(fileId=file_id, mimeType="text/plain")
        with io.FileIO(str(output_file), "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        # Clean up from Drive
        self.service.files().delete(fileId=file_id).execute()
        print(f"OCR complete: {output_file.name}")

    def ocr_pdf_chunked(self, pdf_path: Path, output_path: Optional[Path] = None,
                       keep_chunks: bool = False, delete_original: bool = False,
                       auto_convert: bool = AUTO_CONVERT_TO_IMAGE,
                       dpi: int = DEFAULT_DPI, jpeg_quality: int = DEFAULT_JPEG_QUALITY) -> Path:
        """
        Process a PDF by optionally converting to image PDF, splitting into chunks, and performing OCR.

        Args:
            pdf_path: Path to PDF file
            output_path: Path for final text output (auto-generated if None)
            keep_chunks: Keep intermediate chunk files
            delete_original: Delete original PDF after processing
            auto_convert: Automatically convert to high-quality image PDF before OCR
            dpi: DPI for image conversion (if auto_convert is True)
            jpeg_quality: JPEG quality for image conversion (if auto_convert is True)

        Returns:
            Path to final text output
        """
        if self.service is None:
            self.authenticate()

        # Create processing folder for this PDF
        processing_folder = pdf_path.parent / f"{pdf_path.stem}_processing"
        processing_folder.mkdir(exist_ok=True)
        print(f"Created processing folder: {processing_folder.name}")

        # If output path not specified, place it in the processing folder
        if output_path is None:
            output_path = processing_folder / f"{pdf_path.stem}_ocr_text.txt"

        # Automatically convert to high-quality image PDF before OCR
        pdf_to_process = pdf_path
        if auto_convert and PDF_TO_IMAGE_AVAILABLE:
            print(f"\nConverting PDF to high-quality image PDF for better OCR...")
            converter = PDFToImageConverter(dpi=dpi, jpeg_quality=jpeg_quality)
            image_pdf_path = processing_folder / f"{pdf_path.stem}_image.pdf"
            try:
                pdf_to_process = converter.convert(pdf_path, image_pdf_path)
                print(f"Image PDF created: {image_pdf_path.name}")
            except Exception as e:
                print(f"Warning: Could not convert to image PDF: {e}")
                print("Proceeding with original PDF...")
                pdf_to_process = pdf_path

        # Split PDF into chunks (chunks go into processing folder)
        chunk_files = self.split_pdf_to_folder(pdf_to_process, processing_folder)

        # Process each chunk
        text_files = []
        for chunk_file in chunk_files:
            chunk_output = chunk_file.with_suffix('.txt')
            print(f"\nProcessing {chunk_file.name}...")
            self.ocr_file(chunk_file, chunk_output, 'pdf')
            text_files.append(chunk_output)

        # Combine all text files
        print(f"\nCombining chunks into {output_path.name}...")
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for i, text_file in enumerate(text_files, 1):
                with open(text_file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    if i < len(text_files):
                        outfile.write("\n\n" + "="*50 + f" Chunk {i} End " + "="*50 + "\n\n")

                # Clean up text file
                if not keep_chunks:
                    os.remove(text_file)

        # Clean up chunk PDFs
        if not keep_chunks:
            for chunk_file in chunk_files:
                os.remove(chunk_file)
                print(f"Deleted chunk: {chunk_file.name}")

        # Optionally delete original
        if delete_original:
            os.remove(pdf_path)
            print(f"Deleted original: {pdf_path.name}")

        print(f"\nFinal OCR output saved to: {output_path}")
        print(f"All files organized in: {processing_folder}")
        return output_path

    def split_pdf_to_folder(self, input_pdf: Path, output_folder: Path) -> List[Path]:
        """
        Split PDF into smaller chunks and save to specified folder.

        Args:
            input_pdf: Path to PDF file
            output_folder: Folder to save chunks

        Returns:
            List of chunk file paths
        """
        print(f"Splitting {input_pdf.name} into {self.pages_per_chunk}-page chunks...")

        reader = PdfReader(str(input_pdf))
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        chunk_files = []
        num_chunks = (total_pages + self.pages_per_chunk - 1) // self.pages_per_chunk

        for chunk_num in range(num_chunks):
            start_page = chunk_num * self.pages_per_chunk
            end_page = min(start_page + self.pages_per_chunk, total_pages)

            writer = PdfWriter()
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            chunk_path = output_folder / f"{input_pdf.stem}_chunk_{chunk_num + 1}.pdf"
            with open(chunk_path, 'wb') as output_file:
                writer.write(output_file)

            chunk_files.append(chunk_path)
            print(f"Created chunk {chunk_num + 1}/{num_chunks}: {chunk_path.name} "
                  f"(pages {start_page + 1}-{end_page})")

        return chunk_files

    def scan_and_process_directory(self, directory: Path = Path('.'),
                                   file_types: Optional[List[str]] = None,
                                   auto_convert: bool = AUTO_CONVERT_TO_IMAGE,
                                   dpi: int = DEFAULT_DPI,
                                   jpeg_quality: int = DEFAULT_JPEG_QUALITY):
        """
        Scan directory for files and process them with OCR using organized batch folders.

        Args:
            directory: Directory to scan
            file_types: List of file extensions to process (None = all supported)
            auto_convert: Automatically convert PDFs to image PDFs before OCR
            dpi: DPI for image conversion
            jpeg_quality: JPEG quality for image conversion
        """
        if self.service is None:
            self.authenticate()

        if file_types is None:
            file_types = list(MIME_TYPES.keys())

        # Create batch processing folder
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        batch_folder = directory / f"batch_processing_{timestamp}"
        batch_folder.mkdir(exist_ok=True)
        print(f"\nCreated batch processing folder: {batch_folder.name}")

        # Organize files by type
        files_by_type: Dict[str, List[Path]] = {ft: [] for ft in file_types}

        for file_path in directory.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lstrip('.').lower()
                if ext in files_by_type:
                    files_by_type[ext].append(file_path)

        # Display found files
        print("\nFiles found:")
        for file_type, files in files_by_type.items():
            if files:
                print(f"  {file_type.upper()}: {len(files)} file(s)")

        # Process PDFs with chunking
        if files_by_type.get("pdf"):
            print("\n" + "="*60)
            print("Processing PDF files with automatic conversion and chunking")
            print("="*60)
            for pdf_path in files_by_type["pdf"]:
                print(f"\nProcessing: {pdf_path.name}")

                # Create individual folder for this PDF within batch folder
                pdf_folder = batch_folder / pdf_path.stem
                pdf_folder.mkdir(exist_ok=True)

                # Process with output in the PDF's folder
                output_path = pdf_folder / f"{pdf_path.stem}_ocr_text.txt"

                # Copy original to PDF folder for reference
                import shutil
                original_copy = pdf_folder / pdf_path.name
                shutil.copy2(pdf_path, original_copy)

                # Process the PDF (creates its own processing subfolder)
                self.ocr_pdf_chunked(original_copy, output_path, keep_chunks=False,
                                    auto_convert=auto_convert, dpi=dpi, jpeg_quality=jpeg_quality)

        # Process other file types
        for file_type in [ft for ft in file_types if ft != "pdf"]:
            if files_by_type.get(file_type):
                print(f"\nProcessing {file_type.upper()} files...")

                # Create folder for this file type
                type_folder = batch_folder / f"{file_type}_files"
                type_folder.mkdir(exist_ok=True)

                for input_path in files_by_type[file_type]:
                    # Create individual folder for each file
                    file_folder = type_folder / input_path.stem
                    file_folder.mkdir(exist_ok=True)

                    # Copy original
                    import shutil
                    original_copy = file_folder / input_path.name
                    shutil.copy2(input_path, original_copy)

                    output_path = file_folder / f"{input_path.stem}_ocr_text.txt"
                    print(f"Converting: {input_path.name}")
                    self.ocr_file(original_copy, output_path, file_type)

        print("\n" + "="*60)
        print("All conversions complete!")
        print(f"Results organized in: {batch_folder}")
        print("="*60)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='PDF Toolkit - Convert PDFs to images or perform OCR processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF to image-based PDF
  python pdf_toolkit.py convert input.pdf -o output.pdf --dpi 150

  # Perform OCR on a single PDF
  python pdf_toolkit.py ocr input.pdf -o output.txt

  # Scan directory and OCR all supported files
  python pdf_toolkit.py ocr-batch --dir ./pdfs

  # Convert with custom settings
  python pdf_toolkit.py convert input.pdf --dpi 200 --quality 90
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Convert command
    convert_parser = subparsers.add_parser('convert',
                                          help='Convert PDF to image-based PDF')
    convert_parser.add_argument('input', type=str, help='Input PDF file')
    convert_parser.add_argument('-o', '--output', type=str,
                               help='Output PDF file (default: <input>_image.pdf)')
    convert_parser.add_argument('--dpi', type=int, default=DEFAULT_DPI,
                               help=f'Resolution in DPI (default: {DEFAULT_DPI})')
    convert_parser.add_argument('--quality', type=int, default=DEFAULT_JPEG_QUALITY,
                               help=f'JPEG quality 1-100 (default: {DEFAULT_JPEG_QUALITY})')

    # OCR command
    ocr_parser = subparsers.add_parser('ocr',
                                      help='Perform OCR on a single file')
    ocr_parser.add_argument('input', type=str, help='Input file (PDF, JPG, PNG, etc.)')
    ocr_parser.add_argument('-o', '--output', type=str,
                           help='Output text file (default: <input>_ocr_text.txt)')
    ocr_parser.add_argument('--credentials', type=str, default='credentials.json',
                           help='Google credentials file (default: credentials.json)')
    ocr_parser.add_argument('--token', type=str, default='token.json',
                           help='OAuth token file (default: token.json)')
    ocr_parser.add_argument('--chunk-size', type=int, default=PAGES_PER_CHUNK,
                           help=f'Pages per chunk for PDFs (default: {PAGES_PER_CHUNK})')
    ocr_parser.add_argument('--keep-chunks', action='store_true',
                           help='Keep intermediate chunk files')
    ocr_parser.add_argument('--delete-original', action='store_true',
                           help='Delete original file after processing')
    ocr_parser.add_argument('--no-convert', action='store_true',
                           help='Skip automatic conversion to image PDF (process original PDF directly)')
    ocr_parser.add_argument('--dpi', type=int, default=DEFAULT_DPI,
                           help=f'DPI for image conversion (default: {DEFAULT_DPI}, only if converting)')
    ocr_parser.add_argument('--quality', type=int, default=DEFAULT_JPEG_QUALITY,
                           help=f'JPEG quality for image conversion (default: {DEFAULT_JPEG_QUALITY}, only if converting)')

    # OCR batch command
    batch_parser = subparsers.add_parser('ocr-batch',
                                        help='Scan directory and OCR all files')
    batch_parser.add_argument('--dir', type=str, default='.',
                             help='Directory to scan (default: current directory)')
    batch_parser.add_argument('--credentials', type=str, default='credentials.json',
                             help='Google credentials file (default: credentials.json)')
    batch_parser.add_argument('--token', type=str, default='token.json',
                             help='OAuth token file (default: token.json)')
    batch_parser.add_argument('--chunk-size', type=int, default=PAGES_PER_CHUNK,
                             help=f'Pages per chunk for PDFs (default: {PAGES_PER_CHUNK})')
    batch_parser.add_argument('--types', nargs='+',
                             help='File types to process (default: all supported)')
    batch_parser.add_argument('--no-convert', action='store_true',
                             help='Skip automatic conversion to image PDF (process original PDFs directly)')
    batch_parser.add_argument('--dpi', type=int, default=DEFAULT_DPI,
                             help=f'DPI for image conversion (default: {DEFAULT_DPI}, only if converting)')
    batch_parser.add_argument('--quality', type=int, default=DEFAULT_JPEG_QUALITY,
                             help=f'JPEG quality for image conversion (default: {DEFAULT_JPEG_QUALITY}, only if converting)')

    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'convert':
            # PDF to Image conversion
            converter = PDFToImageConverter(dpi=args.dpi, jpeg_quality=args.quality)
            input_path = Path(args.input)
            output_path = Path(args.output) if args.output else None
            converter.convert(input_path, output_path)

        elif args.command == 'ocr':
            # Single file OCR
            ocr_processor = GoogleDriveOCR(
                credentials_path=args.credentials,
                token_path=args.token,
                pages_per_chunk=args.chunk_size
            )
            ocr_processor.authenticate()

            input_path = Path(args.input)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {args.input}")

            output_path = Path(args.output) if args.output else None
            file_ext = input_path.suffix.lstrip('.').lower()

            if file_ext == 'pdf':
                ocr_processor.ocr_pdf_chunked(
                    input_path,
                    output_path,
                    keep_chunks=args.keep_chunks,
                    delete_original=args.delete_original,
                    auto_convert=not args.no_convert,
                    dpi=args.dpi,
                    jpeg_quality=args.quality
                )
            else:
                if output_path is None:
                    output_path = input_path.parent / f"{input_path.stem}_ocr_text.txt"
                ocr_processor.ocr_file(input_path, output_path, file_ext)

        elif args.command == 'ocr-batch':
            # Batch directory OCR
            ocr_processor = GoogleDriveOCR(
                credentials_path=args.credentials,
                token_path=args.token,
                pages_per_chunk=args.chunk_size
            )
            directory = Path(args.dir)
            if not directory.is_dir():
                raise NotADirectoryError(f"Not a directory: {args.dir}")

            ocr_processor.scan_and_process_directory(
                directory,
                args.types,
                auto_convert=not args.no_convert,
                dpi=args.dpi,
                jpeg_quality=args.quality
            )

        print("\nOperation completed successfully!")

    except ImportError as e:
        print(f"\nError: Missing dependencies\n{str(e)}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
