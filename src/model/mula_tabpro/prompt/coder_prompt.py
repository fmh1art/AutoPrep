DEMO_CODER = """Generate python code given the question and table to process the table.

/*
"date": "october 19" | "july 13 2009" | "september 23 governor's cup"
*/
Requirement: please standardize the column `date` to sortable datetime format.
Code: ```def process_function(date_str):
    try:
        parsed_date = parse(date_str, fuzzy=True)
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        return None

df['date'] = df['date'].apply(process_function)
```

/*
"notes": "5000" | "5000" | "10,000" | "10,000" | "10000" | "10,000"
*/
Requirement: please standardize the column `notes` to numerical format.
Code: ```def convert_to_numeric(value):
    return int(value.replace(',', ''))

df['notes'] = df['notes'].apply(convert_to_numeric)```

/*
"career_win_loss": "22-88" | "nan" | "17-20" | "11-14"
*/
Requirement: Given the column `career_win_loss` please generate a new column to answer "how many wins?"
Code: ```def extract_wins(win_loss_str):
    if pd.isna(win_loss_str):
        return np.nan
    try:
        wins, _ = map(int, win_loss_str.split('-'))
        return wins
    except ValueError:
        return np.nan

df['wins'] = df['career_win_loss'].apply(extract_wins)```

/*
"enter_office": "1996-99" | "1998-2002" | "2000-04" | "2002-06" | "2004-08"
*/
Requirement: Given the column `enter_office` please generate a new column to answer "how many years in office?"
Code: ```def calculate_years_in_office(period):
    start, end = period.split('-')
    start_year = int(start)
    end_year = int(end)
    if len(str(end_year)) == 2:
        end_year += 2000
    return end_year - start_year + 1

df['years_in_office'] = df['enter_office'].apply(calculate_years_in_office)```

/*
"year": 2005 | 2010 | 2007 | 2009
"month": 5 | 5 | [n.a.] | 12
"day": 4 | 22 | 1 | 31
*/
Requirement: Given the column `year`, `month`, `day` please generate a new column to answer "what is the date?"
Code: ```def handle_missing_month(month):
    if month == '[n.a.]':
        return None
    return int(month)

df['month'] = df['month'].apply(handle_missing_month)

df['date'] = pd.to_datetime(df[['year', 'month', 'day']].astype(str).replace('\.0', '', regex=True), errors='coerce')

df.dropna(subset=['date'], inplace=True)```

/*
"term": "1859-1864" | "?-1880" | "1864-1869" | "1869-1880"
*/
Requirement: Given the column `term` please generate a new column to answer "how long does it last?"
Code: ```def calculate_term_duration(term):
    if '-' in term:
        start, end = term.split('-')
        if start == '?':
            return None 
        start_year = int(start)
        end_year = int(end)
        return end_year - start_year + 1
    return None 

df['duration'] = df['term'].apply(calculate_term_duration)```

/*
"prominence": "10080 ft; 3072 m" | "1677 ft; 511 m" | "7196 ft; 2193 m" | 10000 | 10000 | 10000
*/
Requirement: Given the column `prominence` please generate a new column to answer "prominence in ft?"
Code: ```def extract_prominence_in_ft(prominence):
    if isinstance(prominence, str):
        match = re.search(r'(\d+)\s*ft', prominence)
        if match:
            return int(match.group(1))
    elif isinstance(prominence, (int, float)):
        return int(prominence)
    return None

df['prominence_in_ft'] = df['prominence'].apply(extract_prominence_in_ft)```"""

QUERY_CODER = """Please complete the following prompt.

/*
{table}
*/
Requirement: {requirement}
Code:"""