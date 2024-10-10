import os

from src.model.mula_tabpro.agent import NL2SQLer
from global_values import TABLELLM_VERSION
from src.tools.utils import open_json, save_json, df_to_cotable, extract_answers

def run_puresql(datas, llm_name, max_run=9999, VERSION=TABLELLM_VERSION):

    nl2sqler = NL2SQLer(llm_name=llm_name, logger_file=f'mula_tabpro_v{VERSION}.log')
    json_result = {}
    if os.path.exists(f'./tmp/outputs/result_v{VERSION}.json'):
        json_result = open_json(f'./tmp/outputs/result_v{VERSION}.json')
        print(len(json_result))
    err_inses = {}
    if os.path.exists(f'./tmp/outputs/err_inses_v{VERSION}.json'):
        err_inses = open_json(f'./tmp/outputs/err_inses_v{VERSION}.json')

    for data in datas:
        if len(json_result) >= max_run:
            break

        id = data.id
        if id in json_result:
            print(f'id: {id} already processed, skip...')
            continue
        try:
            sql, pro_tbl = nl2sqler.process(data=data)
            answer = extract_answers(pro_tbl)
        except Exception as e:
            err_inses[id] = str(e)
            save_json(err_inses, f'./tmp/outputs/err_inses_v{VERSION}.json')

            sql = nl2sqler.sql
            answer = nl2sqler.ans
            nl2sqler.logger.log_message(msg = f'!!!!!!!!!!!!!!!!!!!Error for {data.id}!!!!!!!!!!!!!!!!!: {e}')

        json_result[id] = {}

        json_result[id]['table'] = df_to_cotable(data.tbl, cut_line=-1)
        json_result[id]['question'] = data.question
        json_result[id]['label'] = data.label
        json_result[id]['sql'] = sql
        json_result[id]['answer'] = answer

        nl2sqler.logger.log_message(msg = f'********************id: {id}, label: {data.label}, answer: {answer}********************')

        save_json(json_result, f'./tmp/outputs/result_v{VERSION}.json')