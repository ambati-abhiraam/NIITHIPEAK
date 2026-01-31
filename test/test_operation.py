import pandas as pd
import pytest
from pathlib import Path
import shutil
import sys
import os

from file_downloader_segmentor.s0_saving_files_to_folder import get_files
from file_downloader_segmentor.get_image import get_image_from_pdf
from file_downloader_segmentor.segmentor import images_segmentor

try:
    BASE_DIR = Path(__file__).resolve().parent  # test/
except NameError:
    BASE_DIR = Path.cwd()

sys.path.append(str(BASE_DIR.parent))

# Configuration - YOUR actual file structure
TEST_DIR = BASE_DIR                    # test/
DOWNLOAD_DIR = TEST_DIR / "download"   # test/download/
PDFS_DIR = TEST_DIR / "pdfs"          # test/pdfs/
DATABASE_DIR = BASE_DIR.parent / "database"  # database/

# Test files
TEST_CSV = TEST_DIR / "test.csv"                # test/test.csv ✅
EXTRACT_TEST_PDF_PATH = PDFS_DIR / "test.pdf"  # test/pdfs/test.pdf ✅
OUTPUT_CSV = DATABASE_DIR / "test_unprocessed.csv"


@pytest.fixture(scope="module")
def setup_test_dirs():
    """Create test directories and verify test files exist"""
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    PDFS_DIR.mkdir(exist_ok=True)
    DATABASE_DIR.mkdir(exist_ok=True)
    
    # Verify required test files exist
    print(f"🔍 Looking for test.csv at: {TEST_CSV}")
    print(f"🔍 Looking for test.pdf at: {EXTRACT_TEST_PDF_PATH}")
    
    missing_files = []
    
    if not TEST_CSV.exists():
        missing_files.append(f"  - {TEST_CSV}")
    if not EXTRACT_TEST_PDF_PATH.exists():
        missing_files.append(f"  - {EXTRACT_TEST_PDF_PATH}")
    
    if missing_files:
        error_msg = "Missing required test files:\n" + "\n".join(missing_files)
        error_msg += f"\n\nFiles in test/: {list(TEST_DIR.iterdir())}"
        error_msg += f"\n\nFiles in test/pdfs/: {list(PDFS_DIR.iterdir()) if PDFS_DIR.exists() else 'Directory not found'}"
        pytest.fail(error_msg)
    
    print(f"✅ Found test.csv: {TEST_CSV}")
    print(f"✅ Found test.pdf: {EXTRACT_TEST_PDF_PATH}")
    
    yield
    
    # Cleanup
    if os.getenv("CI"):
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        if OUTPUT_CSV.exists():
            OUTPUT_CSV.unlink()
        print("🧹 CI cleanup completed")
    else:
        print("💾 Files kept for local inspection")


@pytest.fixture(scope="module")
def downloaded_pdf(setup_test_dirs):
    """Download PDF and return path"""
    print(f"📥 Downloading PDF using test.csv...")
    get_files(str(TEST_CSV), str(DOWNLOAD_DIR), str(TEST_CSV))
    
    downloaded_files = list(DOWNLOAD_DIR.glob("*.pdf"))
    
    if not downloaded_files:
        pytest.fail(f"No PDF downloaded to {DOWNLOAD_DIR}")
    
    pdf_path = downloaded_files[0]
    print(f"✅ Downloaded: {pdf_path}")
    return pdf_path


@pytest.fixture(scope="module")
def extracted_image():
    """Extract image from pre-existing test PDF"""
    print(f"📄 Extracting image from: {EXTRACT_TEST_PDF_PATH}")
    img = get_image_from_pdf(str(EXTRACT_TEST_PDF_PATH))
    
    if img is None:
        print(f"❌ Image extraction returned None")
        print(f"❌ PDF exists: {EXTRACT_TEST_PDF_PATH.exists()}")
        print(f"❌ PDF size: {EXTRACT_TEST_PDF_PATH.stat().st_size if EXTRACT_TEST_PDF_PATH.exists() else 'N/A'}")
    
    assert img is not None, f"Image extraction failed for {EXTRACT_TEST_PDF_PATH}"
    print(f"✅ Image extracted successfully")
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
    
    print(f"📊 CSV rows before: {rows_before}")
    images_segmentor(extracted_image, EXTRACT_TEST_PDF_PATH.name)
    
    assert OUTPUT_CSV.exists(), f"CSV not created: {OUTPUT_CSV}"
    
    df_after = pd.read_csv(OUTPUT_CSV)
    rows_after = len(df_after)
    
    print(f"📊 CSV rows after: {rows_after}")
    
    assert rows_after > 0, "CSV is empty"
    assert rows_after > rows_before, f"No new rows (before: {rows_before}, after: {rows_after})"
    
    print(f"✅ CSV updated: {rows_before} → {rows_after} rows")


def test_4_csv_has_valid_data():
    """Test: CSV has at least one entry"""
    if not OUTPUT_CSV.exists():
        pytest.skip("CSV not created yet")
    
    df = pd.read_csv(OUTPUT_CSV)
    assert len(df) > 0, "CSV is empty"
    print(f"✅ CSV has {len(df)} entries")