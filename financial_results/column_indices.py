import re
import calendar
from datetime import date
from dateutil import parser
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
MAX_SCAN_ROWS = 6

TARGET_DATES = {
    "this_quarter": date(2025, 9, 30),
    "previous_quarter": date(2025, 6, 30),
    "same_q_last_year": date(2024, 9, 30)
}

# -----------------------------
# REGEX - ADDED MONTH-YEAR PATTERN
# -----------------------------
FULL_DATE_REGEX = re.compile(r'''
    \d{1,2}[./-]\d{1,2}[./-]\d{2,4}                     # 30.09.2025
    |
    \d{1,2}\s*[-]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*[-]\s*\d{2,4}  # 30-Sep-25
    |
    \d{1,2}(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4}  # 30th September, 2025
    |
    (January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4}  # September 30th, 2025
''', re.IGNORECASE | re.VERBOSE)

# NEW: Month-Year only pattern
MONTH_YEAR_REGEX = re.compile(r'''
    (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4}  # Sept, 2025 or Sept 2025
    |
    (January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4}  # September, 2025
''', re.IGNORECASE | re.VERBOSE)

MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}

# -----------------------------
# CLEANING
# -----------------------------
def clean_text(text: str) -> str:
    """Clean text while preserving date information"""
    if not isinstance(text, str):
        text = str(text)
    
    # Handle typos
    text = re.sub(r'3lst', '31st', text)
    text = re.sub(r'(\d)lst\b', r'\1st', text)
    
    # Normalize whitespace
    text = text.replace('\n', ' ').replace('\t', ' ')
    
    # Remove markdown and formatting
    text = re.sub(r'\*\*|__|`', '', text)
    
    # Remove audit annotations
    text = re.sub(r'\(?\s*(Unaudited|Audited)\s*\)?', ' ', text, flags=re.I)
    
    # Remove extra phrases (but keep ordinal suffixes for date extraction)
    text = re.sub(r'Quarter ended|Six Months ended|Year ended|ended|Refer note \d+', ' ', text, flags=re.I)
    
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# -----------------------------
# DATE EXTRACTION
# -----------------------------
def extract_all_date_strings(text: str):
    """Extract all potential date strings from text"""
    dates = []
    
    # First try to find full dates (with day)
    for match in FULL_DATE_REGEX.finditer(text):
        dates.append(match.group(0).strip())
    
    # If no full dates found, try month-year only
    if not dates:
        for match in MONTH_YEAR_REGEX.finditer(text):
            dates.append(match.group(0).strip())
    
    return dates

# -----------------------------
# DATE PARSING
# -----------------------------
def parse_date(date_str: str):
    """Parse date string to date object"""
    if not date_str:
        return None
    
    try:
        # Remove ordinal suffixes before parsing
        date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', date_str, flags=re.I)
        date_str_clean = date_str_clean.strip()
        
        # Try DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY format
        match = re.match(r'^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$', date_str_clean)
        if match:
            day, month, year = match.groups()
            year = int(year)
            if year < 100:
                year += 2000 if year < 50 else 1900
            return date(year, int(month), int(day))
        
        # Try DD-Month-YYYY format (30-September-2025)
        match = re.match(r'^(\d{1,2})\s*[-]\s*([A-Za-z]+)\s*[-]\s*(\d{2,4})$', date_str_clean)
        if match:
            day, month_str, year = match.groups()
            month_key = month_str[:4].lower()
            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
            if month:
                year = int(year)
                if year < 100:
                    year += 2000 if year < 50 else 1900
                return date(year, month, int(day))
        
        # Try DD Month YYYY format (30 September 2025 or 30 September, 2025)
        match = re.match(r'^(\d{1,2})\s+([A-Za-z]+)\s*,?\s*(\d{4})$', date_str_clean, re.I)
        if match:
            day, month_str, year = match.groups()
            month_key = month_str[:4].lower()
            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
            if month:
                return date(int(year), month, int(day))
        
        # Try Month DD YYYY format (September 30 2025 or September 30, 2025)
        match = re.match(r'^([A-Za-z]+)\s+(\d{1,2})\s*,?\s*(\d{4})$', date_str_clean, re.I)
        if match:
            month_str, day, year = match.groups()
            month_key = month_str[:4].lower()
            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
            if month:
                return date(int(year), month, int(day))
        
        # Try Month YYYY format (Sept, 2025 or September 2025) - infer last day of month
        match = re.match(r'^([A-Za-z]+)\s*,?\s*(\d{4})$', date_str_clean, re.I)
        if match:
            month_str, year = match.groups()
            month_key = month_str[:4].lower()
            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
            if month:
                year = int(year)
                # Get last day of the month
                last_day = calendar.monthrange(year, month)[1]
                return date(year, month, last_day)
        
        # Fallback to dateutil
        dt = parser.parse(date_str_clean, dayfirst=True, fuzzy=True)
        return dt.date()
        
    except Exception as e:
        return None

