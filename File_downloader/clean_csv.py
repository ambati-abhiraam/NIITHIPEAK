import pandas as pd

#raw_csv = "../download_csv.csv"

def duplicate_remover(raw_csv):
    try:
        # 1. Load the CSV
        df = pd.read_csv(raw_csv)
        
        # 2. Remove duplicates based on the "ATTACHMENT" column
        # 'keep=first' ensures we stay with the original entry and toss the copies
        df_cleaned = df.drop_duplicates(subset=['ATTACHMENT'], keep='first')
        
        # 3. Overwrite the original CSV file
        df_cleaned.to_csv(raw_csv, index=False)
        
        print(f"Success! Cleaned file saved to {raw_csv}")
        print(f"Rows removed: {len(df) - len(df_cleaned)}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
# clean_attachment_duplicates('your_data_file.csv')