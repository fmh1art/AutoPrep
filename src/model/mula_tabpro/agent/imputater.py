from .simple_agent import *

class Imputater(Agent):
    def __init__(self, llm_name='gpt-3.5-turbo-0301', chains: List = [InitOP()], PROMPT = None, agent_name='imputater', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        super().__init__(llm_name=llm_name, chains=chains, PROMPT=PROMPT, agent_name=agent_name, logger_root=logger_root, logger_file=logger_file)
        self.MAX_ROW_NUM = 5
        self.MAX_ROW_IMPUTATE = 80
    
    def _standardize_prompt(self, records: List, is_cleans: List, col:str, coltype:str, key:str, begin_idx:int, sql: str, instance_pool:InstancePool=None):
        
        demo = IMPUTATER_PROMPT[f"demo_{GV.NAMES[key]}"]
        query_temp = IMPUTATER_PROMPT['query_standardize']
        
        prompt = ''
        for row_lim in range(self.MAX_ROW_NUM, 0, -2):
            data = {}
            data_id2record_id = {} # data_id : record_id
            for i in range(row_lim):
                record_id = i + begin_idx
                if record_id >= len(records):
                    break
                ori_val, clean_val = records[record_id]
                is_clean = is_cleans[record_id]
                if not is_clean:
                    data[i+1] = {col: ori_val, f'{col}_cleaned': '[?]'}
                    data_id2record_id[i+1] = record_id
                else:
                    data[i+1] = {col: ori_val, f'{col}_cleaned': clean_val}

            table = df_to_json_dict(data)
            rows = ', '.join([str(idx) for idx in data_id2record_id.keys()])
            query = query_temp.format(table=table, column=col, coltype=coltype, rows=rows, sql=sql)

            prompt = demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                break

        if cal_tokens(prompt) > GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The first row is too long!')
        
        return prompt, len(data), data_id2record_id

    def _standardize_parse_output(self, out:str, data_id2record_id:dict, col:str):
        # find the first { and the last}
        out = out.replace('\t', '').replace('\n', '')
        first_idx = out.find('{')
        last_idx = out.rfind('}')

        if first_idx == -1 or last_idx == -1:
            raise ValueError(f'Error in parsing the output: {out}')

        out = out[first_idx: last_idx+1]

        try:
            cleaned_by_llm = eval(out)
        except:
            raise ValueError(f'Error in parsing the output: {out}')
        
        if type(cleaned_by_llm) != dict:
            raise ValueError(f'Output is not a dict.')
        
        for k in list(cleaned_by_llm.keys()):
            new_key = int(k)
            if new_key not in cleaned_by_llm:
                cleaned_by_llm[new_key] = copy.deepcopy(cleaned_by_llm[k])
                cleaned_by_llm.pop(k)
        
        for data_id in data_id2record_id.keys():
            if data_id not in cleaned_by_llm:
                raise ValueError(f'The data_id {data_id} is not in the output.')
        
        for k in cleaned_by_llm.keys():
            if type(cleaned_by_llm[k]) != dict:
                raise ValueError(f'The format of the output is not correct.')
            if col not in cleaned_by_llm[k] or f'{col}_cleaned' not in cleaned_by_llm[k]:
                raise ValueError(f'The format of the output is not correct.')
        
        return cleaned_by_llm

    def standardize_imputate(self, origin_data:TQAData, cleaned_data:TQAData, col:str, coltype:str, sql: str, instance_pool:InstancePool=None):
        self.self_corr_inses = []
        
        self.err_raise_cnt = 0
        def get_standardize_information(origin_data:TQAData, cleaned_data:TQAData, col:str):
            records, is_cleans = [], []
            ori_tbl = origin_data.tbl
            cleaned_tbl = cleaned_data.tbl
            for ori_val, clean_val in zip(ori_tbl[col], cleaned_tbl[col]):
                records.append((ori_val, clean_val))
                if '[n.a.]' in str(clean_val):
                    is_cleans.append(False)
                else:
                    is_cleans.append(True)
            return records, is_cleans
        
        if coltype == 'datetime':
            key = 'STAND_DATETIME'
        elif coltype == 'numerical':
            key = 'STAND_NUMERICAL'
        else:
            raise ValueError(f'coltype {coltype} is not supported.')
        
        records, is_cleans = get_standardize_information(origin_data, cleaned_data, col)

        begin_idx = 0
        while begin_idx < self.MAX_ROW_IMPUTATE and begin_idx < len(records):
            # whether need imputate
            need_imputate = False
            for is_clean in is_cleans[begin_idx: begin_idx + self.MAX_ROW_NUM]:
                if not is_clean:
                    need_imputate = True
                    break
            
            # 1. not need to imputate the values
            if not need_imputate:
                begin_idx += self.MAX_ROW_NUM
                continue

            # 2. need to imputate the values
            # - 2.1 get the imputation result
            prompt, row_num, data_id2record_id = self._standardize_prompt(records=records, is_cleans=is_cleans,
                                                col=col, coltype=coltype, key=key, begin_idx=begin_idx, sql=sql, instance_pool=instance_pool)
            out = self.gpt.query(prompt)

            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Prompt: {prompt}')
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')    

            try:
                cleaned_by_llm = self._standardize_parse_output(out, data_id2record_id, col)
            except Exception as e:
                self._record_error_raise(e)
                continue

            self.err_raise_cnt = 0
            
            # - 2.2 update the cleaned data
            for data_id, record_id in data_id2record_id.items():
                val_dic = cleaned_by_llm[data_id]
                _, clean_val = records[record_id]

                imputate_val = val_dic[f'{col}_cleaned']
                cleaned_data.tbl.iloc[record_id][col] = imputate_val
            
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Imputate {col} from {begin_idx} to {begin_idx+row_num-1}') 
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Get New Table:\n{cleaned_data.tbl}')

            # 3. update the begin_idx
            begin_idx += row_num
            
            if self.last_log is not None:
                self.last_log = None
            
        return cleaned_data
    
    def _col_generate_prompt(self, records: List, succ_generates: List, source_cols:List[str], target_col:str, begin_idx:int, sql: str, instance_pool:InstancePool=None):
        demo = IMPUTATER_PROMPT[f"demo_{GV.NAMES['GEN_NEW_COL']}"]
        query_temp = IMPUTATER_PROMPT['query_generate']

        prompt = ''
        for row_lim in range(self.MAX_ROW_NUM, 0, -2):
            data = {}
            data_id2record_id = {}
            for i in range(row_lim):
                record_id = i + begin_idx
                if record_id >= len(records):
                    break
                record = copy.deepcopy(records[record_id])
                succ_gen = succ_generates[record_id]
                if not succ_gen:
                    record[target_col] = '[?]'
                    data_id2record_id[i+1] = record_id

                data[i+1] = record

            table = df_to_json_dict(data)
            rows = ', '.join([str(idx) for idx in data_id2record_id.keys()])
            column_flag = 'columns' if len(source_cols) > 1 else 'column'
            column_str = ' and '.join(source_cols)
            new_col = target_col

            query = query_temp.format(table=table, new_col=new_col, column_flag=column_flag, column_str=column_str, rows=rows, sql=sql)

            prompt = demo + '\n\n' + query
            if cal_tokens(prompt) <= GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
                break

        if cal_tokens(prompt) > GV.MAX_INPUT_LIMIT-GV.MAX_OUTPUT_LIMIT:
            raise ValueError(f'E: The first row is too long!')
        
        return prompt, len(data), data_id2record_id

    def _col_generate_parse_output(self, out:str, data_id2record_id:dict, target_col:str):
        # find the first { and the last}
        first_idx = out.find('{')
        last_idx = out.rfind('}')

        if first_idx == -1 or last_idx == -1:
            raise ValueError(f'Error in parsing the output: {out}')

        out = out[first_idx: last_idx+1]

        try:
            generated_by_llm = eval(out)
        except:
            raise ValueError(f'Error in parsing the output: {out}')
        
        if type(generated_by_llm) != dict:
            raise ValueError(f'Output is not a dict.')
        
        for k in list(generated_by_llm.keys()):
            new_key = int(k)
            if new_key not in generated_by_llm:
                generated_by_llm[new_key] = copy.deepcopy(generated_by_llm[k])
                generated_by_llm.pop(k)
        
        for data_id in data_id2record_id.keys():
            if data_id not in generated_by_llm:
                raise ValueError(f'The data_id {data_id} is not in the output.')
        
        for k in generated_by_llm.keys():
            if type(generated_by_llm[k]) != dict:
                raise ValueError(f'The format of the output is not correct.')
            if target_col not in generated_by_llm[k]:
                raise ValueError(f'The target column {target_col} is not in the output of row {k}.')
        
        return generated_by_llm

    def col_generate_imputate(self, data:TQAData, op:GenNewCol, sql: str, instance_pool:InstancePool=None):
        self.err_raise_cnt = 0

        def get_records(data:TQAData, source_cols:List[str], target_col:str):
            records = []
            success_generates = []
            df = data.tbl
            tol_cols = source_cols + [target_col]
            for _, row in df.iterrows():
                record = {}
                for col in tol_cols:
                    record[col] = row[col]
                records.append(record)
                if '[n.a.]' not in str(row[target_col]):
                    success_generates.append(True)
                else:
                    success_generates.append(False)
            return records, success_generates

        # 'new_column': new_column, 'func': func, 'source_cols': source_cols
        new_col = op.args.get('new_column')
        source_cols = op.args.get('source_cols')

        records, success_generates = get_records(data, source_cols, new_col)

        begin_idx = 0
        while begin_idx < self.MAX_ROW_IMPUTATE and begin_idx < len(records):
            # whether need imputate
            need_imputate = False
            for success_generate in success_generates[begin_idx: begin_idx + self.MAX_ROW_NUM]:
                if not success_generate:
                    need_imputate = True
                    break
            
            # 1. not need to imputate the values
            if not need_imputate:
                begin_idx += self.MAX_ROW_NUM
                continue

            # 2. need to imputate the values
            # - 2.1 get the imputation result
            prompt, row_num, data_id2record_id = self._col_generate_prompt(records=records, succ_generates=success_generates,
                                                source_cols=source_cols, target_col=new_col, begin_idx=begin_idx, sql=sql
                                                , instance_pool=instance_pool)
            out = self.gpt.query(prompt)

            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Prompt: {prompt}')
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Output: {out}')    

            try:  
                generated_by_llm = self._col_generate_parse_output(out, data_id2record_id, new_col)
            except Exception as e:
                self._record_error_raise(e)
                continue

            self.err_raise_cnt = 0
            
            # - 2.2 update the cleaned data
            for data_id, record_id in data_id2record_id.items():
                val_dic = generated_by_llm[data_id]
                record = records[record_id]

                old_val = record[new_col]
                imputate_val = val_dic[new_col]
                # replace the value in record_id-th row
                data.tbl.iloc[record_id][new_col] = imputate_val
            
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Imputate {new_col} from {begin_idx} to {begin_idx+row_num-1}') 
            self.logger.log_message(line_limit=GV.cut_log, level='debug', msg=f'Get New Table:\n{data.tbl}')

            # 3. update the begin_idx
            begin_idx += row_num
            
            if self.last_log is not None:
                self.last_log = None

        return data