from .simple_operator import *

class GenNewCol(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['GEN_NEW_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def _get_related_cols(self, func:str):
        var = re.findall(r'lambda (.*?):', func)[0]
        finds = re.findall(rf'{var}\[\'(.*?)\'\]', func) + re.findall(rf'{var}\[\"(.*?)\"\]', func)
        return finds
    
    def execute(self, data:TQAData):
        df = copy.deepcopy(data.tbl)
        table = eval(self.complete_func_str)

        if table is None or len(table) == 0:
            raise ValueError(f'E({self.type}): Empty table returned')
        if type(table) != type(pd.DataFrame()):
            raise ValueError(f'E({self.type}): Not pd.Dataframe')
        data.tbl = table

        new_col = self.args['new_column']
        # if the col value if boolean, convert it to string
        data.tbl[new_col] = data.tbl[new_col].apply(lambda x: x if type(x)==int or type(x)==float else str(x))
        # replace nan into '[n.a.]'
        data.tbl[new_col] = data.tbl[new_col].apply(lambda x: '[n.a.]' if pd.isna(x) else x)

        return data
 
    def _check_func_name(self, op_str:str):
        if not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Please output follow the required format: Function name not found in the output. The function name should be {self.type}')

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output).strip()
        self._check_func_name(op_str)
        
        try:
            new_column, func = parse_two_args(op_str, 'new_column', 'func', data.tbl)
        except:
            raise ValueError(f'E(GEN_NEW_COL): Error in parsing function: {op_str}') if GV.PRE_CHECK_GRAMMAR else None
        
        source_cols = self._get_related_cols(func)
        source_cols = list(set(source_cols))
        for col in source_cols:
            if col not in data.tbl.columns:
                raise ValueError(f'E(GEN_NEW_COL): The column {col} is not in the table')
        
        try:
            eval(func)
        except:
            raise ValueError(f'E({self.type}): Error in parsing the lambda function: {func}. The lambda function is not valid') if GV.PRE_CHECK_GRAMMAR else None
        
        if GV.PRE_CHECK_GRAMMAR and new_column in data.tbl.columns:
            raise ValueError(f'E({self.type}): The target column {new_column} already exists in the table')
        
        return {'new_column': new_column, 'func': func, 'source_cols': source_cols}, op_str

class ExtractColumn(GenNewCol):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['EXT_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

class CalculateColumn(GenNewCol):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['CAL_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

class BooleanColumn(GenNewCol):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['BOOL_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

class CombineColumn(GenNewCol):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=GV.NAMES['COMB_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)
