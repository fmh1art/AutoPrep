from .simple_agent import *

class DirectPromptingManager(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='direct_prompting_manager', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)

    def process(self, data:TQAData, instance_pool:InstancePool=None):
        self.last_log = None
        self.self_corr_inses = []
        self.icl_inses = []
        self.err_raise_cnt = 0
        
        while True:
            prompt = self._ans_gen_prompt(data, instance_pool)
            out = self.gpt.query(prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg='Prompt: ' + prompt)
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')
            parsed_out = parse_any_string(out).lower()
            try:
                self.check_output(parsed_out)
                rel_cols, aug_reqs, nor_reqs = self._generate_dataprep_requirements(data, parsed_out)
                break
            except ValueError as e:
                self._record_error_raise(e)
                continue
        
        if self.last_log is not None:
            self.self_corr_inses.append(
                self.get_self_corr_inses(out)
            )
            self.last_log = None

        self.icl_inses.append(
            self.get_icl_inses(out)
        )

        return rel_cols, aug_reqs, nor_reqs
    
    def check_output(self, out: str):
        if not('(1)' in out and '(2)' in out and '(3)' in out):
            raise ValueError(f'E: The output does not contain three aspects, please generate follow the above format: {out}')
    
    def _generate_dataprep_requirements(self, out: str):
        # 1. split the out into three parts
        one_part = out[out.find('(1)')+4: out.find('(2)')].strip()
        two_part = out[out.find('(2)')+4: out.find('(3)')].strip()
        three_part = out[out.find('(3)')+4:].strip()

        # 2. get the related columns
        col_str = one_part.replace('(1)', '').replace('related columns:').strip()
        rel_cols = [x.strip() for x in col_str.split(',')]
        if len(rel_cols) == 0:
            raise ValueError(f'E: No related columns found: {one_part}')
        
        # 3. get augmenter requirements
        aug_reqs = []
        sent_str = two_part.replace('(2)', '').strip()
        if 'none.' not in sent_str:
            for sent in sent_str.split(';'):
                sent = sent.strip()
                if len(sent) != 0:
                    aug_reqs.append(sent)

        # 4. get normalizer requirements
        nor_reqs = []
        sent_str = three_part.replace('(3)', '').strip()
        if 'none.' not in sent_str:
            for sent in sent_str.split(';'):
                sent = sent.strip()
                if len(sent) != 0:
                    nor_reqs.append(sent)

        return rel_cols, aug_reqs, nor_reqs


    def _ans_gen_prompt(self, data:TQAData, instance_pool:InstancePool=None):
        tbl, question = data.tbl, data.question

        row_len = len(tbl)
        prompt = ''
        for row_lim in range(row_len, 0, -2):
            demo = copy.deepcopy(DEMO_MANAGER)
            _, table_ret = binder_nl2sql_prompt(data, cut_line=row_lim)
            query = QUERY_MANAGER.format(table=table_ret, question=question, title=data.title)

            if self.retrieve_demo and instance_pool is not None:
                # update demo for self-correction
                _, table_tmp = binder_nl2sql_prompt(data, cut_line=3)
                ret_ins = instance_pool.retrieve(
                    get_instance(
                        id = data.id, title=data.title, table=table_tmp, q=question, type=f'{self.name}-in_context_learning'),
                    top_k=GV.RETRIEVE_DEMO_NUM
                )
                
                added_demos = [
                    delete_content_between(
                        s = SELF_CORREC_INS_MANAGER.format(context=ins.context, question=ins.q, last_error=ins.last_err, a=ins.a),
                        start='Last Error:',
                        end='Requirements:'
                    )
                    for ins in ret_ins
                ]
                
                demo = demo + '\n\n' + '\n\n'.join(added_demos)
                demo = demo.strip()

            if self.self_correction and self.last_log is not None:
                query = query.replace('Requirements:', 'Last Error: ' + self.last_log + '\nRequirements:')
                # update demo
                if instance_pool is not None:
                    # update demo for self-correction
                    _, table_tmp = binder_nl2sql_prompt(data, cut_line=3)
                    ret_ins = instance_pool.retrieve(
                        get_instance(
                            id = data.id, title=data.title, table=table_tmp, q=question, 
                            last_err=self.last_log, type=f'{self.name}-self_correction', key=self.last_log),
                        top_k=GV.SELF_CORRECTION_NUM
                    )
                    
                    added_demos = [SELF_CORREC_INS_MANAGER.format(
                                        context=ins.context, question=ins.q, 
                                        last_error=ins.last_err, a=ins.a) for ins in ret_ins]
                    demo = demo + '\n\n' + '\n\n'.join(added_demos)
                    demo = demo.strip()


            prompt = demo + '\n\n' + query

            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                _, table_tmp = binder_nl2sql_prompt(data, cut_line=3)
                self.cur_ins = get_instance(id = data.id, title=data.title, table=table_tmp, q=question)
                break
            
        if cal_tokens(prompt) > GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The prompt is empty, the first row is too long!')
        return prompt

def get_instance(id='None', title='None', table='None', q='None', last_a='None', last_err='None', a='None', type='None', key='None'):
    if key == 'None':
        key = q
    return SelfCorrectionInstance(
        id = id,
        context=f"""Title: {title}
/*
{table}
*/""", 
        q=q,
        last_a=last_a,
        last_err=last_err,
        a=a,
        type=type,
        key=key
    )