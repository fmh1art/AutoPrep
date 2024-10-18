from .simple_agent import *
import sqlite3

class Binder(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='binder', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)
        self.conn = sqlite3.connect(':memory:')

    def process(self, data:TQAData, instance_pool:InstancePool=None):
        self.last_log = None
        self.self_corr_inses = []
        self.icl_inses = []
        self.err_raise_cnt = 0
        
        while True:
            prompt = self._ans_gen_prompt(data, instance_pool)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=cut_log, level='debug', msg=f'Output: {out}')
            binder_sql = parse_any_string(out)
            try:
                self.check_binder_sql(binder_sql)
                post_sql, rel_cols = post_process_sql(binder_sql, data.tbl, data.title)
                if len(rel_cols) == 0:
                    raise ValueError(f'E: No related columns found in the generated binder_sql: {post_sql}, please use specific column names instead of "*"!')
                map_requires = self._extract_mapping_requirements(post_sql, rel_cols)
                break
            except ValueError as e:
                self._record_error_raise(e)
                continue
        
        if self.last_log is not None:
            self.self_corr_inses.append(
                self.get_self_corr_inses(out)
            )
            self.last_log = None
        
        _, table_ret_tmp = binder_nl2sql_prompt(data, cut_line=3, specify_line=True)
        self.icl_inses.append(
            self.get_icl_inses(
                out, 
                key=get_key_for_icl(
                    data.question, list(data.tbl.columns), table_ret_tmp
                )
            )
        )

        return post_sql, rel_cols, map_requires
    
    def check_binder_sql(self, sql: str):
        unacceptable_keywords = ['SUBSTRING(', 'SUBSTRING_INDEX(', 'SPLIT_PART(', 'SPLIT(']
        include_dict = {}
        for keyword in unacceptable_keywords:
            if keyword in sql.capitalize():
                include_dict[keyword] = True

        if len(include_dict) > 0:
            key_str = ','.join([x[:-1] for x in include_dict.keys()])
            raise ValueError(f'E: The SQL contains unacceptable keywords: {key_str}. Use MAP grammar intead.')

    def exe_sql(self, sql: str, data:TQAData):
        tbl = data.tbl
        tbl.to_sql('w', self.conn, index=False, if_exists='replace')
        ans = pd.read_sql(sql, self.conn)
        return ans
    
    def _extract_mapping_requirements(self, binder_sql:str, related_cols: List[str]):
        temp_sql = copy.deepcopy(binder_sql)
        for col in related_cols:
            temp_sql = temp_sql.replace(col, '#'*len(col))

        idx = 0
        ret = []
        while idx < len(binder_sql):
            # binder_sql: SELECT MAP("extract country from cyclist"; `Cyclist`) AS Country, COUNT(*) AS C
            # temp_sql: SELECT MAP("extract country from cyclist"; `#######`) AS Country, COUNT(*) AS C
            if binder_sql[idx: idx+4] == 'MAP(': # find the begin of the mapping statement
                # find the idx of ';'
                ques_end_idx = temp_sql.find(';', idx)
                col_end_idx = temp_sql.find(')', ques_end_idx)
                if ques_end_idx == -1 or col_end_idx == -1:
                    raise ValueError(f'E: The mapping requirement is not complete: {binder_sql}')

                question = binder_sql[idx+5: ques_end_idx-1].strip()
                col_str = binder_sql[ques_end_idx+1: col_end_idx].strip()
                flag_cnt = col_str.count('`')
                if flag_cnt < 2 or flag_cnt % 2 != 0:
                    raise ValueError(f'E: The column name should be wrapped by `: {binder_sql}')
                cols = col_str.split('`')[1::2]

                ret.append((question, tuple(cols)))
                idx = col_end_idx

            idx += 1

        # return List of (requirement, col)
        return ret

    def _ans_gen_prompt(self, data:TQAData, instance_pool:InstancePool=None):
        tbl, question = data.tbl, data.question
        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            demo = copy.deepcopy(DEMO_BINDER)
            create_table, table_ret = binder_nl2sql_prompt(data, cut_line=row_lim)
            query = QUERY_BINDER.format(create_table_text=create_table, table=table_ret, question=question, title=data.title)

            if self.retrieve_demo and instance_pool is not None:
                # update demo for self-correction
                create_table_tmp, table_ret_tmp = binder_nl2sql_prompt(data, cut_line=3, specify_line=True)
                ret_ins = instance_pool.retrieve(
                    get_instance(id = data.id,
                                 create_table=create_table_tmp,
                                 title=data.title,
                                 table=table_ret_tmp,
                                 question=question,
                                 type=f'{self.name}-in_context_learning', 
                                 key=get_key_for_icl(question, list(tbl.columns), table_ret_tmp)),
                    top_k=RETRIEVE_DEMO_NUM
                )
                
                added_demos = [
                    delete_content_between(
                        s = SELF_CORREC_INS_BINDER.format(context=ins.context, question=ins.q, last_error=ins.last_err, a=ins.a),
                        start='Last Error:',
                        end='NeuralSQL:'
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
                query = query.replace('NeuralSQL:', 'Last Error: ' + self.last_log + '\nNeuralSQL:')

                # update demo
                if instance_pool is not None:
                    # update demo for self-correction
                    create_table_tmp, table_ret_tmp = binder_nl2sql_prompt(data, cut_line=3, specify_line=True)
                    ret_ins = instance_pool.retrieve(
                        get_instance(id = data.id,
                                     create_table=create_table_tmp,
                                     title=data.title,
                                     table=table_ret_tmp,
                                     question=question,
                                     last_err=self.last_log,
                                     type=f'{self.name}-self_correction',
                                     key=self.last_log),
                        top_k=SELF_CORRECTION_NUM
                    )
                    
                    added_demos = [SELF_CORREC_INS_BINDER.format(
                                        context=ins.context, question=ins.q, 
                                        last_error=ins.last_err, a=ins.a) for ins in ret_ins]
                    
                    demo = '\n\n'.join(added_demos)
                    
                    # demo = demo + '\n\n' + '\n\n'.join(added_demos)

                    # demo_lis = demo.split('\n\n')
                    # demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                    # demo = '\n\n'.join(demo_lis)
                    
                    demo = demo.strip()

            prompt = demo + '\n\n' + query
            if cal_tokens(prompt) <= MAX_INPUT_LIMIT-MAX_OUTPUT_LIMIT:
                create_table_tmp, table_ret_tmp = binder_nl2sql_prompt(data, cut_line=3, specify_line=True)

                self.cur_ins = get_instance(
                    id = data.id, create_table=create_table_tmp, 
                    title=data.title, table=table_ret_tmp, question=question
                )
                break
            
        if cal_tokens(prompt) > MAX_INPUT_LIMIT-MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt


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

def get_key_for_icl(question:str, columns:List[str], context:str):
    return f'{context}\nQuestion: {question}\ncolumns: {", ".join(columns)}'