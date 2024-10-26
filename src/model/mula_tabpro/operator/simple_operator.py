import re, copy
from typing import List

import pandas as pd

from src.tools.utils import *
import global_values as GV

from ..base import *

class SimpleOperator(Operator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type='simple_operator', log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT=None):
        super().__init__(op_type)
        self.gpt = GPTPOOL(model=llm_model)
        self.logger = Logger(name=op_type, log_file=log_file, root=log_root)
        self.PROMPT = PROMPT
        self.exe_func_name = op_type
        self.required_args = ARG_REQUIRED_DICT[op_type]
        self.complete_func_str = 'no_function(arg=None)'

    def _parse_args(self, data:TQAData):
        pass

    def execute(self, data:TQAData):
        df = copy.deepcopy(data.tbl)
        table = eval(self.complete_func_str)

        if table is None or len(table) == 0:
            raise ValueError(f'E({self.type}): Empty table returned')
        if type(table) != type(pd.DataFrame()):
            raise ValueError(f'E({self.type}): Not pd.Dataframe')
        data.tbl = table
        return data

    def complete_args_with_output(self, data:TQAData, out):
        arg_val, func_str = self._parse_args(data, out)
        self.complete_func_str = func_str

        self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Args: {arg_val}')
        
        for k in self.required_args:
            if k not in arg_val:
                raise ValueError(f'E({self.type}): Missing required argument: {k}')
        for k in self.required_args:
            self.update_arg(k, arg_val[k])
            
        self.update_arg('complete_func_str', self.complete_func_str)

    def complete_args(self, data:TQAData):
        prompt = self._arg_gen_prompt(data.df, data.question)
        out = self.gpt.query(prompt)

        self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
        self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')

        arg_val, func_str = self._parse_args(data, out)
        self.complete_func_str = func_str

        # self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Args: {arg_val}')
        
        for k in self.required_args:
            if k not in arg_val:
                raise ValueError(f'E({self.type}): Missing required argument: {k}')
        for k in self.required_args:
            self.update_arg(k, arg_val[k])
            
        self.update_arg('complete_func_str', self.complete_func_str)

    def op_string(self):
        arg_str = ', '.join([f'{k}={self.args[k]}' for k in self.args])
        return f'{self.type}({arg_str})'

    def _arg_gen_prompt(self, df: pd.DataFrame, question: str):
        head = self.PROMPT['head']

        demo = self.PROMPT['demo']

        cot_tbl = df_to_cotable(df)
        query = self.PROMPT['query'].format(cot_tbl=cot_tbl, question=question)

        return head + '\n\n' + demo + '\n\n' + query