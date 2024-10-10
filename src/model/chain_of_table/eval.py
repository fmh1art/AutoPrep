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


import fire
import os
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

from utils.load_data import load_tabfact_dataset,load_wikiqa_dataset
from utils.llm import ChatGPT
from utils.helper import *
from utils.evaluate import *
from utils.chain import *
from operations import *


def main(
    dataset_path: str = "/Users/annebrian/Desktop/lab/chain-of-table-main/wiki_qa/test_seen.csv",
    raw2clean_path: str ="/Users/annebrian/Desktop/lab/chain-of-table-main/wiki_qa/",
    model_name: str = "gpt-3.5-turbo-16k-0613",
    result_dir: str = "results/wikiqa",
    openai_api_key: str = "sk-V4OtuKqQFM6VsNSHE2203e99Cd764830B35d11Cf86B3Db27",
    first_n=-1,
    n_proc=1,
    chunk_size=1,
):
    gpt_llm = ChatGPT(
        model_name=model_name,
        key=os.environ["OPENAI_API_KEY"] if openai_api_key is None else openai_api_key,
        base_url = os.environ["OPENAI_BASE_URL"]
    )
    os.makedirs(result_dir, exist_ok=True)

    folder_path = '/Users/annebrian/Desktop/lab/chain-of-table-main/results/wikiqa/cache'
    file_list = os.listdir(folder_path)
    proc_samples = []
    dynamic_chain_log_list = {}
    for idx,file_name in enumerate(file_list):
        full_file_path = os.path.join(folder_path, file_name)
        with open(full_file_path,"r") as f:
            data = json.load(f)
        sample,proc_sample,log = data
        # proc_samples[idx] = proc_sample
        proc_samples.append(proc_sample)
        dynamic_chain_log_list[idx] = log
        # if idx > 0:
        #     break
    fixed_chain = [
        (
            "simpleQuery_fewshot",
            simple_query,
            dict(use_demo=True),
            dict(
                temperature=0, per_example_max_decode_steps=200, per_example_top_p=1.0
            ),
        ),
    ]
    final_result, _ = fixed_chain_exec_mp(gpt_llm, proc_samples, fixed_chain)
    acc = tabfact_match_func_for_samples(final_result)
    print("Accuracy:", acc)

    print(
        f'Accuracy: {acc}',
        file=open(os.path.join(result_dir, "result.txt"), "w")
    )
    save_result = []
    for item in final_result:
        entry = {}
        entry[item["id"]] = {
            "table": item["table_text"],
            "label": item["label"],
            "question": item["statement"],
            "answer": item["chain"][-1]["parameter_and_conf"][0][0],
            "chain" : item["chain"]
        }
        save_result.append(entry)
    
    # pickle.dump(
    #     final_result, open(os.path.join(result_dir, "final_result.pkl"), "wb")
    # )
    # pickle.dump(
    #     dynamic_chain_log_list, 
    #     open(os.path.join(result_dir, "dynamic_chain_log_list.pkl"), "wb")
    # )


    json.dump(
        save_result, open(os.path.join(result_dir, "final_result_test.json"), "w")
    )
    json.dump(
        dynamic_chain_log_list, 
        open(os.path.join(result_dir, "dynamic_chain_log_list.json"), "w")
    )


if __name__ == "__main__":
    fire.Fire(main)
