from .simple_operator import *

class FilterColumns(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['FILTER_COLUMNS'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def _parse_args(self, data:TQAData, output: str):
        op_str = parse_any_string(output).strip()
        if not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output')
        
        try:
            cols = parse_one_arg(op_str, 'columns', data.tbl)
        except:
            raise ValueError(f'E(EXT_COL): Error in parsing args: {op_str}')

        return {'columns': cols}, op_str

