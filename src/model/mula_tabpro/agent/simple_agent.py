import copy
from typing import List

from src.tools.utils import *
import global_values as GV
from ..prompt import *
from ..operator import *
from ..base import *
from src.model.mula_tabpro.others.instance_pool import *

class SimpleAgent(Agent):
    def __init__(self, llm_name=None, chains = None, PROMPT = None, agent_name='simple_agent', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', self_correction=GV.SELF_CORRECTION):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file, self_correction=self_correction)
        
    def process(self, data:TQAData):
        self.data = data
        
        while True:
            try:
                cur_op, out = self.generate_op(data)
            
            except Exception as e:
                # if error raised by cur_op.execute(data)
                self._record_error_raise(f'Last error when generating operator: {str(e)}')
                continue
            
            try:
                #? check if the current op is END and append the current op to the chain
                if cur_op.type == GV.NAMES['END']:
                    self.chains.append(cur_op)
                    break #! END WHILE

                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Current chain: {self._log_current_chain()}')
                
                cur_op.complete_args_with_output(data, out)
                data = cur_op.execute(data)

                #? if successfully executed
                self.data = data
                self.chains.append(cur_op)
                self.logger.log_message(line_limit=False, level='debug', msg=f'New Table is:\n{data.tbl}')
                self.last_log = None

            except Exception as e:
                # if error raised by cur_op.execute(data)
                self._record_error_raise(f'Last error when executing operator {cur_op.complete_func_str}: {str(e)}')
                continue

        return self.chains, data

