#import re
#import calendar
#from datetime import date
#from dateutil import parser
#import pandas as pd
#
## -----------------------------
## CONFIG
## -----------------------------
#MAX_SCAN_ROWS = 6
#
##TARGET_DATES = {
##    "this_quarter": date(2025, 9, 30),
##    "previous_quarter": date(2025, 6, 30),
##    "same_q_last_year": date(2024, 9, 30)
##}
#
## -----------------------------
## REGEX - ADDED MONTH-YEAR PATTERN
## -----------------------------
#FULL_DATE_REGEX = re.compile(r'''
#    \d{1,2}[./-]\d{1,2}[./-]\d{2,4}                     # 30.09.2025
#    |
#    \d{1,2}\s*[-]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*[-]\s*\d{2,4}  # 30-Sep-25
#    |
#    \d{1,2}(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4}  # 30th September, 2025
#    |
#    (January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4}  # September 30th, 2025
#''', re.IGNORECASE | re.VERBOSE)
#
## NEW: Month-Year only pattern
#MONTH_YEAR_REGEX = re.compile(r'''
#    (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4}  # Sept, 2025 or Sept 2025
#    |
#    (January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4}  # September, 2025
#''', re.IGNORECASE | re.VERBOSE)
#
#MONTH_MAP = {
#    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
#    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
#    'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
#    'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
#}
#
## -----------------------------
## CLEANING
## -----------------------------
#def clean_text(text: str) -> str:
#    """Clean text while preserving date information"""
#    if not isinstance(text, str):
#        text = str(text)
#    
#    # Handle typos
#    text = re.sub(r'3lst', '31st', text)
#    text = re.sub(r'(\d)lst\b', r'\1st', text)
#    
#    # Normalize whitespace
#    text = text.replace('\n', ' ').replace('\t', ' ')
#    
#    # Remove markdown and formatting
#    text = re.sub(r'\*\*|__|`', '', text)
#    
#    # Remove audit annotations
#    text = re.sub(r'\(?\s*(Unaudited|Audited)\s*\)?', ' ', text, flags=re.I)
#    
#    # Remove extra phrases (but keep ordinal suffixes for date extraction)
#    text = re.sub(r'Quarter ended|Six Months ended|Year ended|ended|Refer note \d+', ' ', text, flags=re.I)
#    
#    # Normalize spaces
#    text = re.sub(r'\s+', ' ', text)
#    
#    return text.strip()
#
## -----------------------------
## DATE EXTRACTION
## -----------------------------
#def extract_all_date_strings(text: str):
#    """Extract all potential date strings from text"""
#    dates = []
#    
#    # First try to find full dates (with day)
#    for match in FULL_DATE_REGEX.finditer(text):
#        dates.append(match.group(0).strip())
#    
#    # If no full dates found, try month-year only
#    if not dates:
#        for match in MONTH_YEAR_REGEX.finditer(text):
#            dates.append(match.group(0).strip())
#    
#    return dates
#
## -----------------------------
## DATE PARSING
## -----------------------------
#def parse_date(date_str: str):
#    """Parse date string to date object"""
#    if not date_str:
#        return None
#    
#    try:
#        # Remove ordinal suffixes before parsing
#        date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', date_str, flags=re.I)
#        date_str_clean = date_str_clean.strip()
#        
#        # Try DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY format
#        match = re.match(r'^(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})$', date_str_clean)
#        if match:
#            day, month, year = match.groups()
#            year = int(year)
#            if year < 100:
#                year += 2000 if year < 50 else 1900
#            return date(year, int(month), int(day))
#        
#        # Try DD-Month-YYYY format (30-September-2025)
#        match = re.match(r'^(\d{1,2})\s*[-]\s*([A-Za-z]+)\s*[-]\s*(\d{2,4})$', date_str_clean)
#        if match:
#            day, month_str, year = match.groups()
#            month_key = month_str[:4].lower()
#            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
#            if month:
#                year = int(year)
#                if year < 100:
#                    year += 2000 if year < 50 else 1900
#                return date(year, month, int(day))
#        
#        # Try DD Month YYYY format (30 September 2025 or 30 September, 2025)
#        match = re.match(r'^(\d{1,2})\s+([A-Za-z]+)\s*,?\s*(\d{4})$', date_str_clean, re.I)
#        if match:
#            day, month_str, year = match.groups()
#            month_key = month_str[:4].lower()
#            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
#            if month:
#                return date(int(year), month, int(day))
#        
#        # Try Month DD YYYY format (September 30 2025 or September 30, 2025)
#        match = re.match(r'^([A-Za-z]+)\s+(\d{1,2})\s*,?\s*(\d{4})$', date_str_clean, re.I)
#        if match:
#            month_str, day, year = match.groups()
#            month_key = month_str[:4].lower()
#            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
#            if month:
#                return date(int(year), month, int(day))
#        
#        # Try Month YYYY format (Sept, 2025 or September 2025) - infer last day of month
#        match = re.match(r'^([A-Za-z]+)\s*,?\s*(\d{4})$', date_str_clean, re.I)
#        if match:
#            month_str, year = match.groups()
#            month_key = month_str[:4].lower()
#            month = MONTH_MAP.get(month_key) or MONTH_MAP.get(month_str.lower())
#            if month:
#                year = int(year)
#                # Get last day of the month
#                last_day = calendar.monthrange(year, month)[1]
#                return date(year, month, last_day)
#        
#        # Fallback to dateutil
#        dt = parser.parse(date_str_clean, dayfirst=True, fuzzy=True)
#        return dt.date()
#        
#    except Exception as e:
#        return None
#
## -----------------------------
## MAIN FUNCTION - SCAN HEADERS AND ROWS
## -----------------------------
#def find_date_columns(df, target_dates, max_rows=MAX_SCAN_ROWS, debug=False):
#    """
#    Scan column headers AND first few rows to find which column contains each target date.
#    
#    Args:
#        df: pandas DataFrame
#        target_dates: dict of {name: date_object}
#        max_rows: number of rows to scan
#        debug: print debug information
#    
#    Returns:
#        dict: {date_name: column_index}
#    """
#    result = {}
#    
#    if debug:
#        print(f"Scanning column headers and first {max_rows} rows...")
#        print(f"Looking for dates: {target_dates}")
#        print("="*70 + "\n")
#    
#    # STEP 1: Scan column headers
#    if debug:
#        print("STEP 1: Scanning column headers...")
#    
#    for col_idx, col_name in enumerate(df.columns):
#        col_str = str(col_name)
#        cleaned = clean_text(col_str)
#        
#        if debug:
#            print(f"Column {col_idx}: '{col_str}'")
#        
#        date_strings = extract_all_date_strings(cleaned)
#        
#        if date_strings:
#            if debug:
#                print(f"  Found date strings: {date_strings}")
#            
#            for date_str in date_strings:
#                parsed_date = parse_date(date_str)
#                
#                if debug and parsed_date:
#                    print(f"  Parsed '{date_str}' → {parsed_date}")
#                
#                if parsed_date:
#                    for date_name, target_date in target_dates.items():
#                        if parsed_date == target_date and date_name not in result:
#                            result[date_name] = col_idx
#                            if debug:
#                                print(f"  ✓ MATCH! {date_name} found in column {col_idx}")
#    
#    # STEP 2: Scan first few rows (for multi-row headers)
#    if debug:
#        print(f"\nSTEP 2: Scanning first {max_rows} rows...")
#    
#    for row_idx in range(min(max_rows, len(df))):
#        if debug:
#            print(f"\nRow {row_idx}:")
#        
#        for col_idx in range(len(df.columns)):
#            cell = df.iloc[row_idx, col_idx]
#            
#            # Skip NaN and non-string cells
#            if pd.isna(cell):
#                continue
#            
#            cell_str = str(cell)
#            cleaned = clean_text(cell_str)
#            
#            if not cleaned:
#                continue
#            
#            # Look for dates
#            date_strings = extract_all_date_strings(cleaned)
#            
#            if date_strings:
#                if debug:
#                    print(f"  Col {col_idx}: '{cell_str[:60]}...' → found {date_strings}")
#                
#                for date_str in date_strings:
#                    parsed_date = parse_date(date_str)
#                    
#                    if debug and parsed_date:
#                        print(f"    Parsed '{date_str}' → {parsed_date}")
#                    
#                    if parsed_date:
#                        for date_name, target_date in target_dates.items():
#                            if parsed_date == target_date and date_name not in result:
#                                result[date_name] = col_idx
#                                if debug:
#                                    print(f"    ✓ MATCH! {date_name} found in column {col_idx}")
#        
#        # Early exit if all found
#        if len(result) == len(target_dates):
#            if debug:
#                print("\nAll dates found! Stopping scan.")
#            break
#    
#    if debug:
#        print("\n" + "="*70)
#        print(f"Final result: {result}\n")
#    
#    return result
#
## -----------------------------
## CONVENIENCE FUNCTION
## -----------------------------
#def get_column_indices(df, target_date,max_rows=MAX_SCAN_ROWS, debug=False):
#    """
#    Get column indices for target dates.
#    
#    Returns:
#        tuple: (this_quarter_column, previous_quarter_column, same_q_last_year_column)
#    """
#    columns = find_date_columns(df, target_date,max_rows=max_rows, debug=debug)
#    
#    this_quarter_column = columns.get('this_quarter')
#    previous_quarter_column = columns.get('previous_quarter')
#    same_q_last_year_column = columns.get('same_q_last_year')
#    
#    return this_quarter_column, previous_quarter_column, same_q_last_year_column
#
## -----------------------------
## USAGE
## -----------------------------
#def get_column_index(df, target_date,debug=False):
#    """Main function to get column indices"""
#    
#    # Find columns
#    columns = find_date_columns(df, target_date,debug=debug)
#    
#    # Get individual variables
#    this_quarter_column, previous_quarter_column, same_q_last_year_column = get_column_indices(df, target_date,debug=debug)
#
#    return this_quarter_column, previous_quarter_column, same_q_last_year_column







