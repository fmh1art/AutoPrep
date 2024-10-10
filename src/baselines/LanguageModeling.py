from src.llm.gpt_inference import GPTPOOL
from src.data.TQAData import TQAData
import os


# Build the LanguageModeling based model to tackle the table process task

class LanguageModeling():
    PROMPT_TEMPLATE: str = \
"""
Given a table:
{table}
And the corresponding question:
{question}
Please generate the answer based on the table with NO other texts.
The answer is:
"""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.gpt = GPTPOOL(model=model_name)
        self.root_dir = './tmp/language_modeling'
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def process_one(self, table: TQAData):
        tab_str = table.serialize_without_label(mode=3)
        ques = table.question
        prompt = self.PROMPT_TEMPLATE.format(table=tab_str, question=ques)
        return self.gpt.query(prompt)