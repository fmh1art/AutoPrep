from global_values import NAMES
from src.model.mula_tabpro.base.operator_pool import OP_FUNC_STRING
from .prompt import HEAD_OP_GEN, DESC_END

PROMPT_ANALYZER = {
    f"head": HEAD_OP_GEN,

    # description for {NAMES['EXT_ROW']}
    f"{NAMES['EXT_ROW']}": f"""The operator `{NAMES['EXT_ROW']}` aims to extract several rows relevant to the statement. We define the operator:

{{fun_str}}

We use the operator by spefifying the arguments `condition` as a list where the element is a dict containing keys "column", "target_value", and "operator". The `column` is the column name, the `target_value` is the value to compare which should be an assigned value, and the `operator` is the comparison operator. The `operator` can be one of the following: `=`, `==`, `!=`, `>`, `<`, `>=`, `<=`.
Also, we need to specify the argument `logical_relation` as a string, which can be either "and" or "or". The "and" means that all conditions must be satisfied, while the "or" means that any condition can be satisfied.""",

    # demo for {NAMES['EXT_MAX_CONS_RECORD']}
    f"{NAMES['EXT_MAX_CONS_RECORD']}": f"""The operator `{NAMES['EXT_MAX_CONS_RECORD']}` aims to extract the maximum consecutive records. We define the operator:

{{fun_str}}

We use the operator by specifying the arguments `columns` as a list of column names.""",
    
    # description for {NAMES['SORT_BY']}
    f"{NAMES['SORT_BY']}": f"""The operator `{NAMES['SORT_BY']}` aims to sort the dataframe by a column. We define the operator:

{{fun_str}}

We use the operator by specifying the arguments `column` and the `ascending` flag.""",

    # description for {NAMES['GROUP_STATISTICS']}
    f"{NAMES['GROUP_STATISTICS']}": f"""The operator `{NAMES['GROUP_STATISTICS']}` aims to group the dataframe by a column and calculate the statistics of other columns. We define the operator:

{{fun_str}}

We use the operator by specifying the arguments `group_by` and the `metrics`.""", 

    # description for {NAMES['END']}
    f"{NAMES['END']}": DESC_END,

    # demo for {NAMES['EXT_ROW']}
    f"demo_{NAMES['EXT_ROW']}": f"""Here are some examples of using the operator `{NAMES['EXT_ROW']}`. When the logical relation is "and", we should use only one condition.

/*
row number | rank | athlete | country
---|---|---|---
1 | 1 | "manjeet kaur (usa)" | "usa"
2 | 2 | "olga tereshkova (kaz)" | "kaz"
3 | 3 | "pinki pramanik (chn)" | "chn"
......
15 | 15 | "sunita rani (ind)" | "ind"
*/
Statement: there are 3 athletes from India in the first 10 ranks
Operator with correct arguments: ```{NAMES['EXT_ROW']}(df, condition=[{{'column':'rank', 'target_value': 10, 'operator':'<='}}])```
Explanation: We reasoning step by step, so extract the rows in the first 10 ranks first.

/*
row number | opponent | result | hurricanes points | opponents
---|---|---|---|---
1 | "colorado" | "win" | 24 | 3
2 | "florida state" | "loss" | 20 | 23
3 | "louisiana state" | "loss" | 8 | 10
4 | "georgia" | "win" | 7 | 6
5 | "indiana" | "win" | 14 | 7
*/
Statement: the hurricane win less than 10 point against louisiana and georgia
Operator with correct arguments: ```{NAMES['EXT_ROW']}(df, condition=[{{'column':'opponent', 'target_value':'louisiana state', 'operator':'=='}}, {{'column':'opponent', 'target_value':'georgia', 'operator':'=='}}], logical_relation='or')```
Explanation: Since we can make sure that the louisiana and georgia both exist in the table, thus we can directly use the operator `{NAMES['EXT_ROW']}` to extract rows.

/*
row number | opponent | result | game site
---|---|---|---
1 | "cincinnati bengals" | "win" | "mile high stadium"
2 | "chicago bears" | "loss" | "soldier field"
3 | "kansas city chiefs" | "win" | "mile high stadium"
4 | "detroit lions" | "win" | "pon1tiac silverdome"
*/
Statement: the bronco have 2 wins at mile high stadium
Operator with correct arguments: ```{NAMES['EXT_ROW']}(df, condition=[{{'column':'game site', 'target_value':'mile high stadium', 'operator':'=='}}])```
Explanation: We first extract the rows where the game site is "mile high stadium".""",

    # demo for {NAMES['EXT_MAX_CONS_RECORD']}
    f"demo_{NAMES['EXT_MAX_CONS_RECORD']}": f"""Here are some examples of using the operator `{NAMES['EXT_MAX_CONS_RECORD']}`,

/*
row number | Outcome | Athlete | Country
---|---|---|---
1 | "Runner-up" | "Andrea Benítez" | "ARG"
2 | "Winner" | "Andrea Benítez" | "ARG"
3 | "Winner" | "Andrea Benítez" | "ARG"
*/
Statement: andrea benítez has the most consecutive wins
Next Operator: ```{NAMES['EXT_MAX_CONS_RECORD']}(df, column='Outcome', target_value='Winner')```""",

    # demo for {NAMES['END']}
    f"demo_{NAMES['END']}": f"""Here are some examples of using the operator `{NAMES['END']}`,

/*
row number | league | year
---|---|---
1 | "usl a-league" | 2001
2 | "usl a-league" | 2002
3 | "usl first division" | 2005
*/
Statement: usl a-league and usl first division both exist in 2005
Next Operator: ```{NAMES['END']}```
Explanation: We have already extracted the required columns and rows. Just output the operator {NAMES['END']}.""", 

    # demo for {NAMES['SORT_BY']}
    f"demo_{NAMES['SORT_BY']}": f"""Here are example of using the operator `{NAMES['SORT_BY']}`,

/*
row number | player | from | rebs
1 | "kurt rambis" | 1989 | 783
2 | "joe reaves" | 1973 | 8
3 | "michael redd" | 2011 | 77
4 | "terrence rencher" | 1995 | 62
*/
Statement: terrence rancher have the most amount of rebound in 1995
Next Operator: ```{NAMES['SORT_BY']}(df, column="rebs", ascending=False)```""",

    # demo for {NAMES['GROUP_STATISTICS']}
    f"demo_{NAMES['GROUP_STATISTICS']}": f"""Here are example of using the operator `{NAMES['GROUP_STATISTICS']}`,

/*
row number | Athlete | Country
---|---|---
1 | "Jenifer Widjaja" | "USA"
2 | "Andrea Benítez" | "ARG"
3 | "Andrea Benítez" | "ARG"
*/
Statement: america has the most athletes
Explanation: We want to know the athlete count for each country, thus, the `group_by` argument should be 'Country' and the `metrics` should be {{'Athlete': 'count'}}.
Next Operator: ```{NAMES['GROUP_STATISTICS']}(df, group_by='Country', metrics={{'Athlete': 'count'}})```""",

    # query prompt
    f"query": """Please complete the prompt below,
/*
{cot_tbl}
*/
Statement: {question}
The next operator must be {operator_option}. Return ```next_operator_here``` based on the table with NO other texts.
Next Operator:"""
}
