from global_values import NAMES
from src.tools.utils import open_json
from src.model.mula_tabpro.base.operator_pool import OP_FUNC_STRING
from .prompt import HEAD_OP_GEN, DESC_END

PROMPT_EXTRACTOR = {
    f"head": HEAD_OP_GEN,
    
    # description for {NAMES['EXT_COL']}
    f"{NAMES['EXT_COL']}": f"""The operator `{NAMES['EXT_COL']}` aims to extract related columns. This operator should be carefully used, since it may remove critical information for answering the original question. We define the operator:

```python
{OP_FUNC_STRING['EXT_COL']}
```
   
We use the operator by specifying the arguments `columns` as a list of column names.""",

    # description for {NAMES['EXT_ROW']}
    f"{NAMES['EXT_ROW']}": f"""The operator `{NAMES['EXT_ROW']}` aims to extract several rows relevant to the question. We define the operator:

```python
{OP_FUNC_STRING['EXT_ROW']}
```

We use the operator by spefifying the arguments `condition` as a list where the element is a dict containing keys "column", "target_value", and "operator". The `column` is the column name, the `target_value` is the value to compare which should be an assigned value, and the `operator` is the comparison operator. The `operator` can be one of the following: `=`, `==`, `!=`, `>`, `<`, `>=`, `<=`.
Also, we need to specify the argument `logical_relation` as a string, which can be either "and" or "or". The "and" means that all conditions must be satisfied, while the "or" means that any condition can be satisfied.""",

    # demo for {NAMES['EXT_MAX_CONS_RECORD']}
    f"{NAMES['EXT_MAX_CONS_RECORD']}": f"""The operator `{NAMES['EXT_MAX_CONS_RECORD']}` aims to extract the maximum consecutive records. We define the operator:

```python
{OP_FUNC_STRING['EXT_MAX_CONS_RECORD']}
```

We use the operator by specifying the arguments `columns` as a list of column names.""",

    # description for {NAMES['END']}
    f"{NAMES['END']}": DESC_END,

    # demo for {NAMES['EXT_COL']}
    f"demo_{NAMES['EXT_COL']}": f"""Here are some examples of using the operator `{NAMES['EXT_COL']}`,

/*
row number | No. | Date | Tournament | Surface | Score
---|---|---|---|---|---
1 | 1.0 | 23 August 2004 | La Paz, Bolivia | Clay | 6-3, 4-6, 0-6
2 | 2.0 | 6 June 2005 | Santa Tecla, El Salvador | Clay | 7-6(7-5), 6-4
*/
Question: Extract the record of the games before April 25.
Operator with correct arguments: ```{NAMES['EXT_COL']}(df, columns=["No.", "Date", "Tournament", "Surface", "Score"])```
Explanation: This operator should be carefully used, since it may remove critical information for answering the original question.""",

    # demo for {NAMES['EXT_ROW']}
    f"demo_{NAMES['EXT_ROW']}": f"""Here are some examples of using the operator `{NAMES['EXT_ROW']}`,

/*
row number | league | year
---|---|---
1 | usl a-league | 2001
2 | usl a-league | 2002
3 | usl first division | 2005
*/
Question: Extract columns "league", "year". Extract record of A-LEAGUE league and FIRST DIVISION league.
Operator with correct arguments: ```{NAMES['EXT_ROW']}(df, condition=[{{'column':'league', 'target_value':'usl a-league', 'operator':'='}}, {{'column':'league', 'target_value':'usl first division', 'operator':'='}}], logical_relation='or')```

/*
row number | Outcome | Athlete | Country
---|---|---|---
1 | Runner-up | Jenifer Widjaja | USA
2 | Winner | Andrea Benítez | ARG
3 | Runner-up | Andrea Benítez | ARG
4 | Winner | Andrea Benítez | ARG
5 | Winner | María Irigoyen | ITA
*/
Question: Extract columns "Outcome", "Athlete", "Country". Extract the records of athletes from Argentina who won the game.
Operator with correct arguments: ```{NAMES['EXT_ROW']}(df, condition=[{{'column':'Country', 'target_value':'ARG', 'operator':'='}}, {{'column':'Outcome', 'target_value':'Winner', 'operator':'='}}], logical_relation='and')```""",

    # demo for {NAMES['EXT_MAX_CONS_RECORD']}
    f"demo_{NAMES['EXT_MAX_CONS_RECORD']}": f"""Here are some examples of using the operator `{NAMES['EXT_MAX_CONS_RECORD']}`,

/*
row number | Outcome | Athlete | Country
---|---|---|---
1 | Runner-up | Andrea Benítez | ARG
2 | Winner | Andrea Benítez | ARG
3 | Winner | Andrea Benítez | ARG
4 | Winner | Andrea Benítez | ARG
5 | Winner | Andrea Benítez | ARG
*/
Question: Extract the maximum consecutive wins of Andrea Benítez.
Next Operator: ```{NAMES['EXT_MAX_CONS_RECORD']}(df, column='Outcome', target_value='Winner')```""",

    # demo for {NAMES['END']}
    f"demo_{NAMES['END']}": f"""Here are some examples of using the operator `{NAMES['END']}`,

/*
row number | league | year
---|---|---
1 | usl a-league | 2001
2 | usl a-league | 2002
*/
Question: Extract record of A-LEAGUE league.
Next Operator: ```{NAMES['END']}```
Explanation: We have already extracted the required columns and rows. Just output the operator {NAMES['END']}.

/*
row number | when | score difference
---|---|---
1 | 2024-04-13 | 6
2 | 2024-04-20 | 12
*/
Question: Extract records of the games before April 25.
Next Operator: ```{NAMES['END']}```
Explanation: We have already extracted the required rows. Just output the operator {NAMES['END']}.""", 

    # query prompt
    f"query": """Please complete the prompt below,
/*
{cot_tbl}
*/
Question: {question}
The next operator must be {operator_option}. Return ```next_operator_here``` based on the table with NO other texts.
Next Operator:"""
}
