import pandas as pd
import shutil
from pathlib import Path

# 1. Setup Paths relative to this script
BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

# Define your locations from the parent directory
#CSV_LOCATION = PARENT_DIR / "all_files" / "your_file.csv"  # Update with your csv name
#SOURCE_FOLDER = PARENT_DIR / "source_images"             # Folder where .png files are
#DEST_FOLDER = PARENT_DIR / "destination_pdfs"            # Folder where .pdf files go

# Create destination folder if it doesn't exist


def process_and_copy(CSV_LOCATION, SOURCE_FOLDER, DEST_FOLDER):
    
    DEST_FOLDER.mkdir(exist_ok=True)
    # 2. Read CSV (header=None because your file has no headings)
    # Column 0: Segment Name | Column 1: Filename

    df = pd.read_csv(CSV_LOCATION, header=None)

    for index, row in df.iterrows():
        segment_name = str(row[0])
        original_filename = str(row[1])
        #print(original_filename)

        # 3. Handle filename replacement (.png -> .pdf)
        if original_filename.endswith(".png"):
            
            new_filename = original_filename.replace(".png", ".pdf")
    
        else:
            
            # If it doesn't have .png, just append .pdf
            new_filename = f"{original_filename}.pdf"

        # 4. Define Full Source and Destination paths
        # We look for the original file (png) but want to save it as pdf
        source_path = SOURCE_FOLDER / new_filename
        dest_path = DEST_FOLDER / new_filename

        # 5. Copy the file
        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            #print(f"✅ Copied: {original_filename} -> {new_filename} (Segment: {segment_name})")
        else:
            print(f"❌ File not found: {source_path}")

#if __name__ == "__main__":
#    process_and_copy()