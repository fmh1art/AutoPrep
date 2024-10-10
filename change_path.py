import os
import re

"""
fmh_win11: the personal pc of fmh
500_pc: the pc of fmh in 500 lab
"""

# src = 'fmh_win11'
# tar = '500_pc'

src = '500_pc'
tar = 'fmh_win11'

var_dict = {
    'fmh_win11': {
        'root1': 'D:\\\\0th-D\\\\MulA_Tabpro',
        'root2': 'D:\\0th-D\\MulA_Tabpro',
        'data_path': rf'D:\0th-D\Firefly\RAG_LLM_DM\data',
    },
    '500_pc': {
        'root1': 'E:\\\\fmh\\\\MulA_Tabpro',
        'root2': 'E:\\fmh\\MulA_Tabpro',
        'data_path': rf'E:\fmh\data',
    },
    'frx_pc': {
        'root1': 'E:\\\\fmh\\\\MulA_Tabpro',
        'root2': 'E:\\fmh\\MulA_Tabpro',
    },
    'cjy_pc': {
        
    }
}

def replace_data_path(folder_path):
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            if file == 'change_path.py':
                continue
            if file.endswith('.py') or file.endswith('.ipynb'):
                if file == 'evaluate.ipynb':
                    print()
                    pass
                file_path = os.path.join(subdir, file)
                modified = False  
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    if var_dict[src]['root1'] in line:
                        lines[i] = lines[i].replace(var_dict[src]['root1'], var_dict[tar]['root1'])
                        modified = True
                    if var_dict[src]['root2'] in line:
                        lines[i] = lines[i].replace(var_dict[src]['root2'], var_dict[tar]['root2'])
                        modified = True
                    if 'DATA_PATH = ' in line:
                        lines[i] = lines[i].replace(var_dict[src]['data_path'], var_dict[tar]['data_path'])
                        modified = True
                
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f'Modified: {file_path}')

# make a file named 'keys.txt' in the folder_path, with content 'XXX-XXX'
def make_key_file(folder_path):
    with open(os.path.join(folder_path, 'keys.txt'), 'w') as f:
        f.write('sk-0SLCV1lrjTsw7M57A06e0759C1Fc414e990a21E7853b051a')

replace_data_path(var_dict[tar]['root2'])
# make_key_file(folder_path)
