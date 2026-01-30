import pathlib
import pytesseract
from PIL import Image
import os
from pathlib import Path

def extract_text_from_image(image_path):
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Use pytesseract to convert the image to string
        text = pytesseract.image_to_string(img)

        return text
    except Exception as e:
        return f"An error occurred: {e} while extraction text from image using pytesseract."
    


def keyword_checking(raw_text, type_of_check):
    #print(raw_text)
#    keyword_list = ["unaudited standalone financial results",
#                    "consolidated unaudited financial results",
#                    "statement of unaudited financial results",
#                    "statement of unaudited consolidated financial results",
#                    "standalone unaudited financial results",
#                    "consolidated financial results",
#                    "unaudited financial results",
#                    "audited financial results",
#                    "unaudited financial result",
#                    "audited financial result",
#                    "standalone financial results",
#                    "consolidated financial results",
#                    "standalone financial result",
#                    "consolidated financial result",
#                    "statement of financial results",
#                    "statement of consolidated financial results",
#                    "standalone statement of financial results",
#                    "consolidated statement of financial results",
#                    "statement of profit and loss",
#                    "consolidated statement of profit and loss",
#                    "standalone statement of profit and loss"
#
#
#    ]
    consolidated_keywords = ["consolidated unaudited financial results",
                             "consolidated un-audited financial results",
                             "unaudited consolidated financial results",
                             "un-audited consolidated financial result",
                             "consolidated audited financial results",
                             "audited consolidated financial results",
                             "consolidated financial results",
                             

                             "statement of unaudited consolidated financial results",
                             "statement of un-audited consolidated financial results",
                             "statement of consolidated unaudited financial results",
                             "statement of consolidated un-audited financial results",
                             "statement of audited consolidated financial results",
                             "statement of consolidated audited financial results",
                             "statement of consolidated financial results",

                             "statement unaudited consolidated financial results",
                             "statement un-audited consolidated financial results",
                             "statement consolidated unaudited financial results",
                             "statement consolidated un-audited financial results",
                             "statement audited consolidated financial results",
                             "statement consolidated audited financial results",
                             "statement consolidated financial results",


                             "unaudited consolidated statement of financial results",
                             "un-audited consolidated statement of financial results",
                             "consolidated unaudited statement of financial results",
                             "consolidated un-audited statement of financial results",
                             "audited consolidated statement of financial results",
                             "consolidated audited statement of financial results",
                             "consolidated statement of financial results",


                             "unaudited consolidated statement financial results",
                             "un-audited consolidated statement financial results",
                             "consolidated unaudited statement financial results",
                             "consolidated un-audited statement financial results",
                             "audited consolidated statement financial results",
                             "consolidated audited statement financial results",
                             "consolidated statement financial results",


                             "unaudited consolidated ind as compliant financial results",
                             "un-audited consolidated ind as compliant financial results",
                             "consolidated unaudited ind as compliant financial results",
                             "consolidated un-audited ind as compliant financial results",
                             "audited consolidated ind as compliant financial results",
                             "consolidated audited ind as compliant financial results",
                             "consolidated ind as compliant financial results",



                             "ind as compliant unaudited consolidated financial results",
                             "ind as compliant un-audited consolidated financial results",
                             "ind as compliant consolidated unaudited financial results",
                             "ind as compliant consolidated un-audited financial results",
                             "ind as compliant audited consolidated financial results",
                             "ind as compliant consolidated audited financial results",
                             "ind as compliant consolidated financial results",
                             
                             ]
    
    alternative_keywords=["standalone statement of financial results",
                          "unaudited financial results",
                          "unaudited standalone ind as compliant financial result",
                          "statement of unaudited financial results",
                          "statement of unaudited standalone financial results",
                          "statement of un-audited standalone financial results",]
    
    consolidated_keyword_2=["consolidated"]

    secondary_check =["revenue from operations"]

    # 1. Standardize the text: convert to lowercase
    clean_text = raw_text.lower()
    
    # 2. Standardize keywords: ensure they are all lowercase for comparison
    keywords_consolidated = [word.lower() for word in consolidated_keywords]
    keywords_secondary_check = [word.lower() for word in secondary_check]
    keywords_alternative = [word.lower() for word in alternative_keywords]

    if type_of_check == "consolidated":
        matches_consolidated = [word for word in keywords_consolidated if word in clean_text]
        if matches_consolidated:
            #print("Consolidated keywords matched:", matches_consolidated)
            matches_secondary_check = [word for word in keywords_secondary_check if word in clean_text]

            if matches_secondary_check:
                print("consolidated keywords matched:", matches_consolidated,matches_secondary_check)
                return True
            else:
                return False
        else:
            return False
    
    else:
        matches_alternative = [word for word in keywords_alternative if word in clean_text]
        
        if matches_alternative:
            #print("Alternative keywords matched:", matches_alternative)
            matches_secondary_check = [word for word in keywords_secondary_check if word in clean_text]

            if matches_secondary_check:
                print("alternative keywords matched:", matches_alternative,matches_secondary_check)
                return True
            else:
                return False
        
        else:
            return False
    





def get_page_number(folder_path, type_of_check):
    # Define the folder path
    #folder_path = pathlib.Path("./my_images")
    page_number = 0
    matched_pages = []
    # Define common image extensions
    image_extensions = {".jpg", ".jpeg", ".png"}
    #print(folder_path)
    folder_path = Path(folder_path)

    image_count = sum(
        1 for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
        )

    for i in range(image_count):
        image_path = os.path.join(folder_path, f"page_{i+1}.jpg")

        text = extract_text_from_image(image_path)
        if type_of_check == "consolidated":
            check = keyword_checking(text, type_of_check)
        else:
            check = keyword_checking(text, type_of_check)

        if check:
            matched_pages.append(i+1)

    return matched_pages
        