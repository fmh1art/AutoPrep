
import os, time
import json
import subprocess

import pandas as pd
import tiktoken, tqdm

from src.data import TQAData
from global_values import DATASETS
import multiprocessing
from multiprocessing import Lock
import pickle

lock = Lock()

def delete_content_between(s, start, end):
    start_idx = s.find(start)
    end_idx = s.find(end)
    if start_idx == -1 or end_idx == -1:
        return s
    return s[:start_idx] + s[end_idx:]

def save_pickle(file_name, data):
    with lock:
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

def load_pickle(file_name, retry=40, sleep_time=0.1):
    with lock:
        for _ in range(retry):
            if os.path.getsize(file_name) > 0:
                with open(file_name, 'rb') as f:
                    data = pickle.load(f)
                return data
            else:
                time.sleep(sleep_time)
                continue
        raise ValueError(f"Failed to load {file_name}")

def rename_file(root, include_str, replace_to):
    # rename files in root directory
    # replace include_str to replace_to
    for path, subdirs, files in os.walk(root):
        for name in files:
            if include_str in name:
                new_name = name.replace(include_str, replace_to)
                os.rename(os.path.join(path, name), os.path.join(path, new_name))

def update_TData_col_type(data:TQAData, col_type:dict):
    for col in col_type:
        t = col_type[col]
        if t != 'string':
            data.col_type[col] = t
    return data


def serialize_table(df:pd.DataFrame):
    return df.to_markdown(index=False,)


def run_python(code_for_processing: str):
    try:
        result = subprocess.run(
            ["python", "-c", code_for_processing],
            capture_output=True, text=True
        )
        if result.stderr:
            return f"Error occurred: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"An error occurred: {str(e)}"


def load_jsonl(path):
    data = []
    with open(path, 'r') as f:
        lines = f.readlines()
    for line in tqdm(lines):
        d = json.loads(line)
        data.append(d)
    return data

def save_jsonl(path, datas):
    if os.path.exists(path):
        print(f'Path: {path} already exists! Please delete it!')
        return
    
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    print(f'saving jsonl object to {path}...')
    with open(path, 'a') as f:
        for d in tqdm(datas):
            f.write(json.dumps(d) + '\n')


def auto_dataset(dataset_name):
    tgt_task = None
    for task in DATASETS:
        if dataset_name in DATASETS[task]:
            tgt_task = task
            break
    
    if tgt_task is None:
        raise ValueError(f"Dataset {dataset_name} not found in any task")
    
    if tgt_task == 'SCM':
        from src.dataset.SCMDataset import SCMDataset
        return SCMDataset(dataset_name)
    elif tgt_task == 'CTA':
        from src.dataset.CTADataset import CTADataset
        return CTADataset(dataset_name)
    elif tgt_task == 'DI':
        from src.dataset.DIDataset import DIDataset
        return DIDataset(dataset_name)
    elif tgt_task == 'ED':
        from src.dataset.EDDataset import EDDataset
        return EDDataset(dataset_name)
    elif tgt_task == 'EM':
        from src.dataset.EMDataset import EMDataset
        return EMDataset(dataset_name)
    else:
        raise ValueError(f"Task {tgt_task} not found")


def cal_f1(preds, labs):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for pred, lab in zip(preds, labs):
        if pred == 1 and lab == 1:
            tp += 1
        elif pred == 1 and lab == 0:
            fp += 1
        elif pred == 0 and lab == 1:
            fn += 1
        elif pred == 0 and lab == 0:
            tn += 1
    if tp == 0:
        return 0, fp, fn, tp, tn, 0, 0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    # print(f'fp: {fp}, fn: {fn}, tp: {tp}, precision: {precision:.3f}, recall: {recall:.3f}, f1: {f1:.3f}')
    return f1, fp, fn, tp, tn, precision, recall

def cal_tokens(s):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    codelist = encoding.encode(s)
    return len(codelist)

def open_json(path):
    with open(path, "r", encoding='ISO-8859-1') as f:
        data = json.load(f)
    return data

def save_json(a, fn):
    dir_path = os.path.dirname(fn)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    b = json.dumps(a)
    f2 = open(fn, 'w')
    f2.write(b)
    f2.close()

def execute_code_from_string(code_string, df, glo = globals(), loc = locals()):
    try:
        loc['df'] = df
        exec(code_string, glo, loc)
        return locals()['df']
    except Exception as e:
        raise ValueError(f"Error executing code: {e}")

def load_tsv(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(line.strip().split('\t'))
    tsv = {}
    for i in range(len(data[0])):
        tsv[data[0][i]] = [data[j][i] for j in range(1,len(data))]
        
    return tsv

def all_filepaths_in_dir(root, endswith=None):
    file_paths = []
    for subdir, dirs, files in os.walk(root):
        for file in files:
            if endswith is None or file.endswith(endswith):
                file_paths.append(os.path.join(subdir, file))
    return file_paths
