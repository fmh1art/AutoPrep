import sys, random
from joblib import Parallel, delayed
from global_values import *

from src.tools.binder_utils.evaluator import Evaluator

from src.model.mula_tabpro import *
from src.dataset import TQADataset, TFVDataset
import pickle as pkl
from src.model.mula_tabpro.base import *
from src.tools.utils import *
from mula_dp import MultiAgentDataPrep
from src.tools.binder_utils.evaluator import Evaluator
import threading
from src.model.mula_tabpro.others.instance_pool import InstancePool

class Experiment:
    def __init__(self, mulprocess_cnt, llm_name, VERSION=TABLELLM_VERSION):
        self.mulprocess_cnt = mulprocess_cnt
        self.llm_name = llm_name
        self.VERSION = VERSION

        if not os.path.exists(rf'.\tmp\outputs'):
            os.makedirs(rf'.\tmp\outputs')
        if not os.path.exists(rf'.\tmp\outputs\analyze'):
            os.makedirs(rf'.\tmp\outputs\analyze')
        if not os.path.exists(rf'.\tmp\table_llm_log'):
            os.makedirs(rf'.\tmp\table_llm_log')

    def run_multi_agents_data_prep(self, sample_num):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_data_prep'
        print(f'BASE_VERSION: {BASE_VERSION}')
        datas = self.load_datas(sample_num)
        print(f'len(datas): {len(datas)}')
        processed_datas = self.multi_agents_data_prep(datas, save=True, BASE_VERSION=BASE_VERSION)
        self.nl2sql_baseline(processed_datas, save=True, BASE_VERSION=BASE_VERSION + '_run_nl2sql')
        self.evaluate_result(BASE_VERSION + '_run_nl2sql', analyze=True)

    def run_nl2sql_baseline(self, sample_num):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_baseline_nl2sqler'
        print(f'BASE_VERSION: {BASE_VERSION}')
        datas = self.load_datas(sample_num)
        print(f'len(datas): {len(datas)}')
        self.nl2sql_baseline(datas, save=True, BASE_VERSION=BASE_VERSION)
        self.evaluate_result(BASE_VERSION, analyze=True)
    
    def _get_original_tbl_size(self):
        if TASK_TYPE == 'tableqa':
            ds = pkl.load(open(rf'.\tmp\wiki_qa.pkl', 'rb'))
            datas = ds.test_unseen_data
        else:
            if not os.path.exists(rf'.\tmp\tablefact_-1.pkl'):
                ds = TFVDataset(dataset_name='tabfact')
                ds.load_data()
                datas = ds.test_data
                pkl.dump(datas, open(rf'.\tmp\tablefact_-1.pkl', 'wb'))
            else:
                datas = pkl.load(open(rf'.\tmp\tablefact_-1.pkl', 'rb'))

        
        tbl_size_dic = {}
        for d in datas:
            df_str = df_to_cotable(d.tbl, cut_line=-1)
            tok_size = cal_tokens(df_str)
            tbl_size_dic[d.id] = tok_size
        
        return tbl_size_dic

    def evaluate_result(self, VERSION, analyze=True, data_dic=None, allow_semantic=True):
        binder_eval = Evaluator()
        result_path = f'./tmp/outputs/result_v{VERSION}.json'
        reses = open_json(result_path)
        eval_results = {}
        err_ids = []
        hit_dic = {}
        analyze_text = ''
        for id in tqdm.tqdm(reses):

            rec = reses[id]
            chain_len = 0
            if chain_len not in eval_results:
                eval_results[chain_len] = {'hit': 0, 'tol': 0, 'acc': 0}
            eval_results[chain_len]['tol'] += 1

            label = rec['label']
            pred = rec['answer']
            if type(pred) == list:
                pred = '|'.join([str(p) for p in pred])
            
            if binder_eval.evaluate(
                pred.split('|') if type(pred) == str else pred,
                label.split('|') if type(label) == str else label,
                'wikitq' if TASK_TYPE == 'tableqa' else 'tab_fact',
                allow_semantic=allow_semantic,
                question=rec['question']):

                eval_results[chain_len]['hit'] += 1
                hit_dic[id] = True
                # print(f'【{id}】: Correct, label: {label}, pred: {pred}')
            else:
                # print(f'【{id}】: Wrong!!, label: {label}, pred: {pred}')
                err_ids.append(id)
                hit_dic[id] = False

                if analyze:
                    sql = rec['sql'] if 'sql' in rec else 'N/A'
                    table = rec['table'] if data_dic is None else df_to_cotable(data_dic[id].tbl)
                    analyze_text += '\n'.join([f"【Table】\n{table}", f"【Question】: {rec['question']}", f"【Label】: {label}", f"【Prediction】: {pred}", f"【SQL】\n{sql}", f"【Reason】:", '', ''])
                pass

        if analyze:
            if not os.path.exists('./tmp/outputs/analyze'):
                os.makedirs('./tmp/outputs/analyze')
            with open(f'./tmp/outputs/analyze/analyze_v{VERSION}.txt', 'w', encoding='utf-8') as f:
                f.write(analyze_text)

        for chain_len in range(max(eval_results.keys())+1):
            if chain_len not in eval_results:
                continue

            acc = eval_results[chain_len]['hit'] / eval_results[chain_len]['tol']
            eval_results[chain_len]['acc'] = acc

        print(VERSION, eval_results, sep='\t\t\t')
        save_json(eval_results, f'./tmp/outputs/eval_results_v{VERSION}.json')
        return hit_dic
    
    def load_datas(self, sample_num=-1, split=SPLIT):

        if TASK_TYPE == 'tableqa':
            if not os.path.exists(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl'):
                ds = pkl.load(open(rf'.\tmp\wiki_qa.pkl', 'rb'))
                # datas = ds.test_unseen_data
                datas = ds.train_data if split == 'train' else ds.test_unseen_data
                if sample_num != -1 and sample_num < len(datas):
                    datas = random.sample(datas, sample_num)
                # save as pkl
                pkl.dump(datas, open(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl', 'wb'))
            else:
                # read pkl
                print(f'load data from pkl')
                datas = pkl.load(open(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl', 'rb'))

        if TASK_TYPE == 'tablefact':
            if not os.path.exists(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl'):
                ds = TFVDataset(dataset_name='tabfact')
                # ds.load_data()
                ds.load_data_org() if split == 'train' else ds.load_data()
                datas = ds.train_data if split == 'train' else ds.test_data
                if sample_num != -1 and sample_num < len(datas):
                    datas = random.sample(datas, sample_num)
                # save as pkl
                pkl.dump(datas, open(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl', 'wb'))
            else:
                # read pkl
                print(f'load data from pkl')
                datas = pkl.load(open(rf'.\tmp\{TASK_TYPE}_{split}_{sample_num}.pkl', 'rb'))
        
        print(f'Total data: {len(datas)}')
        return datas

    def _nl2sql_one_data(self, data, llm_name, VERSION, instance_pool=None):
        nl2sqler = NL2SQLer(llm_name=llm_name, logger_file=f'mula_tabpro_v{VERSION}.log')

        try:
            sql, pro_tbl = nl2sqler.process(data=data, instance_pool=instance_pool)
            answer = extract_answers(pro_tbl)
        except Exception as e:
            sql = nl2sqler.sql
            answer = nl2sqler.ans
        
        self_corr_inses = nl2sqler.self_corr_inses
        icl_inses = nl2sqler.icl_inses

        return data.id, sql, answer, self_corr_inses, icl_inses

    def nl2sql_baseline(self, datas, save=True, BASE_VERSION=TABLELLM_VERSION):
        json_result = {}
        
        if os.path.exists(f'./tmp/outputs/result_v{BASE_VERSION}.json'):
            json_result = open_json(f'./tmp/outputs/result_v{BASE_VERSION}.json')
            print(len(json_result))
        
        logger = Logger(name='EXPERIMENT', log_file=f'mula_tabpro_v{BASE_VERSION}.log', root='tmp/table_llm_log')

        data_dic = {data.id: data for data in datas}

        instance_pool = InstancePool(pool_name=BASE_VERSION.replace('_run_nl2sql', ''), load_from=None)

        for i in tqdm.tqdm(range(0, len(datas), SAVE_STEP)):

            results = Parallel(n_jobs=self.mulprocess_cnt, require='sharedmem')(
                delayed(self._nl2sql_one_data)(data, self.llm_name, BASE_VERSION) for data in datas[i:i+SAVE_STEP]\
                    if data.id not in json_result
            )

            for res in results:
                id, sql, answer, self_corr_inses, icl_inses = res
                data = data_dic[id]

                # for ins in self_corr_inses:
                #     instance_pool.add_instance(ins)
                # for ins in icl_inses:
                #     instance_pool.add_instance(ins)
                
                json_result[id] = {
                    'table': df_to_cotable(data.tbl, cut_line=-1),
                    'question': data.question,
                    'label': data.label,
                    'sql': sql,
                    'answer': answer
                }

                logger.log_message(msg=f'******************** #num: {len(json_result)}, id: {id}, label: {data.label}, answer: {answer} ********************')

                if save:
                    save_json(json_result, f'./tmp/outputs/result_v{BASE_VERSION}.json')
                    
                # if len(instance_pool.instances) > 0:
                #     instance_pool.save_pool()

        return json_result

    def _prepare_one_data(self, data, llm_name, VERSION, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True, instance_pool=None):
        """The code for preparing one data with multi-agents.

        Args:
            data (TQAData): the data to be processed.
            llm_name (str): the name of the language model.
            VERSION (str): the version of the experiment.
            GEN_COL_FLAG (bool, optional): whether use Generator or not. Defaults to True.
            CLEAN_FLAG (bool, optional): whether use Cleaner or not. Defaults to True.
            IMPUTATE_FLAG (bool, optional): whether use Imputator or not. Defaults to True.

        Returns:
            processed_data (TQAData): the processed data.
            log_info (dict): the log information.
            #!the third arg: self-correction instances
        """
        process_id = threading.get_ident()
        original_data = copy.deepcopy(data)
        mdp = MultiAgentDataPrep(llm_name=llm_name, logger_file=f'process{process_id}.log', logger_root=f'tmp/table_llm_log/mula_tabpro_v{VERSION}')
        try:
            if OP_INSTEAD_OF_CODE:
                processed_data, log_info = mdp.process(data, instance_pool=instance_pool, GEN_COL_FLAG=GEN_COL_FLAG, CLEAN_FLAG=CLEAN_FLAG, IMPUTATE_FLAG=IMPUTATE_FLAG)
            else:
                processed_data, log_info = mdp.process_process_table_with_code(data, instance_pool=instance_pool, GEN_COL_FLAG=GEN_COL_FLAG, CLEAN_FLAG=CLEAN_FLAG, IMPUTATE_FLAG=IMPUTATE_FLAG)

            mdp.logger.log_message(msg = f'******************** id: {data.id}, question: {data.question} ********************')
            mdp.logger.log_message(msg = f'【Original Table】\n{original_data.tbl}')
            mdp.logger.log_message(msg = f'【Processed Table】\n{processed_data.tbl}')
        except Exception as e:
            mdp.logger.log_message(msg = f'!!!!!!!!!!!!!!!!!!!Error for {data.id}!!!!!!!!!!!!!!!!!: {e}')
            processed_data = mdp.data
            log_info = mdp.log_info
            if 'related_columns' in log_info:
                rel_cols = log_info['related_columns']
                processed_data.tbl = processed_data.tbl[rel_cols]

        self_corr_inses = mdp.self_corr_inses
        icl_inses = mdp.icl_inses

        return processed_data, log_info, self_corr_inses, icl_inses

    def multi_agents_data_prep(self, datas, save=True, BASE_VERSION=TABLELLM_VERSION, GEN_COL_FLAG=True, CLEAN_FLAG=True, IMPUTATE_FLAG=True):
        processed_datas = []
        log_infos = {}
        mul_dp_temp_data = {}

        logger = Logger(name='EXPERIMENT', log_file=f'mula_tabpro_v{BASE_VERSION}.log', root=f'tmp/table_llm_log/mula_tabpro_v{BASE_VERSION}')
        if os.path.exists(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_processed_data.pkl'):
            with open(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_processed_data.pkl', 'rb') as f:
                processed_datas = pkl.load(f)
            logger.log_message(msg=f'processed_datas: {len(processed_datas)}')
            
        if os.path.exists(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_log_infos.json'):
            log_infos = open_json(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_log_infos.json')
            logger.log_message(msg=f'log_infos: {len(log_infos)}')

        if os.path.exists(MULTIA_TEMP_DATA_PATH):
            with open(MULTIA_TEMP_DATA_PATH, 'rb') as f:
                mul_dp_temp_data = pkl.load(f)

        instance_pool = InstancePool(pool_name=BASE_VERSION)

        # save results every $SAVE_STEP datas
        for i in tqdm.tqdm(range(0, len(datas), SAVE_STEP)):
            results = Parallel(n_jobs=self.mulprocess_cnt, require='sharedmem')(
                delayed(self._prepare_one_data)(data, self.llm_name, BASE_VERSION, GEN_COL_FLAG, CLEAN_FLAG, IMPUTATE_FLAG, instance_pool) for data in datas[i:i+SAVE_STEP]\
                    if data.id not in log_infos and data.id not in [d.id for d in processed_datas]
            )

            for res in results:
                if res is None:
                    continue
                processed_data, log_info, self_corr_inses, icl_inses = res
                processed_datas.append(processed_data)
                log_infos[processed_data.id] = log_info

                # for ins in self_corr_inses:
                #     instance_pool.add_instance(ins)
                # for ins in icl_inses:
                #     instance_pool.add_instance(ins)

                logger.log_message(msg=f'******************** #num: {len(processed_datas)}, id: {processed_data.id}, question: {processed_data.question}, len(self_corr_inses): {len(self_corr_inses)} ********************')

                if save:
                    if 'relcol_mapreq_bindersql' in log_info:
                        binder_result_dic = log_info['relcol_mapreq_bindersql']
                        log_info.pop('relcol_mapreq_bindersql')
                        if processed_data.id not in mul_dp_temp_data:
                            mul_dp_temp_data[processed_data.id] = binder_result_dic
                            with open(MULTIA_TEMP_DATA_PATH, 'wb') as f:
                                pkl.dump(mul_dp_temp_data, f)
                    # Save as pkl
                    with open(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_processed_data.pkl', 'wb') as f:
                        pkl.dump(processed_datas, f)
                    # Save as json
                    save_json(log_infos, rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_log_infos.json')

                    # if len(instance_pool.instances) > 0:
                    #     instance_pool.save_pool()

        return processed_datas
    
if __name__ == '__main__':
    exp = Experiment(mulprocess_cnt=50, llm_name=LLM_DICT['nl2sqler'])

    exp.run_multi_agents_data_prep(sample_num=100)
