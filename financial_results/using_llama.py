import os
from llama_parse import LlamaParse
from pathlib import Path


def use_llama_parse_for_images(image_path, page_number,output_path):
    # 1. SETUP: Put your key here
    api_key = "llx-fEeTCysGXn87ILDIOrszvARZtZpLd31ujt2g6itKcyeURXZh"  

    # 2. INITIALIZE: Set it to "Cost-Effective" mode
    # We do this by turning off 'fast_mode' and 'premium_mode'
#    parser = LlamaParse(
#        api_key=api_key,
#        result_type="markdown",  # Saves as easy-to-read text
#        premium_mode=False,      # Saves money (Cost-Effective)
#        fast_mode=False, 
#        parse_mode="parse_page_with_llm",        # Better quality than "Fast" mode
#        user_prompt="Format all detected tables using strict Markdown syntax with pipes | and dashes --- for separators.",
#        target_pages=page_number
#    )

    parser = LlamaParse(
        # See how to get your API key at https://developers.llamaindex.ai/python/cloud/general/api_key/
        api_key=api_key,

        # The parsing tier. Options: fast, cost_effective, agentic, agentic_plus
        tier="cost_effective",

       # The version of the parsing tier to use. Use 'latest' for the most recent version
        version="latest",

       # Whether to output tables as HTML in the markdown output
        #output_tables_as_HTML=True,

       # A string containing a list of comma separated containing the page number to extract. If not specified all pages are extracted from the document. The first page is the page 0
        target_pages=page_number,

       # The maximum number of pages to parse
        max_pages=1,

       # Compact markdown table. LlamaParse will compact the markdown table to not include too many spaces
        compact_markdown_table=True,

       # Whether to try to extract tables aggressively, may lead to false positives
        aggressive_table_extraction=True,

       # Whether to use precise bounding box extraction (experimental)
        #precise_bounding_box=True,
    )
    # 3. LOCATE FILES: Look for PDFs in a folder
    input_folder = image_path
    output_folder = output_path
    md_output_path = os.path.join(output_path,"output.md")

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 4. RUN: Loop through every file one by one
    #for filename in os.listdir(input_folder):
    #filename.endswith(".jpg"):
    print(f"Working on: {input_folder}...")

    # This line sends the file to LlamaParse and waits for it to finish
    #documents = parser.load_data(Path(input_folder))

    result = parser.parse(Path(input_folder))


    # get the llama-index markdown documents
    markdown_documents = result.get_markdown_documents(split_by_page=True)
    # Save the result to a text file
#    output_filename = filename.replace(".jpg", ".md")
#    with open(f"{output_folder}/{output_filename}", "w", encoding="utf-8") as f:
#        for doc in documents:
#            f.write(doc.text)

    # This saves it to the file
    with open(md_output_path, "a", encoding="utf-8") as f:
        #f.write(f"## Table {table_ix}\n\n")
        for doc in markdown_documents:
            f.write(doc.text)
            f.write("\n\n")
    
#    print(f"Done! Saved to {output_folder}/{output_filename}")

 #   print(" have beenprocessed!")