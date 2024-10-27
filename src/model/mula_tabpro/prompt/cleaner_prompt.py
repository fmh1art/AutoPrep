
import global_values as GV

PROMPT_CLEANER = {

    # description for {GV.NAMES['STAND_DATETIME']}
    f"{GV.NAMES['STAND_DATETIME']}": f"""The operator `{GV.NAMES['STAND_DATETIME']}` aims to standardize the datetime format. We use the operator by specifying the arguments `column` and the format string `format`. Remember, only use the operators to standardize datetime-value column.""",

    # description for {GV.NAMES['STAND_NUMERICAL']}
    f"{GV.NAMES['STAND_NUMERICAL']}": f"""The operator `{GV.NAMES['STAND_NUMERICAL']}` aims to standardize the numerical column. We use the operator by specifying the arguments `column` and the lambda function `func`.""",

    # demo for {GV.NAMES['STAND_DATETIME']}
    f"demo_{GV.NAMES['STAND_DATETIME']}": f"""Here are some examples of using the operator `{GV.NAMES['STAND_DATETIME']}`,

/*
"date": "october 19" | "july 13 2009" | "september 23 governor's cup"
*/
Requirement: please standardize the column `date` to datetime format.
Operator: ```{GV.NAMES['STAND_DATETIME']}(df, column='date', format='%B %d %Y')```

/*
"kickoff": "7:05pm" | "3:05pm" | "7:35pm" | "7:05pm" | "7:05pm"
*/
Requirement: please standardize the column `kickoff` to datetime format.
Operator: ```{GV.NAMES['STAND_DATETIME']}(df, column='kickoff', format='%I:%M%p')```

/*
"date": "1958" | "july 20, 1953" | "1950" | "1950" | "1948" | "1948"
*/
Requirement: please standardize the column `date` to datetime format.
Operator: ```{GV.NAMES['STAND_DATETIME']}(df, column='date', format='%B %d %Y')```
""",

    # demo for {GV.NAMES['STAND_NUMERICAL']}
    f"demo_{GV.NAMES['STAND_NUMERICAL']}": f"""Here are some examples of using the operator `{GV.NAMES['STAND_NUMERICAL']}`,

/*
"notes": "5000" | "5000" | "10,000" | "10,000" | "10000" | "10,000"
*/
Requirement: lease standardize the column `notes` to numerical format.
Operator: ```{GV.NAMES['STAND_NUMERICAL']}(df, column='notes', func=lambda x: int(x.replace(',', '')))```

/*
"score": "25 pt" | "30 pt" | "20 pt" | "15 pt" | "10 pt"
*/
Requirement: please standardize the column `score` to numerical format.
Operator: ```{GV.NAMES['STAND_NUMERICAL']}(df, score='date', func=lambda x: int(x.replace('pt', '').strip()))```

/*
"notes": 1 episode | 1 episode | 119 episodes | 13 episodes | voice<br>3 episodes | episode: \drugs are bad | [n.a.] | season 3 episode 24 'to tell the truth'
*/
Requirement: please standardize the column `notes` to numerical format.
Operator: ```{GV.NAMES['STAND_NUMERICAL']}(df, column='notes', func=lambda x: int(re.search(r'\d+ ', x).group() if 'episodes' in x else 1 if 'episode' in x else '[n.a.]'))```""",

    # query for total standardize
    f"tol_standardize_query": """Given the column and the requirement, please use the operator `{op1}` or `{op2}` to standardize the column to the required format.
/*
{cot_tbl}
*/
Requirement: {req}.
Output ```operator_with_args``` with NO other texts.
Operator:""",
    
    # standarize query
    f"standardize_query": """Given the column and the requirement, please use the operator `{op_name}` to standardize the column to the required format.

/*
{cot_tbl}
*/
Requirement: please standardize the column `{column}` to {format} format.
Output ```operator_with_args``` with NO other texts.
Operator:""",

    f"self_correc_ins": """/*
{context}
*/
Requirement: {question}
Last Error: {last_error}
Operator: {a}"""
}
