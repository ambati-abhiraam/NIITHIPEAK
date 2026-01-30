import pandas as pd



import requests
import os
import time
from urllib.parse import urlparse
import csv


def update_csv(url,filename, url_name_csv):
    data = {"file_name":filename,"url":url}
    field_names = ["file_name","url"]
    try:
        with open(url_name_csv, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            # If the file didn't exist before opening, write the header first
            file_exists = os.path.isfile(url_name_csv)
            if not file_exists:
                writer.writeheader()
                print(f"Created new file '{url_name_csv}' and wrote header.")
            # Write the single row
            writer.writerow(data)
            print(f"Successfully appended a new row to '{url_name_csv}'.")

    except Exception as e:
        print(f"Error processing {data}: {e}")




def get_files(list_file , download_dir ,url_name_csv):
    
    df = pd.read_csv(list_file)

    pdf_url = df["ATTACHMENT"].tolist()
    print(f"Total PDF URLs found: {len(pdf_url)}")
    # -------------------------------------------------
    # Settings
    # -------------------------------------------------
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,*/*;q=0.8',
        'Referer': 'https://www.nseindia.com/'
    }
    DOWNLOAD_DIR = download_dir
    TIMEOUT_SECONDS = 30          # <-- your 30-second limit
    RATE_LIMIT = 2                # seconds to wait between requests

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # -------------------------------------------------
    # Download loop with timeout
    # -------------------------------------------------
    for idx, url in enumerate(pdf_url, start=1):
        filename = os.path.join(DOWNLOAD_DIR, f"{idx:02d}_{url.split('/')[-1]}")
        print(f"\n[{idx}/{len(pdf_url)}] Trying → {url}")

        try:
            # `timeout` applies to *both* connect and read
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, stream=True)

            # Quick sanity checks
            if response.status_code != 200:
                print(f"  [Failed] HTTP {response.status_code}")
                continue

            if 'pdf' not in response.headers.get('Content-Type', '').lower():
                print(f"  [Failed] Not a PDF (type: {response.headers.get('Content-Type')})")
                continue

            # Write the file in chunks (still respects the timeout)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            #update_csv(url,filename, url_name_csv)
            size_kb = os.path.getsize(filename) / 1024
            #print(f"  [Success] Saved {filename} ({size_kb:.1f} KB)")

        except requests.exceptions.Timeout:
            print(f"  [Timeout] > {TIMEOUT_SECONDS}s – skipping")
        except requests.exceptions.RequestException as e:
            print(f"  [Failed] Error: {e}")
        except Exception as e:
            print(f"  [Failed] Unexpected: {e}")

        # Polite pause before the next request
        time.sleep(RATE_LIMIT)