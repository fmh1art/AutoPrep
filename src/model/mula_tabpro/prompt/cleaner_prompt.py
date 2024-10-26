
import global_values as GV

PROMPT_CLEANER = {
    f"head": f"You are a agent to use operators to clean the table. If nothing needs to be cleaned, return {GV.NAMES['END']}.",

    # description for {GV.NAMES['REMOVE_SYMBOL']}
    f"{GV.NAMES['REMOVE_SYMBOL']}": f"""The operator `{GV.NAMES['REMOVE_SYMBOL']}` aims to remove the specified symbol from the column. We use the operator by specifying the arguments `column` and the symbol to be removed by argument `symbol`.""",

    # description for {GV.NAMES['END']}
    f"{GV.NAMES['END']}": f"""If nothing needs to be cleaned, return {GV.NAMES['END']}.""",

    # demo for {GV.NAMES['REMOVE_SYMBOL']}
    f"demo_{GV.NAMES['REMOVE_SYMBOL']}": f"""Here are some examples of using the operator `{GV.NAMES['REMOVE_SYMBOL']}`,

/*
"date": "09/2013*" | "11/13*" | "11/16/2013*" | "11/18/2013*"
*/
Question: please standardize the column `date` to datetime format.
Operator: ```{GV.NAMES['REMOVE_SYMBOL']}(df, column='result', symbol='*')```""", 

    # demo for {NAME['END']}
    f"demo_{GV.NAMES['END']}": f"""Here are some examples of using the operator `{GV.NAMES['END']}`,

/*
Columns: "day"(string), "results_record"(string)

"day": "saturday" | "sunday" | "saturday" | "saturday" | "saturday"
"results_record": "1-0" | "1-1" | "1-2" | "1-3" | "2-3"
*/
Question: how long was the teams longest losing streak?
Operator: ```{GV.NAMES['END']}```

/*
Columns: "title"(string), "producers"(string)

"title": "throw aways" | "i'm a gangsta" | "life goes on interlude #1" | "screwed up" | "against all odds"
"producers": "maj & sosa" | "drew" | "nan" | "mr. lee" | "q-stone"
*/
Question: how many tracks on trae's album "life goes on"?
Operator: ```{GV.NAMES['END']}```

/*
Columns: "school_year"(string), "class_a"(string), "class_aa"(string), "class_aaa"(string)

"school_year": "1994-95" | "1995-96" | "1996-97" | "2000-01" | "2001-02"
"class_a": "menard" | "era" | "sulphur bluff" | "westbrook" | "graford"
"class_aa": "van alstyne" | "coahoma" | "marion" | "edgewood" | "lindsay"
"class_aaa": "cameron yoe" | "colorado city" | "colorado city" | "perryton" | "hamshire-fannett"
*/
Question: what was the only year keene won class aa?
Operator: ```{GV.NAMES['END']}```
Explanation: None of the column is datetime value and No need for further cleaning.""",

    # description for {GV.NAMES['REMOVE_UNIT']}
    f"{GV.NAMES['REMOVE_UNIT']}": f"""The operator `{GV.NAMES['REMOVE_UNIT']}` aims to remove the unit from the column, such as "m", "km/s", "million"... We use the operator by specifying the arguments `column` and the unit to be removed by argument `unit`.""",

    # demo for {GV.NAMES['REMOVE_UNIT']}
    f"demo_{GV.NAMES['REMOVE_UNIT']}": f"""Here are some examples of using the operator `{GV.NAMES['REMOVE_UNIT']}`,

/*
"notes": "5,000 m" | "5,000 m" | "10,000 m" | "10,000 m" | "10,000 m" | "10,000 m"
*/
Requirement: please standardize the column `notes` to numerical format.
Operator: ```{GV.NAMES['REMOVE_UNIT']}(df, column='notes', unit='m')```""",
    



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
