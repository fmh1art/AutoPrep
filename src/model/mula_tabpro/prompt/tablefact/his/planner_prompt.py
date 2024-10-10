from global_values import NAMES
from src.tools.utils import open_json

DEMO_PLANNER = {
    # description for synthesizer
    'synthesizer': f"""The agent `Synthesizer` aims at `synthesizing` a new column to the table. It uses operators `{NAMES['GEN_NEW_COL']}` and `{NAMES['GEN_CON_COL']}`.""",

    # description for analyzer
    'analyzer': f"""The agent `Analyzer` aims at analyze the table. It uses operators `{NAMES['EXT_ROW']}`, `{NAMES['EXT_MAX_CONS_RECORD']}`, `{NAMES['GROUP_STATISTICS']}` and `{NAMES['SORT_BY']}`.""",

    # description for answer generator
    'answer_generator': f"""The agent `AnswerGenerator` aims at generating the final answer based on the table.""",

    # demo for synthesizer
    'demo_synthesizer': f"""Here are the example of using the agent `Synthesizer`,

/*
row number | Date | Tournament | Surface | Opponent | Score
---|---|---|---|---|---
1 | 2004/08/23 | La Paz, Bolivia | Clay | Jenifer Widjaja | 6-3, 4-6, 0-6
2 | 2005/06/06 | Santa Tecla, El Salvador | Clay | Andrea Benítez | 7-6(7-5), 6-4
3 | 2005/08/22 | Bogotá, Colombia | Clay | Carla Tiene | 4-6, 0-6
*/
Statement: the last tournament won by andrew koch benvenuto held in Clay
History Agent: Init ->
Next Agent: ```Synthesizer````

/*
row number | DATE | OPPONENT | SCORE
---|---|---|---
1 | October 19 | STA.LUCIA | 101-94
2 | July 13 | TANDUAY | 104-98
3 | September 23 Governor's Cup | TANDUAY | 108-93
*/
Statement: the game in July 13 have greater score difference than that in September 23?
History Agent: Init ->
Next Agent: ```Synthesizer```""",

    # demo for analyzer
    'demo_analyzer': f"""Here are the example of using the agent `Analyzer`,

/*
row number | Date | Tournament | Surface | Opponent | Score | if won
---|---|---|---|---|---|---
1 | 2004/08/23 | La Paz, Bolivia | Clay | Jenifer Widjaja | 6-3, 4-6, 0-6 | Yes
2 | 2005/06/06 | Santa Tecla, El Salvador | Clay | Andrea Benítez | 7-6(7-5), 6-4 | Yes
3 | 2005/08/22 | Bogotá, Colombia | Clay | Carla Tiene | 4-6, 0-6 | No
*/
Statement: the last tournament won by andrew koch benvenuto held in Clay
History Agent: Init -> Synthesizer({NAMES['GEN_CON_COL']}) ->
Next Agent: ```Analyzer```

/*
row number | DATE | OPPONENT | SCORE | SCORE DIFFERENCE | GREATER THAN 11(SEPTEMBER 23)
---|---|---|---|---|---
1 | October 19 | STA.LUCIA | 101-94 | 7 | No
2 | July 13 | TANDUAY | 104-98 | 6 | No
3 | September 23 Governor's Cup | TANDUAY | 104-93 | 11 | No
*/
Statement: the game in July 13 have greater score difference than that in September 23?
History Agent: Init -> Synthesizer({NAMES['GEN_NEW_COL']}, {NAMES['GEN_CON_COL']}) ->
Next Agent: ```Analyzer```""",

    # demo for answer generator
    'demo_answer_generator': f"""Here are the example of using the agent `AnswerGenerator`,

/*
row number | Date | Tournament | Surface | Score | if won
---|---|---|---|---|---
1 | 2004/08/23 | La Paz, Bolivia | Clay | 6-3, 4-6, 0-6 | Yes
2 | 2005/06/06 | Santa Tecla, El Salvador | Clay | 7-6(7-5), 6-4 | Yes
3 | 2005/08/22 | Bogotá, Colombia | Clay | 4-6, 0-6 | No
*/
Statement: the last tournament won by andrew koch benvenuto held in Clay
History Agent: Init -> Synthesizer({NAMES['GEN_CON_COL']}) -> Analyzer({NAMES['EXT_ROW']}, {NAMES['SORT_BY']}) ->
Next Agent: ```AnswerGenerator```

/*
row number | DATE | SCORE | SCORE DIFFERENCE | GREATER THAN 11(SEPTEMBER 23)
---|---|---|---|---
1 | October 19 | 101-94 | 7 | No
2 | July 13 | 104-98 | 6 | No
3 | September 23 Governor's Cup | 104-93 | 11 | No
*/
Statement: the game in July 13 have greater score difference than that in September 23?
History Agent: Init -> Synthesizer({NAMES['GEN_NEW_COL']}, {NAMES['GEN_CON_COL']}) -> Analyzer({NAMES['EXT_ROW']}) ->
Next Agent: ```AnswerGenerator```""",
}

QUERY_PLANNER = """Please complete the prompt below,
/*
{cot_tbl}
*/
Statement: {question}
History Agent: {history_agent}
The Agent must be {agent_option}. Return ```next_agent``` based on the table with NO other texts.
Next Agent:"""