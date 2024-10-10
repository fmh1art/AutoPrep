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


import re
import numpy as np
import copy
from utils.helper import table2string


group_column_demo ="""To answer the question, we can first use f_group_by() to group the values in a column.
/*
col : Rank | Lane | Athlete | Time | Country
row 1 : 1 | 6 | Manjeet Kaur (IND) | 52.17 | IND
row 2 : 2 | 5 | Olga Tereshkova (KAZ) | 51.86 | KAZ
row 3 : 3 | 4 | Pinki Pramanik (IND) | 53.06 | IND
row 4 : 4 | 1 | Tang Xiaoyin (CHN) | 53.66 | CHN
row 5 : 5 | 8 | Marina Maslyonko (KAZ) | 53.99 | KAZ
*/
Question: tell me the number of athletes from japan.
The existing columns are: Rank, Lane, Athlete, Time, Country.
Explanation: The question asks about the number of athletes from India. Each row is about
an athlete. We can group column "Country" to group the athletes from the same country.
Therefore, the answer is: f_group_by(Country)."""


def group_column_build_prompt(table_text, statement, table_caption=None, num_rows=100):
    table_str = table2string(
        table_text, caption=table_caption, num_rows=num_rows
    ).strip()
    prompt = "/*\n" + table_str + "\n*/\n"
    prompt += "Question: " + statement + "\n"
    prompt += "The existing columns are: "
    prompt += ", ".join(table_text[0]) + ".\n"
    prompt += "Explanation:"
    return prompt


def group_column_func(
    sample, table_info, llm, llm_options=None, debug=False, skip_op=[]
):
    table_text = table_info["table_text"]

    table_caption = sample["table_caption"]
    statement = sample["statement"]
    prompt = "" + group_column_demo.rstrip() + "\n\n"
    prompt += group_column_build_prompt(
        table_text, statement, table_caption=table_caption, num_rows=5
    )
    responses = llm.generate_plus_with_score(
        prompt,
        options=llm_options,
    )

    if debug:
        print(prompt)
        print(responses)

    group_param_and_conf = {}
    group_column_and_conf = {}

    headers = table_text[0]
    rows = table_text[1:]
    for res, score in responses:
        re_result = re.findall(r"f_group\(([^\)]*)\)", res, re.S)

        if debug:
            print("Re result: ", re_result)

        try:
            group_column = re_result[0].strip()
            assert group_column in headers
        except:
            continue

        if group_column not in group_column_and_conf:
            group_column_and_conf[group_column] = 0
        group_column_and_conf[group_column] += np.exp(score)

    for group_column, conf in group_column_and_conf.items():
        group_column_contents = []
        index = headers.index(group_column)
        for row in rows:
            group_column_contents.append(row[index])

        def check_if_group(vs):
            vs_without_empty = [v for v in vs if v.strip()]
            return len(set(vs_without_empty)) / len(vs_without_empty) <= 0.8

        if not check_if_group(group_column_contents):
            continue

        vs_to_group = []
        for i in range(len(group_column_contents)):
            vs_to_group.append((group_column_contents[i], i))

        group_info = []
        for v in sorted(set(group_column_contents)):
            group_info.append((v, group_column_contents.count(v)))
        group_info = sorted(group_info, key=lambda x: x[1], reverse=True)

        group_key = str((group_column, group_info))
        group_param_and_conf[group_key] = conf

    group_param_and_conf_list = sorted(
        group_param_and_conf.items(), key=lambda x: x[1], reverse=True
    )

    operation = {
        "operation_name": "group_column",
        "parameter_and_conf": group_param_and_conf_list,
    }

    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    return sample_copy


def group_column_act(table_info, operation, strategy="top", skip_op=[]):
    table_info = copy.deepcopy(table_info)

    failure_table_info = copy.deepcopy(table_info)
    failure_table_info["act_chain"].append("skip f_group_column()")

    if "group_column" in skip_op:
        return failure_table_info
    if len(operation["parameter_and_conf"]) == 0:
        return failure_table_info
    if strategy == "top":
        group_column, group_info = eval(operation["parameter_and_conf"][0][0])
    else:
        raise NotImplementedError()

    table_info["group_sub_table"] = (group_column, group_info)
    table_info["act_chain"].append(f"f_group_column({group_column})")

    return table_info
