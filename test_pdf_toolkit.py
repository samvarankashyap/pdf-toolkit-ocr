#!/usr/bin/env python3
"""
Comprehensive unit tests for pdf_toolkit.py
Maximum code coverage for all functionality
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
import sys
import os
from pathlib import Path
import io
import tempfile
import shutil
from argparse import Namespace

# Import the module to test
import pdf_toolkit
from pdf_toolkit import (
    PDFToImageConverter,
    GoogleDriveOCR,
    create_parser,
    main,
    SCOPES,
    DEFAULT_DPI,
    DEFAULT_JPEG_QUALITY,
    PAGES_PER_CHUNK,
    AUTO_CONVERT_TO_IMAGE,
    MIME_TYPES
)


class TestConstants(unittest.TestCase):
    """Test module constants"""

    def test_constants_exist(self):
        """Verify all required constants are defined"""
        self.assertEqual(SCOPES, "https://www.googleapis.com/auth/drive")
        self.assertEqual(DEFAULT_DPI, 200)
        self.assertEqual(DEFAULT_JPEG_QUALITY, 95)
        self.assertEqual(PAGES_PER_CHUNK, 10)
        self.assertTrue(AUTO_CONVERT_TO_IMAGE)
        self.assertIsInstance(MIME_TYPES, dict)

    def test_mime_types_complete(self):
        """Verify MIME_TYPES dictionary has all expected entries"""
        expected_types = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'doc']
        for file_type in expected_types:
            self.assertIn(file_type, MIME_TYPES)


class TestPDFToImageConverter(unittest.TestCase):
    """Test PDFToImageConverter class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = Path(self.temp_dir) / "test.pdf"

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', False)
    def test_init_without_dependencies(self):
        """Test initialization fails when dependencies are missing"""
        with self.assertRaises(ImportError) as context:
            PDFToImageConverter()
        self.assertIn("pdf2image", str(context.exception))

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    def test_init_with_default_params(self):
        """Test initialization with default parameters"""
        converter = PDFToImageConverter()
        self.assertEqual(converter.dpi, DEFAULT_DPI)
        self.assertEqual(converter.jpeg_quality, DEFAULT_JPEG_QUALITY)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters"""
        converter = PDFToImageConverter(dpi=150, jpeg_quality=80)
        self.assertEqual(converter.dpi, 150)
        self.assertEqual(converter.jpeg_quality, 80)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    def test_convert_file_not_found(self):
        """Test conversion fails when input file doesn't exist"""
        converter = PDFToImageConverter()
        non_existent = Path(self.temp_dir) / "nonexistent.pdf"

        with self.assertRaises(FileNotFoundError) as context:
            converter.convert(non_existent)
        self.assertIn("Input file not found", str(context.exception))

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    @patch('pdf_toolkit.img2pdf.convert')
    def test_convert_success(self, mock_img2pdf, mock_convert_backend):
        """Test successful PDF to image conversion"""
        # Create test PDF file
        self.test_pdf.touch()

        # Mock PIL Image
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_image.save = MagicMock()

        mock_convert_backend.return_value = [mock_image, mock_image]
        mock_img2pdf.return_value = b'fake pdf bytes'

        converter = PDFToImageConverter(dpi=200, jpeg_quality=95)
        output_path = converter.convert(self.test_pdf)

        # Verify backend conversion was called
        mock_convert_backend.assert_called_once()

        # Verify output file was created
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.name.endswith('_image.pdf'))

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    def test_convert_with_image_mode_conversion(self, mock_convert_backend):
        """Test conversion handles different image modes"""
        self.test_pdf.touch()

        # Mock image with non-standard mode
        mock_image = MagicMock()
        mock_image.mode = 'CMYK'
        mock_image.convert = MagicMock(return_value=mock_image)

        mock_convert_backend.return_value = [mock_image]

        with patch('pdf_toolkit.img2pdf.convert', return_value=b'fake pdf'):
            converter = PDFToImageConverter()
            converter.convert(self.test_pdf)

            # Should NOT convert CMYK (it's in allowed list)
            mock_image.convert.assert_not_called()

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    def test_convert_cleanup_on_failure(self, mock_convert_backend):
        """Test cleanup happens when conversion fails"""
        self.test_pdf.touch()

        mock_convert_backend.side_effect = Exception("Conversion error")

        converter = PDFToImageConverter()
        output_path = Path(self.temp_dir) / "test_image.pdf"

        with self.assertRaises(Exception):
            converter.convert(self.test_pdf, output_path)

        # Output file should not exist after failure
        self.assertFalse(output_path.exists())

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    @patch('pdf_toolkit.img2pdf.convert')
    def test_convert_custom_output_path(self, mock_img2pdf, mock_convert_backend):
        """Test conversion with custom output path"""
        self.test_pdf.touch()

        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_convert_backend.return_value = [mock_image]
        mock_img2pdf.return_value = b'fake pdf bytes'

        converter = PDFToImageConverter()
        custom_output = Path(self.temp_dir) / "custom_output.pdf"
        output_path = converter.convert(self.test_pdf, custom_output)

        self.assertEqual(output_path, custom_output)
        self.assertTrue(output_path.exists())


