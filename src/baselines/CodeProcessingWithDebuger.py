import pandas as pd
import os
from src.llm.gpt_inference import GPTPOOL
from src.data.TQAData import TQAData


from src.tools.utils import run_python, parse_code

# Build the LanguageModeling based model to tackle the table process task

class CodeProcessingWithDebuger():
    PROMPT_TEMPLATE: str = \
"""
Given a table:
{table}
And the corresponding question:
{question}
Assume the table is store in `./tmp/code_processing/tbl.csv` file. Please generate python code can load table into dataframe object then can be executed to get the answer of question from the table.
Use `print()` function to PRINT out the answer based on the table with NO other texts.
Return ```python your_code_here ``` based on the table with NO other texts,
your code:
"""

    DEBUG_TEMPLATE: str = \
"""
Given a table:
{table}
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
        
        self.root_dir = './tmp/code_processing'
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def process_one(self, table: TQAData, table_complete: TQAData):
        tab_str = table.serialize_without_label(mode=3)

        tbl = table_complete.tbl
        
        tbl.to_csv(os.path.join(self.root_dir, 'tbl.csv'), index=False, encoding='utf-8')
        ques = table.question

        prompt = self.PROMPT_TEMPLATE.format(table=tab_str, question=ques)
        # print('PROMPT:', prompt)
        ret = self.gpt.query(prompt)
        # print('RET:', ret)
        code_text = parse_code(ret)
        # print('CODE:', code_text)
        
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
            
            # debug
            code_text = self.debug_code(table, code_text, log)
            code_lists.append(code_text)
            debug_round += 1

        return code_lists, ans
    
    def debug_code(self, table, code_text, code_bug):
        tab_str = table.serialize_without_label(mode=3)
        ques = table.question

        prompt = self.DEBUG_TEMPLATE.format(table=tab_str, question=ques, code=code_text, bug=code_bug)
        # print('PROMPT:', prompt)
        ret = self.gpt.query(prompt)
        # print('RET:', ret)
        code_text = parse_code(ret)
        return code_text
