import pandas as pd
from typing import List
from src.llm.gpt_inference import GPTPOOL
from src.data.TQAData import TQAData
from src.tools.utils import run_python, parse_code
import os

class Summarizer():
    PROMPT_LIST: List = [
"""
Given a table:
{table}
And the corresponding question:
{question}
Your task is to generate appropriate table description which can help latter agent to generate python code to process the table. You should MAKE SURE the summary includes the concise column names, thus the code generated latter can be executed correctly. 
Your summary:
""",

"""
Given a table:
{table}
And the corresponding question:
{question}
Your task is to generate the appropriate table description which can help latter agent to generate python code to process the table.
The summary should follow the format:
```

The table is about ...
The table schema is shown as below:
`column_name1`: Description1. Some example of the values are `examples_of_column1_values1`, `examples_of_column1_values2`, 
`column_name2`: Description2, Some example of the values are  `examples_of_column2_value1`, `examples_of_column1_values2`, 
...
```

Your summary:
""",
]

    def __init__(self, model_name: str = "gpt-3.5-turbo", template_id=0):
        self.gpt = GPTPOOL(model=model_name)
        self.PROMPT_TEMPLATE = self.PROMPT_LIST[template_id]

    def process_one(self, table: TQAData):
        tab_str = table.serialize_without_label(mode=3)
        ques = table.question

        prompt = self.PROMPT_TEMPLATE.format(table=tab_str, question=ques)
        # print('PROMPT:', prompt)
        ret = self.gpt.query(prompt)
        # print('RET:', ret)
        return ret
    

class Coder():
    PROMPT_TEMPLATE: str = \
"""
Given the table description:
{table_summary}
And the corresponding question:
{question}
Assume the table is store in `./tmp/summarize_then_code/tbl.csv` file. Please generate python code can load table into dataframe object then can be executed to get the answer of question from the table.
Use `print()` function to PRINT out the answer based on the table with NO other texts.
Return ```python your_code_here ``` based on the table with NO other texts.
When Generate the code, only use the column name in the table description, and make sure the code can be executed correctly,
your code:
"""

    DEBUG_TEMPLATE: str = \
"""
Given a table description:
{table_summary}
And the corresponding question:
{question}
We generate the following code:
{code}
However, the code has some errors:
{bug}
Please fix the bug and return the complete correct code.
Return ```python the_complete_correct_code_here ``` based on the table with NO other texts,
The correct code:
"""

    def __init__(self, model_name: str = "gpt-3.5-turbo", max_debug_round=3):
        self.gpt = GPTPOOL(model=model_name)
        self.max_debug_round = max_debug_round
        self.root_dir = './tmp/summarize_then_code'

    def process_one(self, table_summary: str, question: str):
        prompt = self.PROMPT_TEMPLATE.format(table_summary=table_summary, question=question)
        ret = self.gpt.query(prompt)
        code_text = parse_code(ret)

        code_lists = [code_text]
        debug_round = 0
        while True:
            ans = run_python(code_text)
            if ans is None or len(ans)==0:
                log = 'Error: There is no output in your code!'
            elif 'Error occurred: ' in ans:
                log = ans.split('Error occurred: ')[1]
            else:
                break

            if debug_round >= self.max_debug_round:
                break

            code_text = self.debug_code(table_summary, question, code_text, log)
            code_lists.append(code_text)
            debug_round += 1

        return code_lists, ans
    
    def debug_code(self, summary, question, code_text, code_bug):

        prompt = self.DEBUG_TEMPLATE.format(table_summary=summary, 
                        question=question, code=code_text, bug=code_bug)
        ret = self.gpt.query(prompt)
        code_text = parse_code(ret)
        return code_text


class SummarizeThenCode():

    def __init__(self, model_name: str = "gpt-3.5-turbo", template_id=0, max_debug_round=3):
        self.summarizer = Summarizer(model_name, template_id)
        self.coder = Coder(model_name, max_debug_round)
        
        self.root_dir = './tmp/summarize_then_code'
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def process_one(self, table: TQAData):

        tbl = table.tbl
        tbl.to_csv(os.path.join(self.root_dir, 'tbl.csv'), index=False, encoding='utf-8')
        ques = table.question
        
        summary = self.summarizer.process_one(table)
        # print('SUMMARY:', summary)
        code_list, ans = self.coder.process_one(summary, ques)

        return summary, code_list, ans