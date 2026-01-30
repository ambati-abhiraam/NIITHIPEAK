from unstructured.partition.auto import partition
from using_llama import use_llama_parse_for_images



from pathlib import Path

import pandas as pd





def get_rmd_using_unstructures_llamaparse(processing_photo ,input_pdf_path, page_number,output_path):
    # Define your image file
    image_path = input_pdf_path

    # 1. Run the partitioner
    # 'hi_res' strategy is required to detect tables in images
    # 'infer_table_structure=True' tells it to try and rebuild the rows/columns
    elements = partition(
        filename=processing_photo,
        strategy="hi_res",
        infer_table_structure=True
    )

    # 2. Filter the results for "Table" elements
    tables = [el for el in elements if el.category == "Table"]

    # 3. Check and Print
    if tables:
        print(f"✅ Found {len(tables)} table(s) in the image!")
        for i, table in enumerate(tables):
            print(f"\n--- Table {i+1} Content ---")
            #print(table.text) # Prints the raw text of the table

            use_llama_parse_for_images(image_path, page_number,output_path)

            # If you want to see the HTML version (rows and cells)
            # print(table.metadata.text_as_html)
    else:
        return "no tables found"











    

