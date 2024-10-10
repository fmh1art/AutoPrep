from .simple_operator import *

class GenConCol(SimpleOperator):
    def __init__(self, llm_model='gpt-3.5-turbo', op_type=NAMES['GEN_CON_COL'], log_root='tmp/table_llm_log', log_file=f'mula_tabpro_v{TABLELLM_VERSION}.log', PROMPT={'demo': '', 'query': '', 'head': ''}):
        super().__init__(llm_model, op_type, log_root, log_file, PROMPT)

    def _parse_args(self, data: TQAData, output: str):
        op_str = parse_any_string(output).strip()
        if not op_str.startswith(self.type):
            raise ValueError(f'E({self.type}): Function name not found in the output')
        
        try:
            new_column, condition = parse_two_args(op_str, 'new_column', 'condition', data.tbl)
        except:
            raise ValueError(f'E(GEN_CON_COL): Error in parsing function: {op_str}')
        
        if new_column in data.tbl.columns:
            raise ValueError(f'E(GEN_CON_COL): The target column {new_column} already exists in the table')

        return {'new_column': new_column, 'condition': condition}, op_str

def main():

    table_text = [
        ['date', 'division', 'league', 'score'],
        ['2001/01/02', '2', 'usl a-league', '15-26'],
        ['2002/08/06', '2', 'usl a-league', '12-18'],
        ['2005/03/24', '2', 'usl first division', '8-15'],
    ]
    table = pd.DataFrame(table_text[1:], columns=table_text[0])
    question = 'how many records are before 2003'
    data = TQAData(tbl=table, question=question)

    op = GenConCol(llm_model='gpt-3.5-turbo-0613')
    op.complete_args(data)
    data = op.execute(data)
    print(data.tbl)
            
if __name__ == '__main__':
    # main()
    pass