
from pdf2image import convert_from_path


def get_image_from_pdf(pdf_file_path):
    # ================= CONFIGURATION =================
    #PDF_FOLDER = "all_pdf_files_raw"              # Folder containing your PDFs
    #OUTPUT_FOLDER = "input"  # Where to save first pages
    DPI = 200                              # Image quality
    POPPLER_PATH = r"C:/Users/akela/Downloads/Release-25.07.0-0/poppler-25.07.0/Library/bin"  # Update if needed
    # =================================================
    try:
        # Convert ONLY the first page
        #print(f"Processing: {pdf_file} → extracting first page...")
        pages = convert_from_path(
            pdf_file_path,
            dpi=DPI,
            poppler_path=POPPLER_PATH,
            first_page=1,
            last_page=1  # This ensures only page 1 is converted
        )
        
        # Save the first (and only) page
        if pages:
            #output_name = os.path.splitext(pdf_file_path)[0] + "_first_page.png"
            #output_path = os.path.join(OUTPUT_FOLDER, output_name)
            #pages[0].save(output_path, "PNG")
            #print(f"Saved: {output_path}")
            return pages[0]
        else: 
            print(f"Warning: No pages extracted from {pdf_file_path}")
            return None
    except Exception as e:
        print(f"Failed to process {pdf_file_path}: {e}")
        return None