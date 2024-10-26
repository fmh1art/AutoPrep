from .simple_agent import *

class ColTypeDeducer(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='coltype_deducer', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)

    def process(self, data:TQAData, related_columns:List[str], sql: str, instance_pool:InstancePool=None):
        self.last_log = None
        self.err_raise_cnt = 0
        self.self_corr_inses = []
        self.icl_inses = []
        if len(related_columns) == 0:
            raise ValueError(f'E: No related columns found in the SQL: {sql}')

        while True:
            try:
                prompt = self._ans_gen_prompt(data, related_columns, sql, instance_pool)
                out = self.gpt.query(prompt)

                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')
                
                coltype_dict = parse_coltype_dict(out)
                if len(coltype_dict) == 0:
                    raise ValueError(f'E: No column type deduced from the output: {out}')
                
                for col in related_columns:
                    if col not in coltype_dict:
                        raise ValueError(f'E: Column {col} not found in the output: {out}')
                    t = coltype_dict[col]
                    if t not in ['string', 'numerical', 'datetime']:
                        raise ValueError(f'E: Column type {t} not supported!')
                break
            except Exception as e:
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.self_corr_inses.append(
                self.get_self_corr_inses(out)
            )
            self.last_log = None
        
        self.icl_inses.append(
            self.get_icl_inses(out)
        )
        
        return coltype_dict
    
    def exe_sql(self, sql: str, data:TQAData):
        tbl = data.tbl
        tbl.to_sql('w', self.conn, index=False, if_exists='replace')
        ans = pd.read_sql(sql, self.conn)
        return ans

    def _ans_gen_prompt(self, data:TQAData, related_columns: List[str], sql: str, instance_pool:InstancePool=None):
        tbl = data.tbl
        exclude_cols = [col for col in tbl.columns if col not in related_columns]

        head = HEAD_COLTYPE_DEDUCER

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            demo = copy.deepcopy(DEMO_COLTYPE_DEDUCER)
            table = df_to_str_columns(df=tbl, cut_line=row_lim, exclude_cols=exclude_cols)
            related_col_str = ', '.join(related_columns)
            query = QUERY_COLTYPE_DEDUCER.format(table=table, sql=sql, columns=related_col_str)
            
            if self.retrieve_demo and instance_pool is not None:
                table_tmp = df_to_str_columns(df=tbl, cut_line=3, exclude_cols=exclude_cols)
                ret_ins = instance_pool.retrieve(
                    get_instance(
                        id=data.id, table=table_tmp, q=f'SQL: {sql}\nRelated Columns: {related_col_str}', type=f'{self.name}-in_context_learning'
                    ),
                    top_k=GV.RETRIEVE_DEMO_NUM
                )
                
                added_demos = [
                    delete_content_between(
                        s = SELF_CORREC_INS_DEDUCER.format(context=ins.context, question=ins.q, last_error=ins.last_err, a=ins.a),
                        start='Last Error:',
                        end='Column Type Dict:'
                    )
                    for ins in ret_ins
                ]
                    
                # demo = demo + '\n\n' + '\n\n'.join(added_demos)

                demo_lis = demo.split('\n\n')
                demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                demo = '\n\n'.join(demo_lis)

                demo = demo.strip()

            if self.self_correction and self.last_log != None:
                query = query.replace('Column Type Dict:', 'Last Error: ' + self.last_log + '\nColumn Type Dict:')

                # update demo
                if instance_pool is not None:
                    table_tmp = df_to_str_columns(df=tbl, cut_line=3, exclude_cols=exclude_cols)
                    ret_ins = instance_pool.retrieve(
                        get_instance(
                            id=data.id, table=table_tmp,
                            q=f'SQL: {sql}\nRelated Columns: {related_col_str}',
                            last_err=self.last_log, type=f'{self.name}-self_correction'
                        ),
                        top_k=GV.SELF_CORRECTION_NUM
                    )

                    added_demos = [SELF_CORREC_INS_DEDUCER.format(
                                        context=ins.context, question=ins.q, 
                                        last_error=ins.last_err, a=ins.a) for ins in ret_ins]
                    
                    # demo = demo + '\n\n' + '\n\n'.join(added_demos)

                    demo_lis = demo.split('\n\n')
                    demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                    demo = '\n\n'.join(demo_lis)

                    demo = demo.strip()
            
            prompt = head + '\n\n' + demo + '\n\n' + query
            
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                table_tmp = df_to_str_columns(df=tbl, cut_line=3, exclude_cols=exclude_cols)
                self.cur_ins = get_instance(id = data.id, table=table_tmp, 
                                            q=f'SQL: {sql}\nRelated Columns: {related_col_str}')
                break
        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt


def get_instance(id='None', table='None', q='None', last_a='None', last_err='None', a='None', type='None', key='None'):
    if key == 'None':
        key = q
        
    return SelfCorrectionInstance(
        id = id,
        context=table,
        q=q,
        last_a=last_a,
        last_err=last_err,
        a=a,
        type=type,
        key=key
    )