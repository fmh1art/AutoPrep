from .simple_agent import *
import sqlite3

class NL2SQLer(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='nl2sqler', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)
        self.conn = sqlite3.connect(':memory:')

    def process(self, data:TQAData, instance_pool:InstancePool=None):
        self.last_log = None
        self.self_corr_inses = []
        self.icl_inses = []
        self.err_raise_cnt = 0
        self.sql, self.ans = 'INIT', 'INIT'

        data.tbl = add_row_number_to_df(data.tbl, col_name='row_id')
        data = update_TData_col_type(data, col_type={'row_id': 'numerical'})
        
        while True:
            prompt = self._ans_gen_prompt(data, instance_pool)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')
            try:
                sql = parse_any_string(out, hard_replace='SQL:')
                sql, _ = post_process_sql(sql, data.tbl, data.title)
                ans = self.exe_sql(sql, data)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'tbl: {df_to_cotable(ans)}')
                break
            except Exception as e:
                self.sql = sql
                self.ans = str(e)
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.self_corr_inses.append(
                self.get_self_corr_inses(out)
            )
            self.last_log = None
        
        _, table_ret_tmp = ansketch_nl2sql_prompt(data, cut_line=3, specify_line=True)
        self.icl_inses.append(
            self.get_icl_inses(
                out, 
                key=get_key_for_icl(
                    data.question, list(data.tbl.columns), table_ret_tmp
                )
            )
        )

        return sql, ans

    def exe_sql(self, sql: str, data:TQAData):
        tbl = data.tbl
        tbl.to_sql('w', self.conn, index=False, if_exists='replace')
        ans = pd.read_sql(sql, self.conn)
        return ans

    def _ans_gen_prompt(self, data:TQAData, instance_pool:InstancePool=None):
        tbl, question, title = data.tbl, data.question, data.title

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            demo = copy.deepcopy(DEMO_NL2SQLER)
            create_table, table_ret = ansketch_nl2sql_prompt(data, cut_line=row_lim)
            query = QUERY_NL2SQLER.format(create_table_text=create_table, table=table_ret, question=question, title=title)

            if self.retrieve_demo and instance_pool is not None:
                create_table_tmp, table_ret_tmp = ansketch_nl2sql_prompt(data, cut_line=3, specify_line=True)
                ret_ins = instance_pool.retrieve(
                    get_instance(id = data.id,
                                 create_table=create_table_tmp,
                                 title=data.title,
                                 table=table_ret_tmp,
                                 question=question,
                                 type=f'{self.name}-in_context_learning', 
                                 key=get_key_for_icl(question, list(tbl.columns), context=table_ret_tmp)),
                    top_k=GV.RETRIEVE_DEMO_NUM
                )
                added_demos = [
                    delete_content_between(
                        s = SELF_CORREC_INS_NL2SQLER.format(context=ins.context, question=ins.q, last_error=ins.last_err, a=ins.a),
                        start='Last Error:',
                        end='SQL:'
                    )
                     for ins in ret_ins
                ]

                demo = '\n\n'.join(added_demos)

                # demo = demo + '\n\n' + '\n\n'.join(added_demos)

                # demo_lis = demo.split('\n\n')
                # demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                # demo = '\n\n'.join(demo_lis)

                demo = demo.strip()

            if self.self_correction and self.last_log is not None:
                query = query.replace('SQL:', 'Last Error: ' + self.last_log + '\n' + 'SQL:')

                if instance_pool is not None:
                    create_table_tmp, table_ret_tmp = ansketch_nl2sql_prompt(data, cut_line=3, specify_line=True)
                    ret_ins = instance_pool.retrieve(
                            get_instance(id = data.id,
                                        create_table=create_table_tmp,
                                        title=data.title,
                                        table=table_ret_tmp,
                                        question=question,
                                        last_err=self.last_log,
                                        type=f'{self.name}-self_correction',
                                        key=self.last_log),
                        top_k=GV.SELF_CORRECTION_NUM
                    )

                    added_demos = [SELF_CORREC_INS_NL2SQLER.format(
                                        context=ins.context, question=ins.q, 
                                        last_error=ins.last_err, a=ins.a) for ins in ret_ins]
                    
                    demo = '\n\n'.join(added_demos)

                    # demo = demo + '\n\n' + '\n\n'.join(added_demos)

                    # demo_lis = demo.split('\n\n')
                    # demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                    # demo = '\n\n'.join(demo_lis)

                    demo = demo.strip()

            
            prompt = demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                create_table_tmp, table_ret_tmp = ansketch_nl2sql_prompt(data, cut_line=3, specify_line=True)
                self.cur_ins = get_instance(
                    id = data.id, create_table=create_table_tmp, 
                    title=data.title, table=table_ret_tmp, question=question
                )
                break
        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt

def get_key_for_icl(question:str, columns:List[str], context: str):
    return f'{context}\nQuestion: {question}\ncolumns: {", ".join(columns)}'

def get_instance(id='None', create_table='None', title='None', table='None', question='None', last_a='None', last_err='None', a='None', type='None', key='None'):
    if key == 'None':
        key = question
        
    return SelfCorrectionInstance(
        id = id,
        context=f"""{create_table}
/*
Title: {title}
example rows:
SELECT * FROM w LIMIT 3;
{table}
*/""",
        q=question,
        last_a=last_a,
        last_err=last_err,
        a=a,
        type=type,
        key=key
    )