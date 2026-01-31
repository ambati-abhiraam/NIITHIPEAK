import fitz  # PyMuPDF
from PIL import Image
import io
import os

def get_image_from_pdf(pdf_path):
    """
    Extract first page image from PDF using PyMuPDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        PIL.Image object or None if extraction fails
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            return None
        
        print(f"📄 Processing PDF: {pdf_path}")
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        if len(doc) == 0:
            print(f"❌ PDF has no pages")
            doc.close()
            return None
        
        # Get first page
        page = doc[0]
        
        # Render page to image (zoom=2 for better quality)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        doc.close()
        
        print(f"✅ Image extracted: {img.size[0]}x{img.size[1]} pixels")
        return img
        
    except Exception as e:
        print(f"❌ Failed to process {pdf_path}: {e}")
        import traceback
        traceback.print_exc()
        return None