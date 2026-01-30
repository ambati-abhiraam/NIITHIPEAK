import markdown
import pandas as pd
import io
import re

from column_indices import get_column_index
from row_indices import get_row_index

def sanitize_index(val):
    # Checks if val is an integer and NOT a boolean (since True/False act like 1/0)
    if isinstance(val, int) and not isinstance(val, bool):
        return val
    return -1

import re

def clean_financial_string(val):
    if not isinstance(val, str):
        return val # Already a number or None
    
    # 1. Check for parentheses to determine if it's a negative number
    # We strip whitespace and asterisks first to check the actual "content"
    temp_val = val.strip().replace("*", "")
    is_negative = temp_val.startswith('(') and temp_val.endswith(')')
    
    # 2. Remove everything except digits, dots, and minus signs
    clean_val = re.sub(r'[^\d.-]', '', val)
    
    try:
        num = float(clean_val)
        # 3. If we detected parentheses, multiply by -1
        return -abs(num) if is_negative else num
    except ValueError:
        return -2  # Flagging parsing errors

def get_values(markdown_file_path: str, pdf_file_name: str, target_date):

    data_json_3 = {
        "pdf_file_name": pdf_file_name,
        "this_quarter_revenue": -3,
        "previous_quarter_revenue": -3,
        "same_quarter_last_year_revenue": -3,
        "this_quarter_expenses": -3,
        "previous_quarter_expenses": -3,
        "same_quarter_last_year_expenses": -3,
        "this_quarter_comprehensive_income": -3,
        "previous_quarter_comprehensive_income": -3,
        "same_quarter_last_year_comprehensive_income": -3,
    }

    # Test with your second table structure
    #markdown_file_path = "saved_md_files/61f6f27d-bacf-4c9f-9357-2ac048fc1cf4_6.md"
    # 1. Load the markdown file content
    with open(markdown_file_path, 'r', encoding="utf-8") as f:
        text = f.read()
    # 2. Convert text to HTML (ensure 'tables' extension is included)
    table = markdown.markdown(text, extensions=['tables'])
    #print("table is ", table)
    if "<table" not in table.lower():
        print("Warning: No table structure found in the provided text.")
        return data_json_3  # Or return an empty pd.DataFrame()
    # 3. Parse HTML with Pandas
    # read_html returns a list of DataFrames, so we take the first one
    df = pd.read_html(io.StringIO(table))[0]
    #print(df)
    #print(df.iloc[0:4,:])
    

    #this_quarter_column, previous_quarter_column, same_q_last_year_column = get_column_index(df, debug=False)
    #print("*********************", this_quarter_column, previous_quarter_column, same_q_last_year_column)
    #revenue_row, expenses_row, pbt_row, comprehensive_income_row = get_row_index(df, debug=False)
    #print("*********************", revenue_row, expenses_row, pbt_row, comprehensive_income_row)
    
    # Apply to your columns
    this_quarter_column, previous_quarter_column, same_q_last_year_column = [
        sanitize_index(x) for x in get_column_index(df, target_date,debug=False)
    ]
    print("*********************", this_quarter_column, previous_quarter_column, same_q_last_year_column)


    # Apply to your rows
    revenue_row, expenses_row, pbt_row, comprehensive_income_row = [
        sanitize_index(x) for x in get_row_index(df, debug=False)
    ]
    print("*********************", revenue_row, expenses_row, pbt_row, comprehensive_income_row)

    data_json = {
        "pdf_file_name": pdf_file_name,
        "this_quarter_revenue": clean_financial_string(df.iat[revenue_row, this_quarter_column]),
        "previous_quarter_revenue": clean_financial_string(df.iat[revenue_row, previous_quarter_column]),
        "same_quarter_last_year_revenue": clean_financial_string(df.iat[revenue_row, same_q_last_year_column]),
        "this_quarter_expenses": clean_financial_string(df.iat[expenses_row, this_quarter_column]),
        "previous_quarter_expenses": clean_financial_string(df.iat[expenses_row, previous_quarter_column]),
        "same_quarter_last_year_expenses": clean_financial_string(df.iat[expenses_row, same_q_last_year_column]),
        "this_quarter_comprehensive_income": clean_financial_string(df.iat[comprehensive_income_row, this_quarter_column]),
        "previous_quarter_comprehensive_income": clean_financial_string(df.iat[comprehensive_income_row, previous_quarter_column]),
        "same_quarter_last_year_comprehensive_income": clean_financial_string(df.iat[comprehensive_income_row, same_q_last_year_column]),
    }

    return data_json









