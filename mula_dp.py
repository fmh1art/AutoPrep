import copy, random
import pickle as pkl

from typing import List, Tuple
from src.tools.utils import *
from global_values import *
from src.tools.logger import Logger
from src.data import TQAData
from src.model.mula_tabpro.agent import Binder, ViewGenerator, Imputater, ColTypeDeducer, Cleaner

class MultiAgentDataPrep:
    def __init__(self, llm_name:str, logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{TABLELLM_VERSION}.log', temp_data_path = MULTIA_TEMP_DATA_PATH):
        self.llm_name = llm_name
        self.binder = Binder(llm_name=LLM_DICT['binder'], logger_root=logger_root, logger_file=logger_file)
        self.view_gen = ViewGenerator(llm_name=LLM_DICT['view_generator'], logger_root=logger_root, logger_file=logger_file)
        self.imputater = Imputater(llm_name=LLM_DICT['imputater'], logger_root=logger_root, logger_file=logger_file)
        self.coltype_deducer = ColTypeDeducer(llm_name=LLM_DICT['coltype_deducer'], logger_root=logger_root, logger_file=logger_file)
        self.cleaner = Cleaner(llm_name=LLM_DICT['cleaner'], logger_root=logger_root, logger_file=logger_file)
        self.logger = Logger(name='MultiAgentDataPrep', root=logger_root, log_file=logger_file)
        self.temp_data_path = temp_data_path
        self.self_corr_inses = []
        self.icl_inses = []

        self.temp_relcol_mapreq_bindersql = {}
        if os.path.exists(self.temp_data_path):
            try:
                self.temp_relcol_mapreq_bindersql = pkl.load(open(self.temp_data_path, 'rb'))
                self.logger.log_message(msg=f'I: Load temp data from {self.temp_data_path}, {len(self.temp_relcol_mapreq_bindersql)} records loaded.')
            except Exception as e:
                self.temp_relcol_mapreq_bindersql = {}
                self.logger.log_message(level='error', msg=f'E: Error raised in loading temp data: {e}')

    def _generate_related_cols_and_mapping_requirements(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, binder_vote_cnt=1, load_from_temp=True):
        #? Generate multiple binder_sql, then select the union for related_column, and update the mapping requirements
        #? Update rules: select the mapping requirements with shorter length.
        #* add function that allow to load temp data from disk
        if load_from_temp and data.id in self.temp_relcol_mapreq_bindersql:
            tar_dic = self.temp_relcol_mapreq_bindersql[data.id]
            self.logger.log_message(msg=f'/*************** Return temp data for {data.id} ***************/')
            return tar_dic['related_columns'], tar_dic['mapping_requirements'], tar_dic['binder_sqls']

        related_columns = []
        mapping_requirements = None
        sql_with_mp = None
        binder_sqls = []
        for _ in range(binder_vote_cnt):
            post_sql, rel_cols, map_requires = self.binder.process(data, instance_pool)
            if len(rel_cols) == 0:
                rel_cols = list(data.tbl.columns)

            binder_sqls.append(post_sql)
            related_columns = list(set(related_columns + rel_cols))

            if mapping_requirements is None:
                mapping_requirements = map_requires
                sql_with_mp = post_sql
            if len(map_requires) < len(mapping_requirements):
                mapping_requirements = map_requires
                sql_with_mp = post_sql
                
        if GEN_COL_FLAG:
            related_columns = self._update_related_cols(related_columns, mapping_requirements, sql_with_mp)

        return related_columns, mapping_requirements, binder_sqls

    def _get_coltype_dict(self, data:TQAData, related_columns:List[str], binder_sql:str, coltype_vote=3, instance_pool=None):
        coltype_dict = {}
        for _ in range(coltype_vote):
            try:
                colty_dic = self.coltype_deducer.process(data, related_columns, binder_sql, instance_pool)
            except:
                continue
            for col, ctype in colty_dic.items():
                if col not in coltype_dict:
                    coltype_dict[col] = []
                coltype_dict[col].append(ctype)
        for col in coltype_dict:
            coltype_dict[col] = max(coltype_dict[col], key=coltype_dict[col].count)
        return coltype_dict
    
    def _get_requires_with_direct_prompting(data: TQAData):
        pass

    
    def process_direct_prompting(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True):
        self.data = data
        self.log_info = {}
        self.self_corr_inses = []
        # 0. base_cleaning 
        self.data.tbl,_ = base_clean_dataframe(self.data.tbl, value_standardization=BASE_STAND)
        origin_cols = list(self.data.tbl.columns)

        # 1. direct prompting and get the requirements
        related_columns, aug_requires, nor_requires = self._get_requires_with_direct_prompting(data=data)

    def process(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True, binder_vote_cnt=1, coltype_vote=1):
        self.data = data
        self.log_info = {}
        self.self_corr_inses = []
        # 0. base_cleaning
        self.data.tbl,_ = base_clean_dataframe(self.data.tbl, value_standardization=BASE_STAND)
            
        origin_cols = list(self.data.tbl.columns)

        # 1. get the binder program: extract the [related columns] and the [mapping requirement(s)]
        related_columns, mapping_requirements, binder_sqls = self._generate_related_cols_and_mapping_requirements(data=data, instance_pool=instance_pool, GEN_COL_FLAG=GEN_COL_FLAG, binder_vote_cnt=binder_vote_cnt)
        related_columns = sorted([x for x in related_columns if x in origin_cols], key=lambda x: origin_cols.index(x))
        self.log_info['relcol_mapreq_bindersql'] = {'related_columns': related_columns, 'mapping_requirements': mapping_requirements, 'binder_sqls': binder_sqls}
        self.logger.log_message(msg=f'/*************** {self.log_info["relcol_mapreq_bindersql"]} ***************/')
        self.log_info['related_columns'] = related_columns

        # -- [G] update related_columns if some columns only exist in the mapping requirements
        # -- update log_info
        self.log_info['binder_sql'] = binder_sqls
        self.log_info['mapping_requirements'] = mapping_requirements

        self.log_info[f'col_gen'] = []
        # 2. [G] generate new columns
        if GEN_COL_FLAG: #!
            for requirement, cols in mapping_requirements:
                try:
                    op = None
                    # -> 2.1. [G] generate new column(s) based on the mapping requirement(s)
                    self.data, op = self.view_gen.generate_column_from_columns(self.data, cols, requirement, instance_pool)
                    # -> 2.2. [GI] impute the ungenerated value(s) of the GEN_NEW_COL operator
                    
                    if IMPUTATE_FLAG: #!
                        self.data = self.imputater.col_generate_imputate(self.data, op, binder_sqls[-1], instance_pool)
                    # -> 2.3. [G] update the related columns
                    new_col = op.args['new_column']
                    if new_col not in related_columns:
                        related_columns.append(new_col)
                    
                    # -- update log_info
                    self.log_info[f'col_gen'].append({'args': op.args, 'complete_func': op.complete_func_str})
                    self.log_info['related_columns'] = related_columns
                except Exception as e:
                    if op is not None:
                        src_cols = op.args['source_cols']
                        for col in src_cols:
                            if col not in related_columns:
                                related_columns.append(col)
                        related_columns = sorted(related_columns, key=lambda x: origin_cols.index(x))
                        self.log_info['related_columns'] = related_columns

                    self.logger.log_message(level='error', msg=f'E: Error raised in generating column: {e}')
                    continue
        
        self.log_info['clean'] = []
        
        if CLEAN_FLAG: #!
            # 3. [C] standardize the columns
            # -> 3.1. [C] deduce the types of all related columns
            coltype_dict = self._get_coltype_dict(self.data, related_columns, binder_sqls[-1], coltype_vote, instance_pool)

            # -- [C] update log_info
            self.log_info['coltype_dict'] = coltype_dict

            self.log_info['standardize'] = []
            origin_data = copy.deepcopy(self.data)
            for col, ctype in coltype_dict.items():
                if ctype in ['datetime', 'numerical']:
                    try:
                        # -> 3.2. [C] standardize the columns based on the deduced types
                        self.data, op = self.cleaner.standardize_coltype(self.data, col, ctype, instance_pool)
                        # -> 3.3. [CI] impute the unstandardized value(s)
                        if IMPUTATE_FLAG: #!
                            self.data = self.imputater.standardize_imputate(origin_data, self.data, col, ctype, sql=binder_sqls[-1], instance_pool=instance_pool)
                        # -- [C] update log_info
                        self.log_info['standardize'].append({'col': col, 'ctype': ctype})
                        if op.type != 'empty_operator':
                            self.log_info['clean'].append({'args': op.args, 'complete_func': op.complete_func_str})
                    except Exception as e:
                        self.logger.log_message(level='error', msg=f'E: Error raised in standardizing column: {e}')
                        continue


        self.log_info['related_columns'] = related_columns
        # 4. return the processed data
        if len(related_columns) != 0 and EXT_REL_COL:
            self.data.tbl = self.data.tbl[related_columns]

        self.self_corr_inses = self.binder.self_corr_inses + self.view_gen.self_corr_inses + self.imputater.self_corr_inses + self.coltype_deducer.self_corr_inses + self.cleaner.self_corr_inses
        self.icl_inses = self.binder.icl_inses + self.view_gen.icl_inses + self.imputater.icl_inses + self.coltype_deducer.icl_inses + self.cleaner.icl_inses

        return self.data, self.log_info

    def _update_related_cols(self, related_cols: List[str], mapping_requirements: List[Tuple[str, str]], sql:str):
        col_exists_cnt_map = {}

        for _, cols in mapping_requirements:
            for col in cols:
                if col not in col_exists_cnt_map:
                    col_exists_cnt_map[col] = 0
                col_exists_cnt_map[col] += 1

        for col in col_exists_cnt_map:
            # if the column only exists in the mapping requirements, then remove it from the related columns
            if col_exists_cnt_map[col] == sql.count(f'`{col}`'):
                if col in related_cols:
                    related_cols.remove(col)

        return related_cols
