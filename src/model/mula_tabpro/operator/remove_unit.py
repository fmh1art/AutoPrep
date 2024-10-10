from .simple_operator import *

class RemoveUnit(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=NAMES['REMOVE_UNIT'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def execute(self, data:TQAData):
        df = copy.deepcopy(data.tbl)
        table = eval(self.complete_func_str)

        if type(table) != type(pd.DataFrame()):
            raise ValueError(f'E({self.type}): Not pd.Dataframe')

        data.tbl = table

        col = self.args.get('column')
        if col in data.col_type:
            data.col_type.pop(col)

        unit = self.args.get('unit')

        new_col = f'{col}_{unit}'.replace(' ', '')

        num_rat = numerical_ratio(df, new_col)
        if num_rat > TYPE_DEDUCE_RATIO:
            data.tbl = standardize_to_numerical(data.tbl, col)
            data.col_type[col] = 'numerical'

        return data

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output).strip()
        if not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output, Please follow the output format in the prompt!')
        
        try:
            column, unit = parse_two_args(op_str, 'column', 'unit', data.tbl)
        except:
            raise ValueError(f'E({self.type}): Error in parsing function: {op_str}')
        
        if column not in data.tbl.columns:
            raise ValueError(f'E({self.type}): Column not found in the table')
        
        return {'column': column, 'unit': unit}, op_str
            
if __name__ == '__main__':
    # main()
    pass