###################################################################################################################


import re
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
MAX_SCAN_ROWS = 6

# Month name variations
MONTH_NAMES = {
    1: ['jan', 'january', '1', '01'],
    2: ['feb', 'february', '2', '02'],
    3: ['mar', 'march', '3', '03'],
    4: ['apr', 'april', '4', '04'],
    5: ['may', '5', '05'],
    6: ['jun', 'june', '6', '06'],
    7: ['jul', 'july', '7', '07'],
    8: ['aug', 'august', '8', '08'],
    9: ['sep', 'sept', 'september', '9', '09'],
    10: ['oct', 'october', '10'],
    11: ['nov', 'november', '11'],
    12: ['dec', 'december', '12']
}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def clean_text(text):
    """Clean text and convert to lowercase for matching"""
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep numbers and letters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def contains_component(text, component):
    """
    Check if text contains a component (number or word).
    Component can be a single value or a list of alternatives.
    """
    if not text:
        return False
    
    # If component is a list, check if any variant matches
    if isinstance(component, list):
        return any(contains_component(text, var) for var in component)
    
    # Convert component to string and clean it
    component_str = str(component).lower().strip()
    
    # Check for word boundary match (avoid partial matches like "1" matching "12")
    pattern = r'\b' + re.escape(component_str) + r'\b'
    return bool(re.search(pattern, text))


def search_tier1(text, day, month_variants, year_variants):
    """
    Tier 1 search: day + month + year
    Returns True if all three components are found
    """
    has_day = contains_component(text, str(day))
    has_month = contains_component(text, month_variants)
    has_year = contains_component(text, year_variants)
    
    return has_day and has_month and has_year


def search_tier2(text, month_variants, year_variants):
    """
    Tier 2 search: month + year only
    Returns True if both components are found
    """
    has_month = contains_component(text, month_variants)
    has_year = contains_component(text, year_variants)
    
    return has_month and has_year


def find_column_for_date(df, day, month, year, max_rows=MAX_SCAN_ROWS, debug=False):
    """
    Find column containing a specific date using two-tier search.
    
    Args:
        df: pandas DataFrame
        day: day of month (e.g., 31)
        month: month number (e.g., 12 for December)
        year: full year (e.g., 2025)
        max_rows: number of rows to scan
        debug: print debug information
    
    Returns:
        column index (int) or None if not found
    """
    # Get month name variations
    month_variants = MONTH_NAMES.get(month, [])
    
    # Year variations (e.g., 2025 and 25)
    year_short = str(year)[-2:]  # Last 2 digits
    year_variants = [str(year), year_short]
    
    if debug:
        print(f"\nSearching for date: {day}/{month}/{year}")
        print(f"  Day: {day}")
        print(f"  Month variants: {month_variants}")
        print(f"  Year variants: {year_variants}")
        print("="*70)
    
    # -------------------------
    # TIER 1 SEARCH: day + month + year
    # -------------------------
    if debug:
        print("\nTIER 1: Searching for [day + month + year]...")
    
    # Search in column headers
    for col_idx, col_name in enumerate(df.columns):
        cleaned = clean_text(str(col_name))
        if search_tier1(cleaned, day, month_variants, year_variants):
            if debug:
                print(f"  ✓ FOUND in column header {col_idx}: '{col_name}'")
            return col_idx
    
    # Search in first few rows
    for row_idx in range(min(max_rows, len(df))):
        for col_idx in range(len(df.columns)):
            cell = df.iloc[row_idx, col_idx]
            if pd.isna(cell):
                continue
            
            cleaned = clean_text(str(cell))
            if search_tier1(cleaned, day, month_variants, year_variants):
                if debug:
                    print(f"  ✓ FOUND in row {row_idx}, column {col_idx}: '{cell}'")
                return col_idx
    
    if debug:
        print("  ✗ Not found in Tier 1")
    
    # -------------------------
    # TIER 2 SEARCH: month + year only (fallback)
    # -------------------------
    if debug:
        print("\nTIER 2: Searching for [month + year] only...")
    
    # Search in column headers
    for col_idx, col_name in enumerate(df.columns):
        cleaned = clean_text(str(col_name))
        if search_tier2(cleaned, month_variants, year_variants):
            if debug:
                print(f"  ✓ FOUND in column header {col_idx}: '{col_name}'")
            return col_idx
    
    # Search in first few rows
    for row_idx in range(min(max_rows, len(df))):
        for col_idx in range(len(df.columns)):
            cell = df.iloc[row_idx, col_idx]
            if pd.isna(cell):
                continue
            
            cleaned = clean_text(str(cell))
            if search_tier2(cleaned, month_variants, year_variants):
                if debug:
                    print(f"  ✓ FOUND in row {row_idx}, column {col_idx}: '{cell}'")
                return col_idx
    
    if debug:
        print("  ✗ Not found in Tier 2")
        print("\n" + "="*70)
    
    return None


