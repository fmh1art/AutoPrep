from .simple_agent import *

class Cleaner(SimpleAgent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = PROMPT_CLEANER, agent_name='cleaner', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, agent_name=agent_name, PROMPT=PROMPT, logger_root=logger_root, logger_file=logger_file)
        self.MAX_ERR_RAISE_CNT = 4

    def _standardize_prompt(self, data:TQAData, col:str, coltype:str, key:str, instance_pool:InstancePool=None):

        op_desc = self.PROMPT[GV.NAMES[key]]

        query_temp = self.PROMPT['standardize_query']
        op_name = GV.NAMES[key]
        column = col
        format = coltype

        prompt = ''
        for row_lim in range(GV.DEFAULT_ROW_CUT, 0, -2):
            op_demo = copy.deepcopy(self.PROMPT[f'demo_{GV.NAMES[key]}'])
            cot_tbl = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c != col], cut_line=row_lim)
            query = query_temp.format(cot_tbl=cot_tbl, column=column, format=format, op_name=op_name)
            
            if self.retrieve_demo and instance_pool is not None:
                # retrieve demo
                table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c != col], cut_line=5)
                ret_ins = instance_pool.retrieve(
                    get_instance(
                        id = data.id, table = table_tmp, 
                        q=f'please standardize the column `{column}` to {format} format.', 
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

                # op_demo = op_demo + '\n\n' + '\n\n'.join(added_demos)
                
                # demo_lis = op_demo.split('\n\n')
                # demo_lis = [demo_lis[0]] + added_demos + demo_lis[1:]
                # op_demo = '\n\n'.join(demo_lis)

                op_demo = op_demo.strip()
            
            if self.self_correction and self.last_log != None and len(self.last_log)!=0:

                query = query.replace('Operator:', 'Last Error: ' + self.last_log + '\n' + 'Operator:')

                # update demo
                if instance_pool is not None:
                    # update demo for self-correction
                    table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c != col], cut_line=5)
                    ret_ins = instance_pool.retrieve(
                        get_instance(
                            id = data.id, table = table_tmp, 
                            q=f'please standardize the column `{column}` to {format} format.', 
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

            prompt = op_desc + '\n\n' + op_demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c != col], cut_line=5)
                self.cur_ins = get_instance(
                    id = data.id, table = table_tmp, 
                    q=f'please standardize the column `{column}` to {format} format.'
                )
                break

        if len(prompt) == 0:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')

        return prompt
    
    def get_physical_op(self, data:TQAData, col:str, coltype:str, instance_pool:InstancePool=None):
        self.last_log = None
        self.err_raise_cnt = 0

        if coltype == 'datetime':
            key = 'STAND_DATETIME'
            OP = StandDatetime
        elif coltype == 'numerical':
            key = 'STAND_NUMERICAL'
            OP = StandNumerical
        else:
            raise ValueError(f'E: The column type is not supported for standardization: {coltype}')
        
        op = Operator(op_type='empty_operator')
        while True:
            prompt = self._standardize_prompt(data, col, coltype, key, instance_pool)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')

            try:
                op = OP(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)
                break
            except Exception as e:
                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.last_log = None

        return op
    
    def execute_physical_op(self, data:TQAData, col:str, coltype:str, op:SimpleOperator):
        self.last_log = None
        self.err_raise_cnt = 0

        if coltype == 'datetime':
            key = 'STAND_DATETIME'
            OP = StandDatetime
        elif coltype == 'numerical':
            key = 'STAND_NUMERICAL'
            OP = StandNumerical
        else:
            raise ValueError(f'E: The column type is not supported for standardization: {coltype}')
        
        op = Operator(op_type='empty_operator')
        while True:

            try:
                data = op.execute(data)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'New Table is:\n{data.tbl}')
                break
            except Exception as e:
                prompt = self._standardize_prompt(data, col, coltype, key)
                out = self.gpt.query(prompt)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')
                op = OP(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)

                self._record_error_raise(e)
        
        if self.last_log is not None:
            self.last_log = None

        return data, op
    

    def standardize_coltype(self, data:TQAData, col:str, coltype:str, instance_pool:InstancePool=None):
        self.last_log = None
        self.err_raise_cnt = 0
        self.self_corr_inses = []
        self.icl_inses = []

        if coltype == 'datetime':
            key = 'STAND_DATETIME'
            OP = StandDatetime
        elif coltype == 'numerical':
            key = 'STAND_NUMERICAL'
            OP = StandNumerical
        else:
            raise ValueError(f'E: The column type is not supported for standardization: {coltype}')
        
        op = Operator(op_type='empty_operator')
        while True:
            prompt = self._standardize_prompt(data, col, coltype, key, instance_pool)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')

            try:
                op = OP(llm_model=self.gpt.model, log_root=self.logger.root, log_file=self.logger.log_file)
                op.complete_args_with_output(data, out)
                data = op.execute(data)
                self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'New Table is:\n{data.tbl}')
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

        table_tmp = df_to_str_columns_add_quo(df=data.tbl, exclude_cols=[c for c in data.tbl.columns if c != col], cut_line=5)
        self.icl_inses.append(
            self.get_icl_inses(
                out,
                key=get_key_for_icl(data.question, table_tmp)
            )
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