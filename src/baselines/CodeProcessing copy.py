import os
import pandas as pd

from src.llm.gpt_inference import GPTPOOL
from src.data.TQAData import TQAData


from src.tools.utils import run_python, parse_code

# Build the LanguageModeling based model to tackle the table process task

class CodeProcessing():
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

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.gpt = GPTPOOL(model=model_name)
        self.root_dir = './tmp/code_processing'
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def process_one(self, table: TQAData):
        tab_str = table.serialize_without_label(mode=3)

        tbl = table.tbl
        tbl.to_csv(os.path.join(self.root_dir, 'tbl.csv'), index=False)
        ques = table.question

        prompt = self.PROMPT_TEMPLATE.format(table=tab_str, question=ques)
        ret = self.gpt.query(prompt)
        code_text = parse_code(ret)
        ans = run_python(code_text)
        return code_text, ans
    