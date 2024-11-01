import copy, random
import pickle as pkl

from typing import List, Tuple
from src.tools.utils import *
import global_values as GV
from src.tools.logger import Logger
from src.data import TQAData
from src.model.mula_tabpro.agent import Binder, ViewGenerator, Imputater, ColTypeDeducer, Cleaner, Coder
from src.model.mula_tabpro.operator import FilterColumns, SimpleOperator

class LogicalOperator:
    def __init__(self, op_type=None):
        self.type = op_type

class Augment(LogicalOperator):
    def __init__(self, op_type='Augment', req:str="", rel_cols:List[str]=[]):
        super().__init__(op_type)
        self.req = req
        self.rel_cols = rel_cols
    
class Normalize(LogicalOperator):
    def __init__(self, op_type='Normalize', req:str="", col:str=''):
        super().__init__(op_type)
        self.req = req
        self.col = col

class Filter(LogicalOperator):
    def __init__(self, op_type='Filter', rel_cols:List[str]=[]):
        super().__init__(op_type)
        self.rel_cols = rel_cols


class MultiAgentDataPrep:
    def __init__(self, llm_name=GV.LLM_NAME, logger_root='tmp/table_llm_log', 
                 logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log', 
                 temp_data_path = GV.MULTIA_TEMP_DATA_PATH):
        self.llm_name = llm_name
        self.binder = Binder(llm_name=GV.LLM_DICT['binder'], logger_root=logger_root, logger_file=logger_file)
        self.view_gen = ViewGenerator(llm_name=GV.LLM_DICT['view_generator'], logger_root=logger_root, logger_file=logger_file)
        self.imputater = Imputater(llm_name=GV.LLM_DICT['imputater'], logger_root=logger_root, logger_file=logger_file)
        self.coltype_deducer = ColTypeDeducer(llm_name=GV.LLM_DICT['coltype_deducer'], logger_root=logger_root, logger_file=logger_file)
        self.cleaner = Cleaner(llm_name=GV.LLM_DICT['cleaner'], logger_root=logger_root, logger_file=logger_file)
        self.logger = Logger(name='MultiAgentDataPrep', root=logger_root, log_file=logger_file)
        self.coder = Coder(llm_name=GV.LLM_DICT['cleaner'], logger_root=logger_root, logger_file=logger_file)

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
    
    def process_process_table_with_code(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True, binder_vote_cnt=1, coltype_vote=1):
        self.data = data
        self.log_info = {}
        self.self_corr_inses = []
        # 0. base_cleaning
        self.data.tbl,_ = base_clean_dataframe(self.data.tbl)
            
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
                    old_df = copy.deepcopy(data.tbl) #!
                    col_str = ', '.join([f'`{col}`' for col in cols])
                    arg_req = f'Given the column {col_str} please generate a new column to answer "{requirement}"'
                    self.data = self.coder.process(self.data, arg_req, cols)
                    new_df = copy.deepcopy(data.tbl) #!
                    new_col_name = []
                    for col in new_df.columns: #!
                        if col not in old_df.columns:
                            new_col_name.append(col)

                    related_columns = related_columns + new_col_name

                except Exception as e:
                    self.logger.log_message(level='error', msg=f'E: Error raised in generating column: {e}')
                    # continue
                    
                self.log_info[f'col_gen'].append({'requirement': requirement, 'cols': cols, 'code': self.coder.code})
        
        self.log_info['clean'] = []
        
        if CLEAN_FLAG: #!
            # 3. [C] standardize the columns
            # -> 3.1. [C] deduce the types of all related columns
            coltype_dict = self._get_coltype_dict(self.data, related_columns, binder_sqls[-1], coltype_vote, instance_pool)

            # -- [C] update log_info
            self.log_info['coltype_dict'] = coltype_dict

            self.log_info['standardize'] = []
            for col, ctype in coltype_dict.items():
                if ctype in ['datetime', 'numerical']:
                    try:
                        old_df = copy.deepcopy(data.tbl) #!
                        arg_req = f'please standardize the column `{col}` to {ctype} format.'
                        self.data = self.coder.process(self.data, arg_req, [col])
                        new_df = copy.deepcopy(data.tbl) #!
                        new_col_name = []
                        for col in new_df.columns: #!
                            if col not in old_df.columns:
                                new_col_name.append(col)
                                
                        related_columns = related_columns + new_col_name

                    except Exception as e:
                        self.logger.log_message(level='error', msg=f'E: Error raised in standardizing column: {e}')
                        # continue
                    
                    self.log_info['standardize'].append({'col': col, 'ctype': ctype, 'code': self.coder.code})


        self.log_info['related_columns'] = related_columns
        # 4. return the processed data
        if len(related_columns) != 0 and GV.EXT_REL_COL:
            self.data.tbl = self.data.tbl[related_columns]

        return self.data, self.log_info
    
    def generate_logical_plan(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True, binder_vote_cnt=1, coltype_vote=1):
        logical_plan = []
        self.data = data
        self.log_info = {}
        print(GV.debug)
        # 0. base_cleaning
        self.data.tbl,_ = base_clean_dataframe(self.data.tbl)

        origin_cols = list(self.data.tbl.columns)

        # 1. get the binder program: extract the [related columns] and the [mapping requirement(s)]
        related_columns, mapping_requirements, binder_sqls = self._generate_related_cols_and_mapping_requirements(data=data, instance_pool=instance_pool, GEN_COL_FLAG=GEN_COL_FLAG, binder_vote_cnt=binder_vote_cnt)
        related_columns = sorted([x for x in related_columns if x in origin_cols], key=lambda x: origin_cols.index(x))
        
        for requirement, cols in mapping_requirements:
            logical_plan.append(Augment(req=requirement, rel_cols=list(cols)))

        coltype_dict = self._get_coltype_dict(self.data, related_columns, binder_sqls[-1], coltype_vote, instance_pool)
        for col, ctype in coltype_dict.items():
            if ctype in ['datetime', 'numerical']:
                logical_plan.append(Normalize(req=f'Cast to {ctype} type.', col=col))

        logical_plan.append(Filter(rel_cols=related_columns))
        
        return logical_plan, binder_sqls[-1]
    
    def execute_physical_plan(self, data:TQAData, physical_plan:List[SimpleOperator]):
        self.data = data

        # return {'new_column': new_column, 'func': func, 'source_cols': source_cols}, op_str
        col_map = {}
        for type, physic_op in physical_plan:
            old_op = copy.deepcopy(physic_op)
            if type == 'Augment':
                self.data, new_op = self.view_gen.execute_physical_op(self.data, physic_op.args['source_cols'], physic_op.req, physic_op)
                old_newcol = old_op.args['new_column']
                new_newcol = new_op.args['new_column']
                if old_newcol != new_newcol:
                    col_map[old_newcol] = new_newcol
            elif type == 'Normalize':
                self.data, new_op = self.cleaner.execute_physical_op(self.data, physic_op.args['column'], 'datetime' if physic_op.type==GV.NAMES['STAND_DATETIME'] else 'numerical', physic_op)
            elif type == 'Filter':
                rel_cols = physic_op.args['columns']
                if len(col_map) > 0:
                    rel_cols = [col_map[col] if col in col_map else col for col in rel_cols]
                    physic_op.complete_args_with_output(self.data, 'filter_columns(df, columns=[{}])'.format(', '.join([f'"{col}"' for col in rel_cols])))
                    physic_op.args['columns'] = rel_cols
                self.data = physic_op.execute(self.data)
            else:
                raise ValueError(f'Unknown physical operator: {type}')
        return self.data
                
    
    def generate_physical_plan(self, data:TQAData, logical_plan:List[LogicalOperator], binder_sql):
        self.data = data

        physical_plan = []

        # Find Filter Operator
        filter_op = None
        for logic_op in logical_plan:
            if isinstance(logic_op, Filter):
                filter_op = logic_op
                break

        new_gened_cols = []

        for logic_op in logical_plan:

                # generate physical operator for Augment
                if isinstance(logic_op, Augment):
                    try:
                        req = logic_op.req
                        cols = logic_op.rel_cols
                        physic_op = None
                        # self.data, physic_op = self.view_gen.generate_column_from_columns(self.data, cols, req)
                        physic_op = self.view_gen.get_physical_op(self.data, cols, req)
                        physic_op.req = req
                        physical_plan.append((logic_op.type, physic_op))
                        # self.data = self.imputater.col_generate_imputate(self.data, physic_op, binder_sql)
                        new_col = physic_op.args['new_column']
                        if new_col not in filter_op.rel_cols:
                            new_gened_cols.append(new_col)
                    except Exception as e:
                        self.logger.log_message(level='error', msg=f'E: Error raised in generating column: {e}')
                        continue
                # generate physical operator for Normalize
                elif isinstance(logic_op, Normalize):
                    try:
                        req = logic_op.req
                        col = logic_op.col
                        physic_op = None
                        ctype = 'datetime' if 'datetime' in req else 'numerical'
                        # self.data, physic_op = self.cleaner.standardize_coltype(self.data, col, ctype)
                        physic_op = self.cleaner.get_physical_op(self.data, col, ctype)
                        physical_plan.append((logic_op.type, physic_op))
                        # self.data = self.imputater.standardize_imputate(self.data, col, ctype, sql=binder_sql)
                    except Exception as e:
                        self.logger.log_message(level='error', msg=f'E: Error raised in standardizing column: {e}')
                        continue
                elif isinstance(logic_op, Filter):
                    pass
                else:
                    raise ValueError(f'Unknown logic_op: {logic_op.type}')

        # update LogicalOperator Filter
        if len(new_gened_cols) > 0:
            filter_op.rel_cols = filter_op.rel_cols + new_gened_cols

        filter_physical_op = FilterColumns()
        filter_physical_op.complete_args_with_output(self.data, 'filter_columns(df, columns=[{}])'.format(', '.join([f'"{col}"' for col in filter_op.rel_cols])))
        physical_plan.append(('Filter', filter_physical_op))

        return physical_plan
        

    def process(self, data:TQAData, instance_pool=None, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True, binder_vote_cnt=1, coltype_vote=1):
        self.data = data
        self.log_info = {}
        self.self_corr_inses = []
        # 0. base_cleaning
        self.data.tbl,_ = base_clean_dataframe(self.data.tbl)

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
        if len(related_columns) != 0 and GV.EXT_REL_COL:
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
