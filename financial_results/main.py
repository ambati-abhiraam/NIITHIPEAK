import os
import shutil
from pathlib import Path 
import time
from datetime import date



from pdf_to_image import convert_pdf_to_image
from page_finder import get_page_number
from using_unstructured import get_rmd_using_unstructures_llamaparse
#from dockling import get_rmd_using_docling
#from llm import get_response_from_llm


#from table_processor import extract_financial_data
from table_extractor import get_values
from load_to_csv import write_or_append_csv


from get_pdf_from_csv import process_and_copy

import pathlib




# 1. Record the start time
start = time.perf_counter()




BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent


TARGET_DATES = {
    "this_quarter": date(2025, 12, 31),
    "previous_quarter": date(2025, 9, 30),
    "same_q_last_year": date(2024, 12, 31)
}



CSV_LOCATION = PARENT_DIR /"database/financial_results_unprocessed.csv"  # Update with your csv name
SOURCE_FOLDER = PARENT_DIR / "pdf_files_unprocessed"             # Folder where .png files are
DEST_FOLDER = PARENT_DIR / "financial_results/pdfs_to_be_processed"            # Folder where .pdf files go

process_and_copy(CSV_LOCATION, SOURCE_FOLDER, DEST_FOLDER)



# Define the directory path
# Use "." for the current folder or provide a full path like "C:/Users/Documents/PDFs"
folder_path = pathlib.Path("./pdfs_to_be_processed")

# Check if the directory exists
if folder_path.exists() and folder_path.is_dir():
    # Iterate through all files ending in .pdf (case-insensitive)
    for pdf_file in folder_path.glob("*.pdf"):
        # Define the directory and filename


        print(f"Processing: {pdf_file.name}")
        
        # Example: Get the absolute path if you need to open it
        #full_path = pdf_file.resolve()
        #print(f"Full Path: {full_path}")


        pdf_page_photos_path = "./pdf_page_photos"
        pdf_path = os.path.join(folder_path, pdf_file.name)
        convert_pdf_to_image(pdf_path , pdf_page_photos_path)

        page_number = get_page_number(pdf_page_photos_path, "consolidated")

        if not page_number:
            page_number = get_page_number(pdf_page_photos_path, "alternative")

            if not page_number:
                shutil.copy(pdf_path, "./pdfs_not_processed/")
        
        print(f"Pages to be processed: {page_number}")


        for i in page_number:
            md_directory = 'md_files'
            md_filename = os.path.join(md_directory, f'output.md')

            # Create the directory if it doesn't exist
            os.makedirs(md_directory, exist_ok=True)

            # Sample markdown content
            markdown_content = """

            """

            # Write the file
            with open(md_filename, 'w', encoding='utf-8') as file:
                
                
                file.write(markdown_content.strip() + '\n')




            processing_page_number = str(i-1)

            processing_photo = os.path.join(pdf_page_photos_path, f"page_{i}.jpg")
            

            
            #no_table = get_rmd_using_docling(
            #        processing_photo,
            #        "./md_files"
            #    )
            no_table = get_rmd_using_unstructures_llamaparse(
                    processing_photo,
                    pdf_path,
                    processing_page_number,
                    "./md_files"
                )
            # Save output.md to another folder with PDF filename
            try:
                # Get PDF filename without extension
                pdf_name_without_ext = Path(pdf_file).stem

                # Create destination folder for saved markdown files
                saved_md_folder = "./saved_md_files"
                os.makedirs(saved_md_folder, exist_ok=True)

                # Copy output.md to destination with PDF filename
                source_md = "./md_files/output.md"
                if os.path.exists(source_md):
                    destination_md = os.path.join(saved_md_folder, f"{pdf_name_without_ext}_{i}.md")
                    shutil.copy2(source_md, destination_md)
                    print(f"Saved output.md as {destination_md}")
            except Exception as e:
                print(f"Failed to save output.md. Reason: {e}")
            
            if no_table == "no tables found":
                continue

            else:
                #llm_json = get_response_from_llm("./md_files/output.md", pdf_file.name)
                #llm_json = extract_financial_data("./md_files/output.md", pdf_file.name)
                json = get_values("./md_files/output.md", pdf_file.name, TARGET_DATES)
                print(json)
                write_or_append_csv(json, "financial_changes.csv")
            
            try:
                #shutil.rmtree(pdf_page_photos_path)
                shutil.rmtree("./md_files")
                #shutil.move(, destination_path)

                #print("Folder and all its contents deleted successfully.")
            except Exception as e:
                print(f"Failed to delete {folder_path}. Reason: {e}")




        # Deleting the folder after processing
        try:
            shutil.rmtree(pdf_page_photos_path)
            #shutil.rmtree("./md_files")
            #shutil.move(, destination_path)

                #print("Folder and all its contents deleted successfully.")
        except Exception as e:
            print(f"Failed to delete {folder_path}. Reason: {e}")

        
        shutil.move(pdf_file, "./processed_pdf's")

        print("-------------------------------------------------------------------------")

        #time.sleep(7 * 60)
        # Your logic here (e.g., extracting text, renaming, moving)
        # ...
else:
    print("The specified folder does not exist.") 



# 2. Record the end time
end = time.perf_counter()

# 3. Calculate the difference
print(f"Total time: {end - start:.6f} seconds")