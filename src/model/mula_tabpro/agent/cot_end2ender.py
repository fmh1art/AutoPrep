from .simple_agent import *

class CoTEnd2Ender(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='cot_end2ender', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)

    def process(self, data:TQAData, fewshot=True):
        self.err_raise_cnt = 0
        prompt = self._ans_gen_prompt(data, fewshot)
        out = self.gpt.query(prompt)
        self.logger.log_message(line_limit=cut_log, level='debug', msg='Prompt: ' + prompt)
        self.logger.log_message(line_limit=cut_log, level='debug', msg=f'Output: {out}')
        ans = self.parse_answer(out)
        return ans
    
    def parse_answer(self, ans: str):
        if 'the answer is' in ans.lower():
            ans = ans.lower().split('the answer is')[-1]
        ans = ans.strip()
        if len(ans) > 0 and ans[0] == ':':
            ans = ans[1:]
        if len(ans) > 0 and ans[-1] == '.':
            ans = ans[:-1]
        ans = ans.strip()

        if TASK_TYPE == 'tablefact':
            ans = 1 if 'true' in ans.lower() else 0
        return ans

    def _ans_gen_prompt(self, data:TQAData, fewshot=True):
        tbl, question, title = data.tbl, data.question, data.title

        demo = DEMO_COT_END2ENDER if fewshot else ''

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            table = df_to_cotable_old(tbl, row_lim)
            query = QUERY_COT_END2ENDER.format(title=title, table=table, question=question)
            if self.self_correction and self.last_log is not None:
                query = query.replace('Explanation:', self.last_log + '\n' + 'Explanation:')
            prompt = demo + '\n\n' + query
            prompt = prompt.strip()
            if cal_tokens(prompt) <= MAX_INPUT_LIMIT-MAX_OUTPUT_LIMIT:
                break
        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt
