from .simple_operator import *

class StandDatetime(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['STAND_DATETIME'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def execute(self, data:TQAData):
        df = copy.deepcopy(data.tbl)
        col = self.args.get('column')
        date_rat = date_ratio(df, col)

        table = eval(self.complete_func_str)

        if GV.PRE_CHECK_GRAMMAR and type(table) != type(pd.DataFrame()):
            raise ValueError(f'E({self.type}): Not pd.Dataframe')
        
        data.tbl = table
        data = update_TData_col_type(data, {col: 'datetime'})
        
        return data

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output, code_type='operator_with_args').strip()
        if GV.PRE_CHECK_GRAMMAR and not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output')
        
        try:
            column, format = parse_two_args(op_str, 'column', 'format', data.tbl)
        except:
            raise ValueError(f'E(GEN_NEW_COL): Error in parsing function: {op_str}') if GV.PRE_CHECK_GRAMMAR else None
        
        return {'column': column, 'format': format}, op_str