# -----------------------------
# MAIN FUNCTION - SCAN HEADERS AND ROWS
# -----------------------------
def find_date_columns(df, target_dates, max_rows=MAX_SCAN_ROWS, debug=False):
    """
    Scan column headers AND first few rows to find which column contains each target date.
    
    Args:
        df: pandas DataFrame
        target_dates: dict of {name: date_object}
        max_rows: number of rows to scan
        debug: print debug information
    
    Returns:
        dict: {date_name: column_index}
    """
    result = {}
    
    if debug:
        print(f"Scanning column headers and first {max_rows} rows...")
        print(f"Looking for dates: {target_dates}")
        print("="*70 + "\n")
    
    # STEP 1: Scan column headers
    if debug:
        print("STEP 1: Scanning column headers...")
    
    for col_idx, col_name in enumerate(df.columns):
        col_str = str(col_name)
        cleaned = clean_text(col_str)
        
        if debug:
            print(f"Column {col_idx}: '{col_str}'")
        
        date_strings = extract_all_date_strings(cleaned)
        
        if date_strings:
            if debug:
                print(f"  Found date strings: {date_strings}")
            
            for date_str in date_strings:
                parsed_date = parse_date(date_str)
                
                if debug and parsed_date:
                    print(f"  Parsed '{date_str}' → {parsed_date}")
                
                if parsed_date:
                    for date_name, target_date in target_dates.items():
                        if parsed_date == target_date and date_name not in result:
                            result[date_name] = col_idx
                            if debug:
                                print(f"  ✓ MATCH! {date_name} found in column {col_idx}")
    
    # STEP 2: Scan first few rows (for multi-row headers)
    if debug:
        print(f"\nSTEP 2: Scanning first {max_rows} rows...")
    
    for row_idx in range(min(max_rows, len(df))):
        if debug:
            print(f"\nRow {row_idx}:")
        
        for col_idx in range(len(df.columns)):
            cell = df.iloc[row_idx, col_idx]
            
            # Skip NaN and non-string cells
            if pd.isna(cell):
                continue
            
            cell_str = str(cell)
            cleaned = clean_text(cell_str)
            
            if not cleaned:
                continue
            
            # Look for dates
            date_strings = extract_all_date_strings(cleaned)
            
            if date_strings:
                if debug:
                    print(f"  Col {col_idx}: '{cell_str[:60]}...' → found {date_strings}")
                
                for date_str in date_strings:
                    parsed_date = parse_date(date_str)
                    
                    if debug and parsed_date:
                        print(f"    Parsed '{date_str}' → {parsed_date}")
                    
                    if parsed_date:
                        for date_name, target_date in target_dates.items():
                            if parsed_date == target_date and date_name not in result:
                                result[date_name] = col_idx
                                if debug:
                                    print(f"    ✓ MATCH! {date_name} found in column {col_idx}")
        
        # Early exit if all found
        if len(result) == len(target_dates):
            if debug:
                print("\nAll dates found! Stopping scan.")
            break
    
    if debug:
        print("\n" + "="*70)
        print(f"Final result: {result}\n")
    
    return result

# -----------------------------
# CONVENIENCE FUNCTION
# -----------------------------
def get_column_indices(df, target_date,max_rows=MAX_SCAN_ROWS, debug=False):
    """
    Get column indices for target dates.
    
    Returns:
        tuple: (this_quarter_column, previous_quarter_column, same_q_last_year_column)
    """
    columns = find_date_columns(df, target_date,max_rows=max_rows, debug=debug)
    
    this_quarter_column = columns.get('this_quarter')
    previous_quarter_column = columns.get('previous_quarter')
    same_q_last_year_column = columns.get('same_q_last_year')
    
    return this_quarter_column, previous_quarter_column, same_q_last_year_column

# -----------------------------
# USAGE
# -----------------------------
def get_column_index(df, target_date,debug=False):
    """Main function to get column indices"""
    
    # Find columns
    columns = find_date_columns(df, target_date,debug=debug)
    
    # Get individual variables
    this_quarter_column, previous_quarter_column, same_q_last_year_column = get_column_indices(df, target_date,debug=debug)

    return this_quarter_column, previous_quarter_column, same_q_last_year_column