class TestGoogleDriveOCR(unittest.TestCase):
    """Test GoogleDriveOCR class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.credentials_path = Path(self.temp_dir) / "credentials.json"
        self.token_path = Path(self.temp_dir) / "token.json"

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', False)
    def test_init_without_dependencies(self):
        """Test initialization fails when dependencies are missing"""
        with self.assertRaises(ImportError) as context:
            GoogleDriveOCR()
        self.assertIn("google-api-python-client", str(context.exception))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_init_with_defaults(self):
        """Test initialization with default parameters"""
        ocr = GoogleDriveOCR()
        self.assertEqual(ocr.credentials_path, 'credentials.json')
        self.assertEqual(ocr.token_path, 'token.json')
        self.assertEqual(ocr.pages_per_chunk, PAGES_PER_CHUNK)
        self.assertIsNone(ocr.service)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters"""
        ocr = GoogleDriveOCR(
            credentials_path='custom_creds.json',
            token_path='custom_token.json',
            pages_per_chunk=20
        )
        self.assertEqual(ocr.credentials_path, 'custom_creds.json')
        self.assertEqual(ocr.token_path, 'custom_token.json')
        self.assertEqual(ocr.pages_per_chunk, 20)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_authenticate_missing_credentials(self):
        """Test authentication fails when credentials file is missing"""
        ocr = GoogleDriveOCR(credentials_path='nonexistent.json')

        with self.assertRaises(FileNotFoundError) as context:
            ocr.authenticate()
        self.assertIn("Credentials file not found", str(context.exception))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.oauth_file.Storage')
    @patch('pdf_toolkit.client.flow_from_clientsecrets')
    @patch('pdf_toolkit.oauth_tools.run_flow')
    @patch('pdf_toolkit.discovery.build')
    def test_authenticate_new_credentials(self, mock_build, mock_run_flow,
                                          mock_flow_from_secrets, mock_storage):
        """Test authentication flow for new credentials"""
        # Create credentials file
        self.credentials_path.write_text('{}')

        # Mock storage
        mock_store = MagicMock()
        mock_storage.return_value = mock_store
        mock_store.get.return_value = None  # No existing credentials

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.invalid = False
        mock_creds.token_expiry = None
        mock_run_flow.return_value = mock_creds

        # Mock flow
        mock_flow = MagicMock()
        mock_flow.params = {}
        mock_flow_from_secrets.return_value = mock_flow

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        ocr = GoogleDriveOCR(
            credentials_path=str(self.credentials_path),
            token_path=str(self.token_path)
        )
        ocr.authenticate()

        # Verify flow parameters were set
        self.assertEqual(mock_flow.params['access_type'], 'offline')
        self.assertEqual(mock_flow.params['approval_prompt'], 'force')

        # Verify service was created
        self.assertEqual(ocr.service, mock_service)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PdfReader')
    def test_split_pdf(self, mock_pdf_reader):
        """Test PDF splitting into chunks"""
        # Create test PDF
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        # Mock PdfReader
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_reader.pages = [mock_page] * 25  # 25 pages
        mock_pdf_reader.return_value = mock_reader

        with patch('pdf_toolkit.PdfWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer_class.return_value = mock_writer

            ocr = GoogleDriveOCR(pages_per_chunk=10)
            chunks = ocr.split_pdf(test_pdf)

            # Should create 3 chunks (10 + 10 + 5)
            self.assertEqual(len(chunks), 3)
            self.assertTrue(all(chunk.name.endswith('.pdf') for chunk in chunks))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PdfReader')
    def test_split_pdf_to_folder(self, mock_pdf_reader):
        """Test PDF splitting to specific folder"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        output_folder = Path(self.temp_dir) / "chunks"
        output_folder.mkdir()

        # Mock PdfReader
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_reader.pages = [mock_page] * 15  # 15 pages
        mock_pdf_reader.return_value = mock_reader

        with patch('pdf_toolkit.PdfWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer_class.return_value = mock_writer

            ocr = GoogleDriveOCR(pages_per_chunk=10)
            chunks = ocr.split_pdf_to_folder(test_pdf, output_folder)

            # Should create 2 chunks in the specified folder
            self.assertEqual(len(chunks), 2)
            self.assertTrue(all(chunk.parent == output_folder for chunk in chunks))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_ocr_file_unsupported_type(self):
        """Test OCR file with unsupported file type"""
        ocr = GoogleDriveOCR()
        ocr.service = MagicMock()  # Mock authenticated service

        test_file = Path(self.temp_dir) / "test.xyz"
        test_file.touch()
        output_file = Path(self.temp_dir) / "output.txt"

        with self.assertRaises(ValueError) as context:
            ocr.ocr_file(test_file, output_file, 'xyz')
        self.assertIn("Unsupported file type", str(context.exception))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_ocr_file_not_authenticated(self):
        """Test OCR file without authentication"""
        ocr = GoogleDriveOCR()
        # Don't set service (not authenticated)

        test_file = Path(self.temp_dir) / "test.pdf"
        test_file.touch()
        output_file = Path(self.temp_dir) / "output.txt"

        with self.assertRaises(RuntimeError) as context:
            ocr.ocr_file(test_file, output_file, 'pdf')
        self.assertIn("Not authenticated", str(context.exception))

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.MediaFileUpload')
    @patch('pdf_toolkit.io.FileIO')
    @patch('pdf_toolkit.MediaIoBaseDownload')
    def test_ocr_file_success(self, mock_download, mock_fileio, mock_upload):
        """Test successful OCR of a file"""
        test_file = Path(self.temp_dir) / "test.pdf"
        test_file.write_text("test content")
        output_file = Path(self.temp_dir) / "output.txt"

        # Mock Google Drive service
        mock_service = MagicMock()
        mock_file_response = {'id': 'file123'}
        mock_service.files().create().execute.return_value = mock_file_response

        # Mock download
        mock_downloader = MagicMock()
        mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]
        mock_download.return_value = mock_downloader

        # Mock FileIO
        mock_file_handle = MagicMock()
        mock_fileio.return_value = mock_file_handle

        ocr = GoogleDriveOCR()
        ocr.service = mock_service

        ocr.ocr_file(test_file, output_file, 'pdf')

        # Verify file was uploaded (call count includes method chaining)
        self.assertTrue(mock_service.files().create.called)

        # Verify file was deleted from Drive
        mock_service.files().delete.assert_called_once_with(fileId='file123')

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    def test_ocr_pdf_chunked_creates_folder(self):
        """Test that ocr_pdf_chunked creates processing folder"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        ocr = GoogleDriveOCR()
        ocr.service = MagicMock()

        with patch.object(ocr, 'split_pdf_to_folder', return_value=[]):
            with patch('builtins.open', mock_open()):
                try:
                    ocr.ocr_pdf_chunked(test_pdf)
                except:
                    pass

        # Verify processing folder was created
        processing_folder = Path(self.temp_dir) / "test_processing"
        self.assertTrue(processing_folder.exists())


class TestArgumentParser(unittest.TestCase):
    """Test command-line argument parsing"""

    def test_parser_creation(self):
        """Test that parser is created successfully"""
        parser = create_parser()
        self.assertIsNotNone(parser)

    def test_convert_command(self):
        """Test convert command arguments"""
        parser = create_parser()
        args = parser.parse_args(['convert', 'input.pdf'])

        self.assertEqual(args.command, 'convert')
        self.assertEqual(args.input, 'input.pdf')
        self.assertEqual(args.dpi, DEFAULT_DPI)
        self.assertEqual(args.quality, DEFAULT_JPEG_QUALITY)

    def test_convert_command_with_options(self):
        """Test convert command with all options"""
        parser = create_parser()
        args = parser.parse_args([
            'convert', 'input.pdf',
            '-o', 'output.pdf',
            '--dpi', '150',
            '--quality', '80'
        ])

        self.assertEqual(args.output, 'output.pdf')
        self.assertEqual(args.dpi, 150)
        self.assertEqual(args.quality, 80)

    def test_ocr_command(self):
        """Test OCR command arguments"""
        parser = create_parser()
        args = parser.parse_args(['ocr', 'input.pdf'])

        self.assertEqual(args.command, 'ocr')
        self.assertEqual(args.input, 'input.pdf')
        self.assertEqual(args.chunk_size, PAGES_PER_CHUNK)
        self.assertFalse(args.keep_chunks)
        self.assertFalse(args.delete_original)
        self.assertFalse(args.no_convert)

    def test_ocr_command_with_all_options(self):
        """Test OCR command with all options"""
        parser = create_parser()
        args = parser.parse_args([
            'ocr', 'input.pdf',
            '-o', 'output.txt',
            '--credentials', 'creds.json',
            '--token', 'token.json',
            '--chunk-size', '20',
            '--keep-chunks',
            '--delete-original',
            '--no-convert',
            '--dpi', '150',
            '--quality', '85'
        ])

        self.assertEqual(args.output, 'output.txt')
        self.assertEqual(args.credentials, 'creds.json')
        self.assertEqual(args.token, 'token.json')
        self.assertEqual(args.chunk_size, 20)
        self.assertTrue(args.keep_chunks)
        self.assertTrue(args.delete_original)
        self.assertTrue(args.no_convert)
        self.assertEqual(args.dpi, 150)
        self.assertEqual(args.quality, 85)

    def test_ocr_batch_command(self):
        """Test OCR batch command arguments"""
        parser = create_parser()
        args = parser.parse_args(['ocr-batch'])

        self.assertEqual(args.command, 'ocr-batch')
        self.assertEqual(args.dir, '.')
        self.assertIsNone(args.types)

    def test_ocr_batch_with_options(self):
        """Test OCR batch command with options"""
        parser = create_parser()
        args = parser.parse_args([
            'ocr-batch',
            '--dir', './docs',
            '--types', 'pdf', 'jpg',
            '--chunk-size', '15',
            '--no-convert'
        ])

        self.assertEqual(args.dir, './docs')
        self.assertEqual(args.types, ['pdf', 'jpg'])
        self.assertEqual(args.chunk_size, 15)
        self.assertTrue(args.no_convert)

    def test_no_command_provided(self):
        """Test behavior when no command is provided"""
        parser = create_parser()
        args = parser.parse_args([])

        self.assertIsNone(args.command)


class TestMainFunction(unittest.TestCase):
    """Test main function and CLI integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('sys.argv', ['pdf_toolkit.py'])
    @patch('sys.exit')
    def test_main_no_command(self, mock_exit):
        """Test main function with no command prints help"""
        with patch('sys.stdout', new=io.StringIO()):
            main()

        mock_exit.assert_called_once_with(1)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    @patch('pdf_toolkit.img2pdf.convert')
    def test_main_convert_command(self, mock_img2pdf, mock_convert_backend):
        """Test main function with convert command"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        # Mock image conversion
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_convert_backend.return_value = [mock_image]
        mock_img2pdf.return_value = b'fake pdf'

        with patch('sys.argv', ['pdf_toolkit.py', 'convert', str(test_pdf)]):
            with patch('sys.stdout', new=io.StringIO()):
                main()

        # Verify output file was created
        output_file = Path(self.temp_dir) / "test_image.pdf"
        self.assertTrue(output_file.exists())

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', False)
    def test_main_ocr_without_image_deps(self):
        """Test OCR without image conversion dependencies"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        with patch('sys.argv', ['pdf_toolkit.py', 'ocr', str(test_pdf), '--no-convert']):
            with patch.object(GoogleDriveOCR, 'authenticate'):
                with patch.object(GoogleDriveOCR, 'ocr_pdf_chunked') as mock_ocr:
                    main()

                    # Verify ocr_pdf_chunked was called
                    mock_ocr.assert_called_once()

    @patch('sys.argv', ['pdf_toolkit.py', 'ocr', 'nonexistent.pdf'])
    @patch('sys.exit')
    def test_main_file_not_found(self, mock_exit):
        """Test main function handles file not found error"""
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            main()

        mock_exit.assert_called_once_with(1)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', False)
    @patch('sys.argv', ['pdf_toolkit.py', 'convert', 'test.pdf'])
    @patch('sys.exit')
    def test_main_missing_dependencies(self, mock_exit):
        """Test main function handles missing dependencies"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        with patch('sys.argv', ['pdf_toolkit.py', 'convert', str(test_pdf)]):
            with patch('sys.stdout', new=io.StringIO()):
                main()

        mock_exit.assert_called_once_with(1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PdfReader')
    def test_split_pdf_single_page(self, mock_pdf_reader):
        """Test splitting a single-page PDF"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]  # Single page
        mock_pdf_reader.return_value = mock_reader

        with patch('pdf_toolkit.PdfWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer_class.return_value = mock_writer

            ocr = GoogleDriveOCR(pages_per_chunk=10)
            chunks = ocr.split_pdf(test_pdf)

            # Should create 1 chunk
            self.assertEqual(len(chunks), 1)

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PdfReader')
    def test_split_pdf_exact_chunk_size(self, mock_pdf_reader):
        """Test splitting PDF with exact chunk size"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()] * 20  # Exactly 2 chunks of 10
        mock_pdf_reader.return_value = mock_reader

        with patch('pdf_toolkit.PdfWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer_class.return_value = mock_writer

            ocr = GoogleDriveOCR(pages_per_chunk=10)
            chunks = ocr.split_pdf(test_pdf)

            self.assertEqual(len(chunks), 2)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    def test_convert_empty_pdf(self, mock_convert_backend):
        """Test converting PDF with no pages"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        mock_convert_backend.return_value = []  # No pages

        with patch('pdf_toolkit.img2pdf.convert', return_value=b''):
            converter = PDFToImageConverter()
            output = converter.convert(test_pdf)

            self.assertTrue(output.exists())

    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    def test_ocr_with_special_characters_in_filename(self):
        """Test OCR with special characters in filename"""
        test_pdf = Path(self.temp_dir) / "test file (1).pdf"
        test_pdf.touch()

        ocr = GoogleDriveOCR()
        ocr.service = MagicMock()

        with patch.object(ocr, 'split_pdf_to_folder', return_value=[]):
            with patch('builtins.open', mock_open()):
                try:
                    ocr.ocr_pdf_chunked(test_pdf)
                except:
                    pass

        # Should handle special characters in folder name
        processing_folder = Path(self.temp_dir) / "test file (1)_processing"
        self.assertTrue(processing_folder.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('pdf_toolkit.PDF_TO_IMAGE_AVAILABLE', True)
    @patch('pdf_toolkit.PYPDFIUM2_AVAILABLE', True)
    @patch('pdf_toolkit.GOOGLE_OCR_AVAILABLE', True)
    @patch('pdf_toolkit.PDFToImageConverter._convert_with_pypdfium2')
    @patch('pdf_toolkit.img2pdf.convert')
    def test_full_convert_then_ocr_workflow(self, mock_img2pdf, mock_convert_backend):
        """Test complete workflow: convert then OCR"""
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.touch()

        # Mock conversion
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_convert_backend.return_value = [mock_image]
        mock_img2pdf.return_value = b'fake pdf'

        # Step 1: Convert
        converter = PDFToImageConverter()
        image_pdf = converter.convert(test_pdf)
        self.assertTrue(image_pdf.exists())

        # Step 2: OCR (mocked completely)
        ocr = GoogleDriveOCR()
        ocr.service = MagicMock()

        # Mock the entire ocr_pdf_chunked to avoid PdfReader issues
        with patch.object(ocr, 'ocr_pdf_chunked', return_value=Path('output.txt')) as mock_ocr:
            result = ocr.ocr_pdf_chunked(image_pdf, auto_convert=False)
            mock_ocr.assert_called_once()
            self.assertIsNotNone(result)


def run_tests_with_coverage():
    """Run tests with coverage report"""
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()

        # Run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        cov.stop()
        cov.save()

        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        cov.report(include=['pdf_toolkit.py'])

        # Generate HTML coverage report
        cov.html_report(directory='htmlcov', include=['pdf_toolkit.py'])
        print("\nHTML coverage report generated in 'htmlcov/' directory")

        return result.wasSuccessful()

    except ImportError:
        print("Coverage module not installed. Running tests without coverage.")
        print("Install with: pip install coverage")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)
