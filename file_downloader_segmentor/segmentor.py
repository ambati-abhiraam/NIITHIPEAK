import re
import pytesseract 
import csv
import os
import sys
from pathlib import Path

# Adds the parent directory to the system path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR.parent))

PROJECT_ROOT = BASE_DIR.parent
DATABASE_DIR = PROJECT_ROOT / "database"


from keywords.keywords import (
    AMALGAMATION_KEYWORDS,
    CASH_FLOW_KEYWORDS,
    CHANGE_IN_MANAGEMENT_KEYWORDS,
    CREDIT_RATING_KEYWORDS,
    ESG_RATING_KEYWORDS,
    ESOPS_KEYWORDS,
    INSIDER_TRADING_REGEX,
    INSOLVENCY_KEYWORDS,
    INVESTOR_PRESENTATION_KEYWORDS,
    JOINT_VENTURES_KEYWORDS,
    LAW_COURT_GOVT_KEYWORDS,
    MANUFACTURING_PLAT_INSPECTION_KEYWORDS,
    MEETING_UPDATE_KEYWORDS,
    NEWS_PAPERS_KEYWORDS,
    ORDER_UPDATE_MOU_KEYWORDS,
    OUTCOME_OF_BOARDMEETING_KEYWORDS,
    POSTAL_BALLOT_NOTICES,
    RE_LODGEMENT_KEYWORDS,
    SUBSIDARY_NCBS_KEYWORDS,
    SUBSIDARY_STATUS_CHANGE_KEYWORDS,
    TRANSCRIPTS_KEYWORDS,
    FINANCIAL_RESULTS_KEYWORDS,
    TEST_KEYWORDS
)

def images_segmentor(img, img_name):

    img_name=img_name.removesuffix('.pdf') + '.png'
    #image_path = os.path.join(SOURCE_FOLDER, filename)
    
    # Extract text
    #text = pytesseract.image_to_string(Image.open(image_path), lang="eng").lower()
    text = pytesseract.image_to_string(img, lang="eng").lower()
    #print(text)
    
    segment_results = {
    "change_in_management": any(k in text for k in CHANGE_IN_MANAGEMENT_KEYWORDS),
    "law_court_govt": any(k in text for k in LAW_COURT_GOVT_KEYWORDS),
    "news_papers": any(k in text for k in NEWS_PAPERS_KEYWORDS),
    "investor_presentation": any(k in text for k in INVESTOR_PRESENTATION_KEYWORDS),
    "meeting_update": any(k in text for k in MEETING_UPDATE_KEYWORDS),
    "esops": any(k in text for k in ESOPS_KEYWORDS),
    "outcome_of_boardmeeting": any(k in text for k in OUTCOME_OF_BOARDMEETING_KEYWORDS),
    "insolvency": any(k in text for k in INSOLVENCY_KEYWORDS),
    "manufacturing_plat_inspection": any(k in text for k in MANUFACTURING_PLAT_INSPECTION_KEYWORDS),
    "transcripts": any(k in text for k in TRANSCRIPTS_KEYWORDS),
    "credit_rating": any(k in text for k in CREDIT_RATING_KEYWORDS),
    "insider_trading": re.search(INSIDER_TRADING_REGEX, text, re.IGNORECASE) is not None,
    "order_update_mou": any(k in text for k in ORDER_UPDATE_MOU_KEYWORDS),
    "cash_flow": any(k in text for k in CASH_FLOW_KEYWORDS),
    "esg_rating": any(k in text for k in ESG_RATING_KEYWORDS),
    "postal_ballot_notices": any(k in text for k in POSTAL_BALLOT_NOTICES),
    "re_lodgement": any(k in text for k in RE_LODGEMENT_KEYWORDS),
    "subsidary_ncbs": any(k in text for k in SUBSIDARY_NCBS_KEYWORDS),
    "amalgamation": any(k in text for k in AMALGAMATION_KEYWORDS),
    "joint_ventures": any(k in text for k in JOINT_VENTURES_KEYWORDS),
    "subsidary_status_change": any(k in text for k in SUBSIDARY_STATUS_CHANGE_KEYWORDS),
    "financial_results":any(k in text for k in FINANCIAL_RESULTS_KEYWORDS),
    "test": any(k in text for k in TEST_KEYWORDS)
    }



    go_to_any = 0
    
    for i in segment_results:
        
        if segment_results[i]==True:
            go_to_any+=1
            # The row you want to add
            new_row = [i, img_name]

            csv_file = i+"_unprocessed.csv"
            #csv_path = f"../database/{csv_file}"
            csv_path = DATABASE_DIR / csv_file
            # Open file in 'a' (append) mode
            with open(csv_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
        
    if go_to_any==0:
        new_row = ["unprocessed", img_name]
        csv_file = "_unprocessed.csv"
        #csv_path = f"../database/{csv_file}"
        csv_path = DATABASE_DIR / csv_file
        # Open file in 'a' (append) mode
        with open(csv_path, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)


            


    
 