from .simple_operator import *

class GenConCol(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['GEN_CON_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output).strip()
        if GV.PRE_CHECK_GRAMMAR and not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output')
        
        try:
            new_column, condition = parse_two_args(op_str, 'new_column', 'condition', data.tbl)
        except:
            raise ValueError(f'E(GEN_CON_COL): Error in parsing function: {op_str}') if GV.PRE_CHECK_GRAMMAR else None
        
        if new_column in data.tbl.columns:
            raise ValueError(f'E(GEN_CON_COL): The target column {new_column} already exists in the table') if GV.PRE_CHECK_GRAMMAR else None

        return {'new_column': new_column, 'condition': condition}, op_str
