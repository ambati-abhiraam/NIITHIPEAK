import pandas as pd
import os


#from create_folders import create_all_necessary_folders
from s0_saving_files_to_folder import get_files
#from engine import process_images
#from get_image import get_image_from_pdf
#from segmentor import images_segmentor
from  clean_csv import duplicate_remover 




#url_name_csv_path = "url_name.csv"
raw_csv = "../download_csv.csv"

duplicate_remover(raw_csv)


download_dir = "../pdf_files_unprocessed_500-1000"

get_files(raw_csv,download_dir)


#for pdf in os.listdir(download_dir):
#    pdf_file_path = os.path.join(download_dir, pdf)
    #print("processing file:", pdf_file_path)
#    img = get_image_from_pdf(pdf_file_path)
#    if img:
#        images_segmentor(img, pdf)