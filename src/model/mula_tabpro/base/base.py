import copy

import pandas as pd
from typing import List
from src.tools.logger import Logger
import global_values as GV
from src.llm.gpt_inference import GPTPOOL
from src.data import TQAData

class Operator(object):
    def __init__(self, op_type=GV.NAMES['EXT_COL']):
        self.args = {}
        self.type = op_type
        self.complete_func_str = None

    def complete_args(self):
        pass

    def _parse_args(self):
        pass

    def _arg_gen_prompt(self):
        pass

    def op_string(self):
        return self.type

    def update_arg(self, arg_name, arg_val):
        self.args[arg_name] = arg_val

class Agent(object):
    def __init__(self, llm_name=None, chains = None, PROMPT = None, 
                 agent_name='BaseAgent', logger_root='./', logger_file=None, 
                 self_correction=GV.SELF_CORRECTION, retrieve_demo=GV.RETRIEVE_DEMO):
        self.gpt = GPTPOOL(model=llm_name)
        self.chains = chains
        self.PROMPT = PROMPT
        
        self.err_raise_cnt = 0
        self.MAX_ERR_RAISE_CNT = 4
        self.self_correction = self_correction
        self.retrieve_demo = retrieve_demo

        self.name = agent_name
        self.logger = Logger(name=self.name.capitalize(), root=logger_root, log_file=logger_file)
        self.last_log = None
        self.cur_ins = None
        self.self_corr_inses = []
        self.icl_inses = []

    def process(self, data:TQAData):
        pass

    def generate_op(self, data:TQAData):
        pass

    def _log_current_chain(self):
        pass

    def _parse_next_ops(self, possible_next_op_type, answer):
        pass

    def _op_gen_prompt(self, next_op_type:List[str], tbl: pd.DataFrame, question: str):
        pass

    def _record_error_raise(self, e):
        self.last_log = str(e)
        self.logger.log_message(level='error', msg=e)
        self.err_raise_cnt += 1
        if self.err_raise_cnt >= self.MAX_ERR_RAISE_CNT:
            self.err_raise_cnt = 0
            raise ValueError(f'E-19: Error raised more than {self.MAX_ERR_RAISE_CNT} times')
    
    def _get_next_possible_op_name(self, his_op_names):
        pass
    
    def get_self_corr_inses(self, out):
        tmp_ins = copy.deepcopy(self.cur_ins)
        tmp_ins.key = copy.deepcopy(self.last_log)
        tmp_ins.last_err = copy.deepcopy(self.last_log)
        tmp_ins.a = copy.deepcopy(out)
        tmp_ins.type = f'{self.name}-self_correction'
        return tmp_ins
    
    def get_icl_inses(self, out, key=None):
        tmp_ins = copy.deepcopy(self.cur_ins)
        tmp_ins.key = copy.deepcopy(tmp_ins.q) if key is None else key
        tmp_ins.last_err = copy.deepcopy(self.last_log)
        tmp_ins.a = copy.deepcopy(out)
        tmp_ins.type = f'{self.name}-in_context_learning'
        return tmp_ins

class InitOP(Operator):
    def __init__(self, op_type=GV.NAMES['INIT'], llm_model=None):
        super().__init__(op_type)
    
class EndOP(Operator):
    def __init__(self, op_type=GV.NAMES['END'], llm_model=None):
        super().__init__(op_type)
