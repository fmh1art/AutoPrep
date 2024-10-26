from .simple_agent import *
import sqlite3

class NL2SQLer(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='nl2sqler', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)
        self.conn = sqlite3.connect(':memory:')

    def process(self, data:TQAData):
        while True:
            prompt = self._ans_gen_prompt(data)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')

            sql = parse_any_string(out)
            try:
                ans = self.exe_sql(sql, data)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'tbl: {df_to_cotable(ans)}')
                break
            except Exception as e:
                self._record_error_raise(e)

        return sql, ans
    
    def exe_sql(self, sql: str, data:TQAData):
        tbl = data.tbl
        tbl.to_sql('w', self.conn, index=False, if_exists='replace')
        ans = pd.read_sql(sql, self.conn)
        return ans

    def _ans_gen_prompt(self, data:TQAData):
        tbl, question = data.tbl, data.question
        demo = DEMO_NL2SQLER

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            create_table, table_ret = binder_nl2sql_prompt(data, cut_line=row_lim)
            query = QUERY_NL2SQLER.format(create_table_text=create_table, table=table_ret, question=question)
            prompt = demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                break
        if cal_tokens(prompt) > GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The first row is too long!')
        return prompt