# -----------------------------
# MAIN FUNCTION
# -----------------------------

def find_date_columns(df, target_dates, max_rows=MAX_SCAN_ROWS, debug=False):
    """
    Find columns for multiple target dates.
    
    Args:
        df: pandas DataFrame
        target_dates: dict of {name: (day, month, year)}
                     Example: {"this_quarter": (31, 12, 2025)}
        max_rows: number of rows to scan
        debug: print debug information
    
    Returns:
        dict: {date_name: column_index}
    """
    result = {}
    
    if debug:
        print(f"\nScanning DataFrame with {len(df.columns)} columns, {len(df)} rows")
        print(f"Will scan headers + first {max_rows} rows")
        print(f"Target dates: {target_dates}")
    
    for date_name, (day, month, year) in target_dates.items():
        if debug:
            print(f"\n{'='*70}")
            print(f"Looking for: {date_name} = {day}/{month}/{year}")
        
        col_idx = find_column_for_date(df, day, month, year, max_rows, debug)
        
        if col_idx is not None:
            result[date_name] = col_idx
            if debug:
                print(f"\n✓✓✓ {date_name} FOUND at column {col_idx}")
        else:
            if debug:
                print(f"\n✗✗✗ {date_name} NOT FOUND")
    
    if debug:
        print(f"\n{'='*70}")
        print(f"Final result: {result}\n")
    
    return result


