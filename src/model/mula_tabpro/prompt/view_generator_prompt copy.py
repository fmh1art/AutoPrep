from global_values import NAMES

PROMPT_VIEW_GENERATOR = {
    f"head": f"You are a agent to generate a new column.",
    
    # description for {NAMES['GEN_NEW_COL']}
    f"{NAMES['GEN_NEW_COL']}": f"""The operator `{NAMES['GEN_NEW_COL']}` aims to generate a new column based on the existing column(s). We use the operator by specifying the arguments `new_column` and the `func` function.""",

    # demo for {NAMES['GEN_NEW_COL']}
    f"demo_{NAMES['GEN_NEW_COL']}_from_column": f"""Here are example of using the operator `{NAMES['GEN_NEW_COL']}`,

/*
"career_win_loss": "22-88" | "nan" | "17-20" | "11-14"
*/
Given the column `career_win_loss` please generate a new column to answer: how many wins?
Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="win_number", func=lambda x: int(str(x['career_win_loss']).split('-')[0]) if '-' in str(x['career_win_loss']) else '[n.a.]')```

/*
"enter_office": "1996-99" | "1998-2002" | "2000-04" | "2002-06" | "2004-08"
*/
Given the column `enter_office` please generate a new column to answer: how many years in office?
Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="years_in_office", func=lambda x: (int(str(x['enter_office']).split('-')[1][-2:]) - int(str(x['enter_office']).split('-')[0][-2:]))%100)```

/*
"term": "1859-1864" | "?-1880" | "1864-1869" | "1869-1880"
*/
Given the column `term` please generate a new column to answer: how long does it last?
Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="duration", func=lambda x: int(str(x['term']).split('-')[1]) - int(str(x['term']).split('-')[0]))```

/*
"prominence": "10080 ft; 3072 m" | "1677 ft; 511 m" | "7196 ft; 2193 m" | 10000 | 10000 | 10000
*/
Given the column `prominence` please generate a new column to answer: prominence in ft?
Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="prominence_ft", func=lambda x: int(str(x['prominence']).split(';')[0].split(' ')[0]) if ';' in str(x['prominence']) else '[n.a.]')```

/*
"place": "søfteland , norway" | "nan" | "york , united kingdom" | "burrator , united kingdom"
*/
Given the column `place` please generate a new column to answer: is it in united kingdom?
Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="in_uk", func=lambda x: 'united kingdom' in str(x['place']))```""",

    # query for {NAMES['GEN_NEW_COL']}_from_column
    f"query_{NAMES['GEN_NEW_COL']}_from_column": """Please complete the following prompt.

/*
{table}
*/
Given the column {col} please generate a new column to answer: {question}
Operator:""",

    "self_correc_ins": """/*
{context}
*/
Requirement: {question}
Last Error: {last_error}
Operator: {a}"""
}
