import sys, random
from joblib import Parallel, delayed
sys.path.append(r'E:\fmh\MulA_Tabpro')
from global_values import *

from src.tools.binder_utils.evaluator import Evaluator

from src.model.mula_tabpro import *
from src.dataset import TQADataset, TFVDataset
import pickle as pkl
from src.model.mula_tabpro.base import *
from src.tools.utils import *
from mula_dp import MultiAgentDataPrep
from main import run_puresql, evaluate_result
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
        # processed_datas = self._load_processed_data(BASE_VERSION, datas)
        self.nl2sql_baseline(processed_datas, save=True, BASE_VERSION=BASE_VERSION + '_run_nl2sql')
        self.evaluate_result(BASE_VERSION + '_run_nl2sql', analyze=True)

    def run_nl2sql_baseline(self, sample_num):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_baseline_nl2sqler'
        print(f'BASE_VERSION: {BASE_VERSION}')
        datas = self.load_datas(sample_num)
        print(f'len(datas): {len(datas)}')
        self.nl2sql_baseline(datas, save=True, BASE_VERSION=BASE_VERSION)
        self.evaluate_result(BASE_VERSION, analyze=True)

    def run_end2end_baseline(self, sample_num, fewshot=True, cot=False):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_baseline_{a}_{b}end2ender'.format(a='fewshot-' if fewshot else '', b='cot-' if cot else '')
        print(f'BASE_VERSION: {BASE_VERSION}')
        datas = self.load_datas(sample_num)
        print(f'len(datas): {len(datas)}')
        self.end2end_baseline(datas, save=True, BASE_VERSION=BASE_VERSION, fewshot=fewshot, cot=cot)
        self.evaluate_result(BASE_VERSION, analyze=True, allow_semantic=False)

    def run_end2end_data_prep(self, sample_num, fewshot=True, cot=False):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_data_prep_{a}_{b}end2ender'.format(a='fewshot-' if fewshot else '', b='cot-' if cot else '')
        print(f'BASE_VERSION: {BASE_VERSION}')
        processed_datas = pkl.load(open(rf'E:\fmh\MulA_Tabpro\tmp\outputs\mula_tabpro_v3.1.22-{TASK_TYPE}-deepseek-chat-False-LEVEN_RATION_-1_ablation_study_G_C_I_processed_data.pkl', 'rb'))
        print(f'len(processed_datas): {len(processed_datas)}')
        self.end2end_baseline(processed_datas, save=True, BASE_VERSION=BASE_VERSION + '_run_end2ender', fewshot=fewshot, cot=cot)
        self.evaluate_result(BASE_VERSION + '_run_end2ender', analyze=True, allow_semantic=False)
    
    def run_ablation_study(self, sample_num, exps=None):
        BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_ablation_study'
        print(f'BASE_VERSION: {BASE_VERSION}')
        datas = self.load_datas(sample_num)
        print(f'len(datas): {len(datas)}')
        for G, C, I in [
            (True, True, True),
            (False, False, False), 
            (True, False, False), (False, True, False), 
            (False, True, True), 
            (True, False, True), (True, True, False), 
        ] if exps is None else exps:
            BASE_VERSION=TABLELLM_VERSION+f'_{sample_num}' + '_ablation_study'
            if G:
                BASE_VERSION += '_G'
            if C:
                BASE_VERSION += '_C'
            if I:
                BASE_VERSION += '_I'
            if EXT_REL_COL:
                BASE_VERSION += '_T'
            # if not BASE_STAND:
            #     BASE_VERSION += '_NotBaseStand'
            if not G and not C and not I:
                BASE_VERSION += '_baseline'
            print(f'BASE_VERSION: {BASE_VERSION}')
            processed_datas = self.multi_agents_data_prep(datas, save=True, BASE_VERSION=BASE_VERSION, GEN_COL_FLAG=G, CLEAN_FLAG=C, IMPUTATE_FLAG=I)
            self.nl2sql_baseline(processed_datas, save=True, BASE_VERSION=BASE_VERSION + '_run_nl2sql')
            self.evaluate_result(BASE_VERSION + '_run_nl2sql', analyze=True)
    
    def analyze_pair_wise_results(self, VERSION_A, VERSION_B):
        reses_A = open_json(f'./tmp/outputs/result_v{VERSION_A}.json')
        reses_B = open_json(f'./tmp/outputs/result_v{VERSION_B}.json')
        analyze_text = ''
        task_type = 'wikitq' if 'tableqa' in VERSION_A else 'tab_fact'
        if task_type == 'wikitq':
            datas = pkl.load(open(rf'.\tmp\{TASK_TYPE}_test_-1.pkl', 'rb'))
        else:
            datas = pkl.load(open(rf'.\tmp\tablefact_-1.pkl', 'rb'))
        data_dict = {data.id: data for data in datas}
        binder_eval = Evaluator()
        for id in reses_A:
            rec_A = reses_A[id]
            rec_B = reses_B[id]
            label = rec_A['label']
            pred_A = rec_A['answer']
            pred_B = rec_B['answer']
            if type(pred_A) == list:
                pred_A = '|'.join([str(p) for p in pred_A])
            if type(pred_B) == list:
                pred_B = '|'.join([str(p) for p in pred_B])
            # if both correct, continue
            correct_A = binder_eval.evaluate(
                pred_A.split('|') if type(pred_A) == str else pred_A,
                label.split('|') if type(label) == str else label,
                task_type,
                allow_semantic=True,
                question=rec_A['question'])
            correct_B = binder_eval.evaluate(
                pred_B.split('|') if type(pred_B) == str else pred_B,
                label.split('|') if type(label) == str else label,
                task_type,
                allow_semantic=True,
                question=rec_B['question'])

            flag = 'ERROR'
            if correct_A and correct_B:
                continue
            if not correct_A:
                flag += f'_A【{VERSION_A}】'
            if not correct_B:
                flag += f'_B【{VERSION_B}】'

            analyze_text += '\n'.join([f"************************************ 【{id}】: {flag} ************************************", '#!【NOTE】: ', '', 
                                       f"【Original Table】:\n{df_to_cotable_add_quo(data_dict[id].tbl)}",
                                       f"【Question】: {rec_A['question']}",  f"【Label】: {label}", 
                                       '',
                                       f"【Table A】\n{rec_A['table']}", f"【Prediction_A】: {pred_A}", 
                                       '',
                                       f"【Table B】\n{rec_B['table']}", f"【Prediction_B】: {pred_B}", 
                                       '', ''])
            
        with open(f'./tmp/outputs/analyze/analyze_pairwise_{VERSION_A}_{VERSION_B}.txt', 'w', encoding='utf-8') as f:
            f.write(analyze_text)

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

    def evaluate_result(self, VERSION, analyze=True, data_dic=None, allow_semantic=True, based_on_tbl_size=False):
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

        if based_on_tbl_size:
            tbl_size_dic = self._get_original_tbl_size()
            tbl_acc = {
                'small': {'hit': 0, 'tol': 0}, # < 2048
                'medium': {'hit': 0, 'tol': 0}, # 2048 - 4096
                'large': {'hit': 0, 'tol': 0} # > 4096
            }
            for id in hit_dic:
                tok = tbl_size_dic[id]
                if tok < 2048:
                    tbl_acc['small']['tol'] += 1
                    if hit_dic[id]:
                        tbl_acc['small']['hit'] += 1
                elif tok < 4096:
                    tbl_acc['medium']['tol'] += 1
                    if hit_dic[id]:
                        tbl_acc['medium']['hit'] += 1
                else:
                    tbl_acc['large']['tol'] += 1
                    if hit_dic[id]:
                        tbl_acc['large']['hit'] += 1
            for size in tbl_acc:
                acc = tbl_acc[size]['hit'] / (tbl_acc[size]['tol']+0.00001)
                tbl_acc[size]['acc'] = acc

            tbl_acc['total_acc'] = sum([tbl_acc[size]['hit'] for size in tbl_acc]) / sum([tbl_acc[size]['tol'] for size in tbl_acc])
            save_json(tbl_acc, f'./tmp/outputs/analyze/analyze_v{VERSION}_tbl_size_acc.json')

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

    def _load_processed_data(self, BASE_VERSION, datas):
        if not os.path.exists(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_processed_data.pkl'):
            processed_datas = self.multi_agents_data_prep(datas, save=True, BASE_VERSION=BASE_VERSION)
        else:
            processed_datas = pkl.load(open(rf'.\tmp\outputs\mula_tabpro_v{BASE_VERSION}_processed_data.pkl', 'rb'))
        return processed_datas

    def _end2end_one_data(self, data, llm_name, VERSION, fewshot, cot=False):
        if cot:
            end2ender = CoTEnd2Ender(llm_name=llm_name, logger_file=f'mula_tabpro_v{VERSION}.log')
        else:
            end2ender = End2Ender(llm_name=llm_name, logger_file=f'mula_tabpro_v{VERSION}.log')

        try:
            answer = end2ender.process(data=data, fewshot=fewshot)
        except Exception as e:
            answer = end2ender.ans
        
        return data.id, answer

    def end2end_baseline(self, datas, save=True, BASE_VERSION=TABLELLM_VERSION, fewshot=True, cot=False):
        json_result = {}
        
        if os.path.exists(f'./tmp/outputs/result_v{BASE_VERSION}.json'):
            json_result = open_json(f'./tmp/outputs/result_v{BASE_VERSION}.json')
            print(len(json_result))
        
        logger = Logger(name='EXPERIMENT', log_file=f'mula_tabpro_v{BASE_VERSION}.log', root='tmp/table_llm_log')

        data_dic = {data.id: data for data in datas}

        for i in range(0, len(datas), SAVE_STEP):

            results = Parallel(n_jobs=self.mulprocess_cnt, require='sharedmem')(
                delayed(self._end2end_one_data)(data, self.llm_name, BASE_VERSION, fewshot, cot) for data in datas[i:i+SAVE_STEP]\
                    if data.id not in json_result
            )

            for res in results:
                if res is None:
                    continue
                id, answer = res
                data = data_dic[id]
                
                json_result[id] = {
                    'table': df_to_cotable(data.tbl, cut_line=-1),
                    'question': data.question,
                    'label': data.label,
                    'answer': answer
                }

                logger.log_message(msg=f'******************** #num: {len(json_result)}, id: {id}, label: {data.label}, answer: {answer} ********************')

                if save:
                    save_json(json_result, f'./tmp/outputs/result_v{BASE_VERSION}.json')

        return json_result

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

        instance_pool = InstancePool(pool_name=BASE_VERSION.replace('_run_nl2sql', ''), load_from=INS_LOAD_FROM)

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
            processed_data, log_info = mdp.process(data, instance_pool=instance_pool, GEN_COL_FLAG=GEN_COL_FLAG, CLEAN_FLAG=CLEAN_FLAG, IMPUTATE_FLAG=IMPUTATE_FLAG)
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

        instance_pool = InstancePool(pool_name=BASE_VERSION, load_from=INS_LOAD_FROM)

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
    
    def delete_wrong_instances(self):
        if os.path.exists(f'./tmp/outputs/hit_dic-{TASK_TYPE}.json'):
            hit_dic = open_json(f'./tmp/outputs/hit_dic-{TASK_TYPE}.json')
        else:
            hit_dic = self.evaluate_result(VERSION='3.8-tablefact-deepseek-chat-selfc0-retd0-LEVEN-RetDFirst_1000_ablation_study_G_C_I_T_run_nl2sql')
            save_json(hit_dic, f'./tmp/outputs/hit_dic-{TASK_TYPE}.json')
        instance_pool = InstancePool(pool_name=f'instance_from_train-{TASK_TYPE}')
        instance_pool.remove_instance_by_ids([id for id in hit_dic if not hit_dic[id]])
        instance_pool.save_pool(f'./tmp/instances/correct_instances-{TASK_TYPE}')

if __name__ == '__main__':
    exp = Experiment(mulprocess_cnt=200, llm_name=LLM_DICT['nl2sqler'])
    exp.run_end2end_baseline(sample_num=-1, fewshot=True, cot=False)

    # exp.run_ablation_study(sample_num=-1, exps=[(True, True, True)])

    # files = all_filepaths_in_dir(fr'D:\0th-D\MulA_Tabpro\tmp\outputs')
    # for file in files:
    #     file_name = os.path.basename(file)
    #     if 'result_v' in file_name and TASK_TYPE in file_name:
    #         EXT_VERSION = file_name.replace('result_v', '').replace('.json', '')
    #         if os.path.exists(f'./tmp/outputs/analyze/analyze_v{EXT_VERSION}_tbl_size_acc.json'):
    #             data = open_json(f'./tmp/outputs/analyze/analyze_v{EXT_VERSION}_tbl_size_acc.json')
    #             if not 'end2ender' in EXT_VERSION and 'total_acc' in data and 'acc' in data['small']:
    #                 print(f'EXT_VERSION: {EXT_VERSION}, total_acc: {data["total_acc"]}, small_acc: {data["small"]["acc"]}, medium_acc: {data["medium"]["acc"]}, large_acc: {data["large"]["acc"]}')
    #                 continue

    #         exp.evaluate_result(EXT_VERSION, based_on_tbl_size=True, allow_semantic=False if 'end2ender' in EXT_VERSION else True)

    # exp.run_end2end_baseline(sample_num=-1, fewshot=False)

    # exp.run_nl2sql_baseline(sample_num=500)
    # exp.run_multi_agents_data_prep(sample_num=-1)
    # exp.run_ablation_study(sample_num=200, exps=[(True, True, True)])
    # exp.analyze_pair_wise_results(
    #     VERSION_A='3.1.20-tableqa-deepseek-chat-False-LEVEN_RATION_-1_ablation_study_G_C_I_run_nl2sql', 
    #     VERSION_B='3.1.20-tableqa-deepseek-chat-False-LEVEN_RATION_-1_ablation_study_C_I_run_nl2sql', 
    # )

    # BASE_VERSION = TABLELLM_VERSION+f'_{-1}' + '_data_prep'

    # processed_datas = pkl.load(open(rf'E:\fmh\MulA_Tabpro\tmp\history\____v3.1.5_complete_perf_on_wikit_tabfact\wikitq\outputs\mula_tabpro_v3.1.1-tableqa-deepseek-chat_-1_data_prep_processed_data.pkl', 'rb'))
    # print(f'len(processed_datas): {len(processed_datas)}')
    # exp.nl2sql_baseline(processed_datas, save=True, BASE_VERSION=BASE_VERSION + '_run_nl2sql_on-deepseek-process-data')
    # exp.evaluate_result(BASE_VERSION + '_run_nl2sql_on-deepseek-process-data', analyze=True)