# -----------------------------
# CONVENIENCE FUNCTIONS
# -----------------------------

def get_column_index(df, target_dates, max_rows=MAX_SCAN_ROWS, debug=False):
    """
    Get column indices for target dates.
    
    Args:
        df: pandas DataFrame
        target_dates: dict with keys 'this_quarter', 'previous_quarter', 'same_q_last_year'
                     Each value is a tuple of (day, month, year)
    
    Returns:
        tuple: (this_quarter_column, previous_quarter_column, same_q_last_year_column)
    """
    columns = find_date_columns(df, target_dates, max_rows, debug)
    
    this_quarter_column = columns.get('this_quarter')
    previous_quarter_column = columns.get('previous_quarter')
    same_q_last_year_column = columns.get('same_q_last_year')
    
    return this_quarter_column, previous_quarter_column, same_q_last_year_column


#def get_column_index(df, target_dates, debug=False):
#    """
#    Main function to get column indices.
#    
#    Args:
#        df: pandas DataFrame
#        target_dates: dict with keys 'this_quarter', 'previous_quarter', 'same_q_last_year'
#                     Each value is a tuple of (day, month, year)
#                     Example: {
#                         "this_quarter": (31, 12, 2025),
#                         "previous_quarter": (30, 9, 2025),
#                         "same_q_last_year": (31, 12, 2024)
#                     }
#        debug: print debug information
#    
#    Returns:
#        tuple: (this_quarter_column, previous_quarter_column, same_q_last_year_column)
#    
#    Example:
#        >>> TARGET_DATES = {
#        ...     "this_quarter": (31, 12, 2025),
#        ...     "previous_quarter": (30, 9, 2025),
#        ...     "same_q_last_year": (31, 12, 2024)
#        ... }
#        >>> col1, col2, col3 = get_column_index(df, TARGET_DATES, debug=True)
#    """
#    return get_column_indices(df, target_dates, debug=debug)


# -----------------------------
# EXAMPLE USAGE
# -----------------------------

#if __name__ == "__main__":
#    # Example: Create a sample DataFrame
#    data = {
#        'Metric': ['Revenue', 'Expenses', 'Profit'],
#        'Q3-2025 (30-Sep-25)': [100, 60, 40],
#        'Dec 2025': [120, 70, 50],
#        '31/12/2024': [90, 55, 35]
#    }
#    df = pd.DataFrame(data)
#    
#    print("Sample DataFrame:")
#    print(df)
#    print("\n")
#    
#    # Define target dates (day, month, year)
#    TARGET_DATES = {
#        "this_quarter": (31, 12, 2025),        # Q4 2025
#        "previous_quarter": (30, 9, 2025),     # Q3 2025
#        "same_q_last_year": (31, 12, 2024)     # Q4 2024
#    }
#    
#    # Find columns
#    col1, col2, col3 = get_column_index(df, TARGET_DATES, debug=True)
#    
#    print("\n" + "="*70)
#    print("RESULTS:")
#    print(f"  This Quarter (31/12/2025): Column {col1}")
#    print(f"  Previous Quarter (30/9/2025): Column {col2}")
#    print(f"  Same Q Last Year (31/12/2024): Column {col3}")