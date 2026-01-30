

import re
import pandas as pd
from difflib import get_close_matches

# -----------------------------
# CONFIG - TARGET ROW PATTERNS
# -----------------------------
TARGET_ROW_PATTERNS = {
    "revenue_from_operations": {
        "keywords": ["revenue", "operations","from"],
        "min_matches": 2,  # At least 1 keyword must match
        "exclude": ["other"]
    },
    "total_expenses": {
        "keywords": ["total", "expense", "expenditure", "before"],
        "min_matches": 2,  # At least 2 keywords must match
        "exclude": []
    },
    "profit_before_tax": {
        "keywords": ["profit", "tax", "before"],
        "min_matches": 2,
        "exclude": ["comprehensive", "after"]
    },
    "total_comprehensive_income": {
        "keywords": ["total", "comprehensive", "income"],
        "min_matches": 3,
        "exclude": ["other"]
    }
}

# -----------------------------
# TEXT CLEANING
# -----------------------------
def clean_row_text(text: str) -> str:
    """Clean text for row matching"""
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove markdown formatting
    text = re.sub(r'\*\*|__|`', '', text)
    
    # Remove parentheses content like (Refer Note 5), (IV), etc
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove common prefixes like "a.", "(a)", "i.", "1.", etc
    text = re.sub(r'^[a-z]\.\s*', '', text)
    text = re.sub(r'^\([a-z]\)\s*', '', text)
    text = re.sub(r'^\d+\.\s*', '', text)
    
    # Normalize separators
    text = re.sub(r'[/]+', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# -----------------------------
# FUZZY MATCHING
# -----------------------------
def matches_pattern(text: str, pattern_config: dict, debug=False) -> bool:
    """Check if text matches pattern based on keyword count with fuzzy matching."""
    cleaned = clean_row_text(text)
    
    if debug:
        print(f"      Checking: '{text[:60]}...'")
        print(f"        Cleaned: '{cleaned[:60]}...'")
    
    # Check exclude keywords first
    exclude = pattern_config.get("exclude", [])
    for keyword in exclude:
        if keyword in cleaned:
            if debug:
                print(f"        ✗ Contains excluded keyword: '{keyword}'")
            return False
    
    # Count matching keywords (with fuzzy matching)
    keywords = pattern_config.get("keywords", [])
    min_matches = pattern_config.get("min_matches", len(keywords))
    
    matched_count = 0
    matched_keywords = []
    
    words_in_text = cleaned.split()
    
    for keyword in keywords:
        # Direct match - check if keyword is in the cleaned text
        if keyword in cleaned:
            matched_count += 1
            matched_keywords.append(keyword)
        # Fuzzy match for typos (e.g., "xpenses" matches "expenses")
        elif len(keyword) > 4:  # Only fuzzy match longer words to avoid false positives
            close = get_close_matches(keyword, words_in_text, n=1, cutoff=0.8)
            if close:
                matched_count += 1
                matched_keywords.append(f"{keyword}≈{close[0]}")
                if debug:
                    print(f"        ~ Fuzzy matched '{keyword}' to '{close[0]}'")
    
    if matched_count >= min_matches:
        if debug:
            print(f"        ✓ Match! ({matched_count}/{min_matches} keywords: {matched_keywords})")
        return True
    else:
        if debug:
            print(f"        ✗ Only {matched_count}/{min_matches} keywords matched: {matched_keywords}")
        return False

# -----------------------------
# MAIN FUNCTION - FIND FIRST OCCURRENCE
# -----------------------------
def find_row_indices(df, target_patterns=TARGET_ROW_PATTERNS, 
                     search_columns=5, max_rows=None, debug=True):
    """
    Find row index for first occurrence of each pattern across multiple columns.
    
    Args:
        df: pandas DataFrame
        target_patterns: dict of pattern configurations
        search_columns: number of columns to search (default 5)
        max_rows: max rows to search (None = search all)
        debug: print debug info
    
    Returns:
        dict: {pattern_name: row_index}
    """
    result = {}
    max_rows = max_rows or len(df)
    max_cols = min(search_columns, len(df.columns))
    
    if debug:
        print(f"Searching for row patterns in first {max_cols} columns...")
        print(f"Max rows to search: {max_rows}")
        print("="*70 + "\n")
    
    # For each target pattern, find FIRST occurrence
    for pattern_name, pattern_config in target_patterns.items():
        found = False
        
        if debug:
            print(f"Searching for: {pattern_name}")
            print(f"  Keywords: {pattern_config.get('keywords', [])}")
            print(f"  Min matches: {pattern_config.get('min_matches', 0)}")
            print(f"  Exclude: {pattern_config.get('exclude', [])}")
        
        # Scan rows (stop at first match)
        for row_idx in range(min(max_rows, len(df))):
            
            if found:
                break
            
            # Check across first N columns
            for col_idx in range(max_cols):
                cell = df.iloc[row_idx, col_idx]
                
                if pd.isna(cell):
                    continue
                
                cell_str = str(cell).strip()
                
                if not cell_str:
                    continue
                
                # Check if this cell matches the pattern
                if matches_pattern(cell_str, pattern_config, debug=debug):
                    result[pattern_name] = row_idx
                    found = True
                    
                    if debug:
                        print(f"  ✓ FOUND at Row {row_idx}, Col {col_idx}")
                        print(f"    Original text: '{cell_str[:80]}'\n")
                    
                    break  # Stop searching columns for this pattern
        
        if not found and debug:
            print(f"  ✗ Not found\n")
    
    if debug:
        print("="*70)
        print(f"Final result: {result}\n")
    
    return result

# -----------------------------
# CONVENIENCE FUNCTION
# -----------------------------
def get_row_indices(df, search_columns=5, debug=False):
    """
    Get row indices for common financial statement items.
    
    Args:
        df: pandas DataFrame
        search_columns: number of columns to search (default 5)
        debug: print debug info
    
    Returns:
        tuple: (revenue_row, expenses_row, pbt_row, comprehensive_income_row)
    """
    rows = find_row_indices(df, search_columns=search_columns, debug=debug)
    
    revenue_row = rows.get('revenue_from_operations')
    expenses_row = rows.get('total_expenses')
    pbt_row = rows.get('profit_before_tax')
    comprehensive_income_row = rows.get('total_comprehensive_income')
    
    return revenue_row, expenses_row, pbt_row, comprehensive_income_row

# -----------------------------
# DIAGNOSTIC HELPER
# -----------------------------
def show_dataframe_content(df, search_columns=5, max_rows=30):
    """Show what's actually in the DataFrame"""
    max_cols = min(search_columns, len(df.columns))
    max_rows = min(max_rows, len(df))
    
    #print("DataFrame Content (First columns and rows):")
    #print("="*70)
    
    for row_idx in range(max_rows):
        has_content = False
        row_str = f"Row {row_idx}: "
        
        for col_idx in range(max_cols):
            cell = df.iloc[row_idx, col_idx]
            if pd.notna(cell) and str(cell).strip():
                has_content = True
                row_str += f"[Col{col_idx}] '{str(cell)[:40]}...' | "
        
        if has_content:
            print(row_str)
    
    print("="*70 + "\n")

# -----------------------------
# USAGE EXAMPLE
# -----------------------------
def get_row_index(df, debug=False):
    # Test data
    #markdown_file_path = "saved_md_files/5a8846f6-e7e1-46e8-b1e1-c7973deb34d0_3.md"
    # 1. Load the markdown file content
    #with open(markdown_file_path, 'r') as f:
    #    text = f.read()
    # 2. Convert text to HTML (ensure 'tables' extension is included)
    #table = markdown.markdown(text, extensions=['tables'])
    # 3. Parse HTML with Pandas
    # read_html returns a list of DataFrames, so we take the first one
    #df = pd.read_html(io.StringIO(table))[0]
    #print(df.iloc[0:4,:])

    
    # Find rows with detailed debug
    rows = find_row_indices(df, search_columns=5, debug=False)
    
    #print("\nFinal Row Indices:")
    #print(f"revenue_from_operations_row = {rows.get('revenue_from_operations')}")
    #print(f"total_expenses_row = {rows.get('total_expenses')}")
    #print(f"profit_before_tax_row = {rows.get('profit_before_tax')}")
    #print(f"total_comprehensive_income_row = {rows.get('total_comprehensive_income')}")
    
    # Or use convenience function
    #print("\n" + "="*70 + "\n")
    revenue_row, expenses_row, pbt_row, comprehensive_income_row = get_row_indices(df, debug=False)
    #print("Using convenience function:")
    #print(f"revenue_row = {revenue_row}")
    #print(f"expenses_row = {expenses_row}")
    #print(f"pbt_row = {pbt_row}")
    #print(f"comprehensive_income_row = {comprehensive_income_row}")
    return revenue_row, expenses_row, pbt_row, comprehensive_income_row