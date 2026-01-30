
import pandas as pd
import pytest
from pathlib import Path
import shutil
import sys
import os


try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

sys.path.append(str(BASE_DIR.parent))

from file_downloader_segmentor.s0_saving_files_to_folder import get_files
from file_downloader_segmentor.get_image import get_image_from_pdf
from file_downloader_segmentor.segmentor import images_segmentor




# Configuration
TEST_DATA_DIR = BASE_DIR 
DOWNLOAD_DIR = TEST_DATA_DIR / "download"
DATABASE_DIR = BASE_DIR.parent / "database"

# Test files
URL_CSV = TEST_DATA_DIR / "test.csv"
RAW_CSV = TEST_DATA_DIR / "test.csv"
TEST_PDF_NAME = "01_CYBERMEDIA_25012026224121_cmilNPad.pdf"
EXTRACT_TEST_PDF_PATH = TEST_DATA_DIR / "pdfs" / "test.pdf"
OUTPUT_CSV = DATABASE_DIR / "test_unprocessed.csv"


@pytest.fixture(scope="module")
def setup_test_dirs():
    """Create test directories and verify test files exist"""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    DATABASE_DIR.mkdir(exist_ok=True)
    (TEST_DATA_DIR / "pdfs").mkdir(exist_ok=True)
    
    # Verify required test files exist
    assert URL_CSV.exists(), f"Required test file missing: {URL_CSV}"
    assert RAW_CSV.exists(), f"Required test file missing: {RAW_CSV}"
    assert EXTRACT_TEST_PDF_PATH.exists(), f"Required test file missing: {EXTRACT_TEST_PDF_PATH}"
    
    yield
    
    # Cleanup
    if os.getenv("CI"):
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
        if OUTPUT_CSV.exists():
            OUTPUT_CSV.unlink()
        print("🧹 CI cleanup completed")
    else:
        print("💾 Files kept for local inspection at:")
        print(f"   - {DOWNLOAD_DIR}")
        print(f"   - {OUTPUT_CSV}")


@pytest.fixture(scope="module")
def downloaded_pdf(setup_test_dirs):
    """Download PDF and return path"""
    get_files(str(RAW_CSV), str(DOWNLOAD_DIR), str(URL_CSV))
    
    pdf_path = DOWNLOAD_DIR / TEST_PDF_NAME
    assert pdf_path.exists(), f"PDF not downloaded: {pdf_path}"
    
    return pdf_path


@pytest.fixture(scope="module")
def extracted_image():
    """Extract image from pre-existing test PDF"""
    img = get_image_from_pdf(str(EXTRACT_TEST_PDF_PATH))
    assert img is not None, "Image extraction failed"
    return img


# Tests
def test_1_pdf_downloaded(downloaded_pdf):
    """Test: PDF is downloaded successfully"""
    assert downloaded_pdf.exists()
    assert downloaded_pdf.suffix == ".pdf"
    assert downloaded_pdf.stat().st_size > 0
    print(f"✅ PDF downloaded: {downloaded_pdf.name} ({downloaded_pdf.stat().st_size} bytes)")


def test_2_image_extracted(extracted_image):
    """Test: Image is extracted from PDF"""
    assert extracted_image is not None
    
    if hasattr(extracted_image, 'size'):
        width, height = extracted_image.size
        assert width > 0 and height > 0
        print(f"✅ Image extracted: {width}x{height} pixels")
    else:
        print(f"✅ Image extracted: {type(extracted_image)}")


def test_3_csv_updated_after_segmentation(extracted_image):
    """Test: CSV is updated after image segmentation"""
    rows_before = len(pd.read_csv(OUTPUT_CSV)) if OUTPUT_CSV.exists() else 0
    
    images_segmentor(extracted_image, EXTRACT_TEST_PDF_PATH.name)
    
    assert OUTPUT_CSV.exists(), f"CSV not created: {OUTPUT_CSV}"
    
    df_after = pd.read_csv(OUTPUT_CSV)
    rows_after = len(df_after)
    
    assert rows_after > 0, "CSV is empty"
    assert rows_after > rows_before, f"No new rows (before: {rows_before}, after: {rows_after})"
    
    if 'pdf_filename' in df_after.columns:
        assert EXTRACT_TEST_PDF_PATH.name in df_after['pdf_filename'].values, \
            f"PDF {EXTRACT_TEST_PDF_PATH.name} not found in CSV"
    
    print(f"✅ CSV updated: {rows_before} → {rows_after} rows")


def test_4_csv_has_valid_data():
    """Test: CSV has at least one entry"""
    if not OUTPUT_CSV.exists():
        pytest.skip("CSV not created yet")
    
    assert len(pd.read_csv(OUTPUT_CSV)) > 0, "CSV is empty"
    print(f"✅ CSV has data")