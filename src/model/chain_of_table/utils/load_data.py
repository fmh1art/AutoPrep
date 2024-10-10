# Copyright 2024 The Chain-of-Table authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
from tqdm import tqdm

def load_tabfact_dataset(
    dataset_path,
    raw2clean_path,
    tag="test",
    first_n=-1,
):
    tabfact_statement_raw2clean_dict = {}
    with open(raw2clean_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            info = json.loads(line)
            tabfact_statement_raw2clean_dict[info["statement"]] = info["cleaned_statement"]

    dataset = []
    if first_n != -1:
        all_lines = []
        for line in open(dataset_path):
            all_lines.append(line)
            if len(all_lines) >= first_n: break
    else:
        all_lines = open(dataset_path).readlines()
    for i, line in tqdm(enumerate(all_lines), total=len(all_lines), desc=f"Loading tabfact-{tag} dataset"):
        info = json.loads(line)
        info["id"] = f"{tag}-{i}"
        info["chain"] = []
        if info["statement"] in tabfact_statement_raw2clean_dict:
            info["cleaned_statement"] = tabfact_statement_raw2clean_dict[
                info["statement"]
            ]
        else:
            info["cleaned_statement"] = info["statement"]
        dataset.append(info)
    return dataset


def wrap_input_for_demo(statement, table_caption, table_text, cleaned_statement=None):
    return {
        "statement": statement,
        "table_caption": table_caption,
        "table_text": table_text,
        "cleaned_statement": cleaned_statement if cleaned_statement is not None else statement,
        "chain": [],
    }


import pandas as pd
import os
import csv

def load_wikiqa_dataset(file_path_list,table_csv_path,first_n,id_file_path = None):
    if id_file_path is None:
        data_ids = None
    else:
        # id_file_path = '/Users/annebrian/Desktop/lab/chain-of-table-main/result_v2.1.0.json'
        with open(id_file_path, 'r') as file:
            data = json.load(file)
        data_ids =list(data.keys())
    question_info = []

    for file_path in file_path_list:
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            if data_ids is not None and row["id"] not in data_ids: #["ns-325","ns-1889","ns-3122","nu-179","nu-2026","nu-2280","nu-2382","nu-2483","nu-2928"]:
                continue
            entry = {
                'id': row['id'],
                'statement': row['question'],
                'cleaned_statement': row['question'],
                'table': row['table'],
                'label': row['answer']
            }
            question_info.append(entry)
    dataset = []
    if first_n != -1:
        question_info = question_info[:first_n]
    for i,entry in enumerate(question_info):
        table_path = os.path.join(table_csv_path,entry["table"])
        print(table_path)
        # table_path=table_path.replace(".csv",".table")
        # markdown_table=''''''
        # with open(table_path,encoding="utf-8") as f:
        #     markdown_table=f.read()
        with open(table_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data_list = list(reader)

        # df = pd.DataFrame(data[1:], columns=data[0])
        # data_list = [df.columns.tolist()] + df.values.tolist()
        new_entry = entry
        new_entry["table_text"] = data_list
        new_entry["table_caption"] = None  
        new_entry["chain"] = []      
        dataset.append(new_entry)
    return dataset



