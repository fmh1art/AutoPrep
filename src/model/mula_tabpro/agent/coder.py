from .simple_agent import *

class Coder(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='coder', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)

    def process(self, data:TQAData, requirement: str, cols:List[str]):
        self.last_log = None
        self.err_raise_cnt = 0
        
        while True:
            prompt = self._ans_gen_prompt(data, requirement, cols)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg=f'Output: {out}')

            code_str = parse_any_string(out, hard_replace='Code:')
            self.code = code_str

            try:
                df = copy.deepcopy(data.tbl)
                df = execute_code_from_string(code_str, df)
                data.tbl = df
                self.logger.log_message(line_limit=cut_log, level='debug', msg=f'tbl: {df_to_cotable(data.tbl)}')
                break
            except Exception as e:
                self.code = code_str
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.last_log = None
            self.logger.log_message(msg=f'---- ID: {data.id}, SUCCESSFULLY DEBUG IN {self.err_raise_cnt} times! ----')
        else:
            self.logger.log_message(msg=f'---- ID: {data.id}, NO BUGS! ----')

        return data

    def _ans_gen_prompt(self, data:TQAData, requirement: str, cols:List[str]):
        tbl = data.tbl

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            demo = copy.deepcopy(DEMO_CODER)
            table = df_to_str_columns_add_quo(df=data.tbl, cut_line=row_lim, exclude_cols=[col for col in data.tbl.columns if col not in cols])

            query = QUERY_CODER.format(table=table, requirement=requirement)

            if self.self_correction and self.last_log is not None:

                query = query.replace('Code:', 'Last Error: ' + self.last_log + '\n' + 'Code:')
            
            prompt = demo + '\n\n' + query

            if cal_tokens(prompt) <= MAX_INPUT_LIMIT-MAX_OUTPUT_LIMIT:
                break

        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt