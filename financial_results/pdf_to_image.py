import os
from pathlib import Path
from pdf2image import convert_from_path

def pdf_to_images(pdf_path, output_folder):
    # Create output directory if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert PDF to a list of PIL Image objects
    # dpi=200 is a good balance between quality and file size
    print(f"Converting: {pdf_path}...")
    pages = convert_from_path(pdf_path, dpi=200)

    for i, page in enumerate(pages):
        # Save each page as a JPEG
        image_name = f"page_{i + 1}.jpg"
        image_path = output_path / image_name
        
        page.save(image_path, "JPEG")
        #print(f"Saved: {image_path}")

def convert_pdf_to_image(pdf_path, output_folder):
    # Update these paths for your system
    file_to_convert = pdf_path
    destination = output_folder
    
    try:
        pdf_to_images(file_to_convert, destination)
        print("Done!")
    except Exception as e:
        print(f"An error occurred: {e}")