from global_values import NAMES
from src.model.mula_tabpro.base.operator_pool import OP_FUNC_STRING
from .prompt import HEAD_OP_GEN, DESC_END

PROMPT_SYNTHESIZER = {
    f"head": HEAD_OP_GEN,
    
    # description for {NAMES['GEN_NEW_COL']}
    f"{NAMES['GEN_NEW_COL']}": f"""The operator `{NAMES['GEN_NEW_COL']}` aims to generate a new column based on the existing columns. We define the operator:

{{fun_str}}

We use the operator by specifying the arguments `column` and the `ascending` flag.""",

    # description for {NAMES['GEN_CON_COL']}
    f"{NAMES['GEN_CON_COL']}": f"""The operator `{NAMES['GEN_CON_COL']}` aims to generate a conditional column based on the existing columns. We define the operator:

{{fun_str}}

We use the operator by specifying the arguments `new_column` and the `condition`.""", 

    # description for {NAMES['END']}
    f"{NAMES['END']}": DESC_END,

    # demo for {NAMES['GEN_NEW_COL']}
    f"demo_{NAMES['GEN_NEW_COL']}": f"""Here are example of using the operator `{NAMES['GEN_NEW_COL']}`,

/*
Columns: "iso/iec standard", "status", "wg"

"row number": "iso/iec tr 19759" | "iso/iec 15288" | "iso/iec 12207"
"status": "published (2005)" | "published (2008)" | "published (2011)"
"wg": 20 | 7 | 7
*/
Statement: 2 standards are published in 2011
Explanation: We need to extract the year from the "status" column.
Next Operator: ```{NAMES['GEN_NEW_COL']}(df, new_column="year", operation=lambda x: x['status'].split('(')[1].split(')')[0])```""",

    # demo for {NAMES['GEN_CON_COL']}
    f"demo_{NAMES['GEN_CON_COL']}": f"""Here are example of using the operator `{NAMES['GEN_CON_COL']}`,

/*
Columns: "row number", "DATE", "OPPONENT", "SCORE DIFFERENCE"

"row number": 1 | 2 | 3
"DATE": "October 19" | "July 13" | "September 23 Governor's Cup"
"OPPONENT": "STA.LUCIA" | "TANDUAY" | "TANDUAY"
"SCORE DIFFERENCE": 7 | 6 | 15
*/
Statement: 2 games have a score difference greater than 15
Explanation: We need to compare the "SCORE DIFFERENCE" with the target value of September 23's score difference, which is 15.
Next Operator: ```{NAMES['GEN_CON_COL']}(df, new_column='GREATER THAN TARGET', condition=lambda x: x['SCORE DIFFERENCE'] > 15)```""",

    # demo for {NAMES['END']}
    f"demo_{NAMES['END']}": f"""Here are example of using the operator `{NAMES['END']}`,

/*
Columns: "row number", "when", "score difference", "is equal to 6"

"row number": 1 | 2
"when": "2024-04-13" | "2024-04-20"
"score difference": 6 | 12
"is equal to 6": "Yes" | "No"
*/
Statement: 2 games have a score difference equal to 6
Explanation: We have already generated the "score difference" and "is equal to 6" columns. Now return {NAMES['END']}.
Next Operator: ```{NAMES['END']}```""",

    # query prompt
    f"query": """Please complete the prompt below,
/*
{cot_tbl}
*/
Statement: {question}
The next operator must be {operator_option}. Return ```next_operator_here``` based on the table with NO other texts. 
Next Operator:"""
}
