from .simple_operator import *

class RemoveSymbol(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['REMOVE_SYMBOL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def execute(self, data:TQAData):
        df = copy.deepcopy(data.tbl)
        table = eval(self.complete_func_str)

        if type(table) != type(pd.DataFrame()):
            raise ValueError(f'E({self.type}): Not pd.Dataframe')
        
        data.tbl = table

        col = self.args.get('column')
        num_rat = numerical_ratio(df, col)
        if num_rat > GV.TYPE_DEDUCE_RATIO:
            data.tbl = standardize_to_numerical(data.tbl, col)
            data.col_type[col] = 'numerical'
        
        return data

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output).strip()
        if not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output, Please follow the output format in the prompt!')
        
        try:
            column, symbol = parse_two_args(op_str, 'column', 'symbol', data.tbl)
        except:
            raise ValueError(f'E({self.type}): Error in parsing function: {op_str}')
        
        if column not in data.tbl.columns:
            raise ValueError(f'E({self.type}): Column not found in the table')
        
        # calculate the numbers and letters in symbol
        cnt = 0
        for c in symbol:
            if c.isdigit() or c.isalpha():
                cnt += 1
            if cnt > 1:
                raise ValueError(f'E({self.type}): Symbol should not contain too much numbers or letters')
        
        return {'column': column, 'symbol': symbol}, op_str
            
if __name__ == '__main__':
    # main()
    pass