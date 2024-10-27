from .simple_agent import *

class ViewGenerator(SimpleAgent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = PROMPT_VIEW_GENERATOR, agent_name='view_generator', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, agent_name=agent_name, PROMPT=PROMPT, logger_root=logger_root, logger_file=logger_file)

        self.MAX_ERR_RAISE_CNT = 4
    
    def _generate_column_from_columns_prompt(self, data:TQAData, cols:str, require:str, instance_pool:InstancePool=None):
        head = self.PROMPT['head']
        op_desc = self.PROMPT[GV.NAMES['GEN_NEW_COL']]
        query_temp = self.PROMPT[f"query_{GV.NAMES['GEN_NEW_COL']}_from_column"]
        prompt = ''
        for row_lim in range(len(data.tbl), 0, -2):
            op_demo = copy.deepcopy(self.PROMPT[f"demo_{GV.NAMES['GEN_NEW_COL']}_from_column"])
            table = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c not in cols], cut_line=row_lim)
            col_str = ', '.join([f'`{col}`' for col in cols])
            query = query_temp.format(table=table, col=col_str, question=require)

            if self.retrieve_demo and instance_pool is not None:
                # retrieve demo
                table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c not in cols], cut_line=5)
                ret_ins = instance_pool.retrieve(
                    get_instance(
                        id = data.id, table = table_tmp, 
                        q=f'Given the column {col_str} please generate a new column to answer: {require}', 
                        key=get_key_for_icl(question=query, context=table_tmp),
                        type=f'{self.name}-in_context_learning'),
                    top_k=GV.RETRIEVE_DEMO_NUM
                )

                added_demos = [
                    delete_content_between(
                        s = self.PROMPT['self_correc_ins'].format(context=ins.context, question=ins.q, last_error=ins.last_err, a=ins.a),
                        start='Last Error:',
                        end='Operator:'
                    )
                    for ins in ret_ins
                ]

                op_demo = '\n\n'.join(added_demos)

                op_demo = op_demo.strip()

            if self.self_correction and self.last_log != None:
                query = query.replace('Operator:', 'Last Error: ' + self.last_log + '\n' + 'Operator:')

                # update demo
                if instance_pool is not None:
                    table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c not in cols], cut_line=5)
                    ret_ins = instance_pool.retrieve(
                        get_instance(
                            id = data.id, table = table_tmp, 
                            q=f'Given the column {col_str} please generate a new column to answer: {require}', 
                            last_err=self.last_log, type=f'{self.name}-self_correction', key=self.last_log),
                        top_k=GV.SELF_CORRECTION_NUM
                    )

                    added_demos = [self.PROMPT['self_correc_ins'].format(
                                        context=ins.context, question=ins.q, 
                                        last_error=ins.last_err, a=ins.a) for ins in ret_ins]
                    
                    op_demo = '\n\n'.join(added_demos)

                    # op_demo = op_demo + '\n\n' + '\n\n'.join(added_demos)

                    # demo_lis = op_demo.split('\n\n')
                    # demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                    # op_demo = '\n\n'.join(demo_lis)

                    op_demo = op_demo.strip()
                
            
            prompt = head + '\n\n' + op_desc + '\n\n' + op_demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c not in cols], cut_line=5)
                self.cur_ins = get_instance(
                    id = data.id, table=table_tmp, 
                    q=f'Given the column {col_str} please generate a new column to answer: {require}')
                
                break

        if cal_tokens(prompt) > GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The prompt is too long, the first row is too long!')

        return prompt
    
    def get_physical_op(self, data:TQAData, cols:List[str], require:str):
        self.last_log = None
        self.err_raise_cnt = 0
        
        for col in cols:
            if col not in data.tbl.columns:
                raise ValueError(f'E: The column {col} does not exist in the table!')
        while True:
            prompt = self._generate_column_from_columns_prompt(data, cols, require)
            out = self.gpt.query(prompt)

            try:
                OpClass = AutoOP.deduce_op(out)
                op = OpClass(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)
                break
            except Exception as e:
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.last_log = None

        return op
    
    def execute_physical_op(self, data:TQAData, cols:List[str], require:str, op:SimpleOperator):
        self.last_log = None
        self.err_raise_cnt = 0
        
        for col in cols:
            if col not in data.tbl.columns:
                raise ValueError(f'E: The column {col} does not exist in the table!')
            
        while True:

            try:
                data = op.execute(data)
                self.logger.log_message(msg=f'New Table is:\n{data.tbl}')
                break
            except Exception as e:
                prompt = self._generate_column_from_columns_prompt(data, cols, require)
                out = self.gpt.query(prompt)
                self.logger.log_message(msg='Prompt: ' + prompt)
                self.logger.log_message(msg=f'Output: {out}')
                OpClass = AutoOP.deduce_op(out)
                op = OpClass(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)

                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.last_log = None

        return data, op

    def generate_column_from_columns(self, data:TQAData, cols:List[str], require:str, instance_pool:InstancePool=None):
        self.last_log = None
        self.err_raise_cnt = 0
        self.self_corr_inses = []
        self.icl_inses = []
        
        for col in cols:
            if col not in data.tbl.columns:
                raise ValueError(f'E: The column {col} does not exist in the table!')
        while True:
            prompt = self._generate_column_from_columns_prompt(data, cols, require, instance_pool)
            out = self.gpt.query(prompt)

            self.logger.log_message(msg='Prompt: ' + prompt)
            self.logger.log_message(msg=f'Output: {out}')

            try:
                OpClass = AutoOP.deduce_op(out)
                op = OpClass(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)
                data = op.execute(data)
                self.logger.log_message(msg=f'New Table is:\n{data.tbl}')
                break
            except Exception as e:
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.self_corr_inses.append(
                self.get_self_corr_inses(out)
            )
            self.last_log = None
            self.logger.log_message(msg=f'---- ID: {data.id}, SUCCESSFULLY DEBUG IN {self.err_raise_cnt} times! ----')
        else:
            self.logger.log_message(msg=f'---- ID: {data.id}, NO BUGS! ----')

        table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c not in cols], cut_line=5)
        self.icl_inses.append(
            self.get_icl_inses(out, key=get_key_for_icl(question=prompt, context=table_tmp))
        )

        return data, op


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

def get_key_for_icl(question:str, context:str):
    return f'{context}\nQuestion: {question}'