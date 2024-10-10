from .simple_agent import *
import sqlite3

class NL2SQLer(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='nl2sqler', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)
        self.conn = sqlite3.connect(':memory:')

    def process(self, data:TQAData):
        tbl, question = data.tbl, data.question

        while True:
            prompt = self._ans_gen_prompt(tbl, question)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg=f'Output: {out}')

            sql = parse_any_string(out)
            try:
                ans = self.exe_sql(sql, data)
                self.logger.log_message(line_limit=cut_log, level='debug', msg=f'tbl: {df_to_cotable(ans)}')
                break
            except Exception as e:
                self._record_error_raise(e)

        return sql, ans
    
    def exe_sql(self, sql: str, data:TQAData):
        tbl = data.tbl
        tbl.to_sql('df', self.conn, index=False, if_exists='replace')
        ans = pd.read_sql(sql, self.conn)
        return ans

    def _ans_gen_prompt(self, tbl: pd.DataFrame, question: str):
        demo = DEMO_NL2SQLER

        row_len = len(tbl)
        for row_lim in range(row_len, 0, -2):
            cot_tbl = df_to_cotable(tbl, cut_line=-1)
            query = QUERY_NL2SQLER.format(cot_tbl=cot_tbl, question=question)
            prompt = demo + '\n\n' + query

            if cal_tokens(prompt) <= MAX_INPUT_LIMIT-MAX_OUTPUT_LIMIT:
                break
        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt