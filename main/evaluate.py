from src.tools.utils import open_json, save_json, df_to_cotable

def evaluate_result(VERSION, analyze=False, data_dic=None):
    from src.tools.binder_utils.evaluator import Evaluator

    binder_eval = Evaluator()

    result_path = f'./tmp/outputs/result_v{VERSION}.json'
    reses = open_json(result_path)
    eval_results = {}
    err_ids = []

    analyze_text = ''
    for id in reses:

        rec = reses[id]
        chain_len = 0
        if chain_len not in eval_results:
            eval_results[chain_len] = {'hit': 0, 'tol': 0, 'acc': 0}
        eval_results[chain_len]['tol'] += 1

        label = rec['label']
        pred = rec['answer']
        sql = rec['sql']
        if type(pred) == list:
            pred = '|'.join([str(p) for p in pred])
        
        # print(label, pred)
        # if wikit_if_hit(pred, label):
        if binder_eval.evaluate(
            pred.split('|') if type(pred) == str else pred,
            label.split('|') if type(label) == str else label,
            'wikitq',
            allow_semantic=True,
            question=rec['question']):

            eval_results[chain_len]['hit'] += 1
        else:
            err_ids.append(id)
            if analyze:
                table = rec['table'] if data_dic is None else df_to_cotable(data_dic[id].tbl)
                analyze_text += '\n'.join([f"【Table】\n{table}", f"【Question】: {rec['question']}", f"【Label】: {label}", f"【Prediction】: {pred}", f"【SQL】\n{sql}", f"【Reason】:", '', ''])
            pass

    if analyze:
        with open(f'./tmp/outputs/analyze_v{VERSION}.txt', 'w', encoding='utf-8') as f:
            f.write(analyze_text)

    for chain_len in range(max(eval_results.keys())+1):
        if chain_len not in eval_results:
            continue

        acc = eval_results[chain_len]['hit'] / eval_results[chain_len]['tol']
        eval_results[chain_len]['acc'] = acc

    print(VERSION, eval_results, sep='\t\t\t')
    save_json(eval_results, f'./tmp/outputs/eval_results_v{VERSION}.json')
