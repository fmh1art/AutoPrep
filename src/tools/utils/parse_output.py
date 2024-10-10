
import re

import pandas as pd

from global_values import ord_pref, TASK_TYPE

def get_py_function_name(rsp):
    func_name = re.findall(r'def (.*?)\(', rsp)[0]
    return func_name

# def parse_code(rsp):
#     pattern = r"```python(.*)```"
#     match = re.search(pattern, rsp, re.DOTALL)
#     code_text = match.group(1) if match else rsp
#     return code_text

def parse_code(rsp):
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, rsp, re.DOTALL)
    code_text = matches[0] if matches else ""
    return code_text

def parse_any_string(rsp, code_type=None, hard_replace=None):
    if hard_replace != None:
        rsp = rsp.replace(hard_replace, '')
    if code_type != None:
        rsp = rsp.replace('```'+code_type, '```')
    pattern = r"```(.*?)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    if rsp.count('```') < 2:
        return rsp
    if code_text.strip().startswith('python'):
        code_text = code_text.replace('python', '', 1).strip()
    if code_text.strip().startswith('SQL'):
        code_text = code_text.replace('SQL', '', 1).strip()
    if code_text.strip().startswith('sql'):
        code_text = code_text.replace('sql', '', 1).strip()
    if code_text.strip().startswith('neuralsql'):
        code_text = code_text.replace('neuralsql', '', 1).strip()
    if code_text.strip().startswith('NeuralSQL'):
        code_text = code_text.replace('NeuralSQL', '', 1).strip()
    if code_text.strip().startswith('neural_sql'):
        code_text = code_text.replace('neural_sql', '', 1).strip()
    return code_text

def parse_coltype_dict(s:str):
    # find the first '{' and the last '}'
    beg = s.find('{')
    end = s.rfind('}')
    if beg == -1 or end == -1:
        return {}
    s = s[beg:end+1]
    return eval(s)

def get_ord_prefix(num):
    if num in ord_pref:
        return ord_pref[num]
    else:
        last_number = num % 10
        return ord_pref[last_number]


def modify_tabfact_answer(ret):
    modi_ret = ret
    
    if len(ret)==0:
        modi_ret = [0]
    elif len(ret)==1:
        val = ret[0]
        if val == 'None' or val == '' or val == 'none' or val == None:
            modi_ret = [0]
        else:
            if str(val) != '0' and str(val) != '1':
                modi_ret = [1]
    else:
        modi_ret = [1]
    
    return modi_ret


def extract_answers(sub_table: pd.DataFrame):
    if 'row_id' in sub_table.columns:
        ret = sub_table.iloc[:, 1:].values.flatten().tolist()
    else:
        ret = sub_table.values.flatten().tolist()
    
    if TASK_TYPE == 'tablefact':
        ret = modify_tabfact_answer(ret)

    return ret


def parse_one_arg(func_str:str, arg_name:str, df=None):
    # str = 'func_name(df, arg_name = 2)'
    func_str = func_str.replace(f'{arg_name} ', f'{arg_name}').replace(f'{arg_name}= ', f'{arg_name}=')
    # str = 'func_name(df,arg_name=2)'
    arg_val = re.findall(f'{arg_name}=(.*?)\)', func_str)[0].strip()
    return eval(arg_val)

def parse_two_args(func_str:str, arg1_name:str, arg2_name:str, df=None):
    # str = 'func_name(df, arg1_name = 2, arg2_name = 3)'
    func_str = func_str.replace(f'{arg1_name} ', f'{arg1_name}').replace(f'{arg1_name}= ', f'{arg1_name}=')
    func_str = func_str.replace(f' {arg2_name}', f'{arg2_name}').replace(f'{arg2_name} ', f'{arg2_name}').replace(f'{arg2_name}= ', f'{arg2_name}=')
    # str = 'func_name(df, arg1_name=2,arg2_name=3)'
    arg1_val = re.findall(f'{arg1_name}=(.*?),{arg2_name}', func_str)[0].strip()
    # arg2_val is from '{arg2_name}=' to the rightest ')'
    arg2_val = func_str[func_str.find(f'{arg2_name}=')+len(f'{arg2_name}='):func_str.rfind(')')].strip()
    if not arg1_val.startswith('lambda'):
        arg1_val = eval(arg1_val)
    if not arg2_val.startswith('lambda'):
        arg2_val = eval(arg2_val)
    return arg1_val, arg2_val
