import pandas as pd

from src.data import TQAData
import global_values as GV

from .funcs import cal_tokens

def df_to_cotable(df: pd.DataFrame, cut_line = GV.DEFAULT_ROW_CUT):
        ret = ""
        col_str = ' | '.join(df.columns) + '\n'
        ret += col_str
        ret += '|'.join(['---' for _ in range(len(df.columns))]) + '\n'
        for i in range(len(df)):
            if cut_line!=-1 and i > cut_line-1:
                ret += '......\n'
                break
            # row_str = ' | '.join([str(x) for x in df.iloc[i].values]) + '\n'
            row_str = ' | '.join([str(x) for x in df.iloc[i].values]) + '\n'
            ret += row_str

        return ret.strip()

def df_to_cotable_add_quo(df: pd.DataFrame, cut_line = GV.DEFAULT_ROW_CUT):
        ret = ""
        col_str = ' | '.join(df.columns) + '\n'
        ret += col_str
        ret += '|'.join(['---' for _ in range(len(df.columns))]) + '\n'
        for i in range(len(df)):
            if cut_line!=-1 and i > cut_line-1:
                ret += '......\n'
                break
            row_str = ' | '.join([f'"{str(x)}"' if type(x) == str else str(x) for x in df.iloc[i].values]) + '\n'
            ret += row_str

        return ret.strip()
        

def df_to_json_dict(data:dict):
    ret = ''
    ret += '{\n'
    for k, v in data.items():
        ret += f'\t{k}: {v},\n'
    ret += '}'
    return ret

def df_to_str_columns_add_quo(df: pd.DataFrame, cut_line = GV.DEFAULT_ROW_CUT, exclude_cols = [], col_type = None):
    ret = ""
    if col_type is not None:
        ret += 'Columns: ' + ', '.join([f'"{col}"({col_type[col]})' if col in col_type else f'"{col}"(string)'
                                        for col in df.columns if col not in exclude_cols]) + '\n\n'
    for col in df.columns:
        if col in exclude_cols:
            continue
        # cut
        if cut_line!=-1 and len(df) > cut_line:
            values = df[col].values[:cut_line]
        else:
            values = df[col].values
        ret += f'"{col}": ' + ' | '.join([f'{str(x)}' if type(x) != str else f'"{str(x)}"' for x in values]) + '\n'
    return ret.strip()

def df_to_str_columns(df: pd.DataFrame, cut_line = GV.DEFAULT_ROW_CUT, exclude_cols = [], col_type = None):
    ret = ""
    if col_type is not None:
        ret += 'Columns: ' + ', '.join([f'"{col}"({col_type[col]})' if col in col_type else f'"{col}"(string)'
                                        for col in df.columns if col not in exclude_cols]) + '\n\n'
    for col in df.columns:
        if col in exclude_cols:
            continue
        # cut
        if cut_line!=-1 and len(df) > cut_line:
            values = df[col].values[:cut_line]
        else:
            values = df[col].values
        ret += f'"{col}": ' + ' | '.join([f'{str(x)}' for x in values]) + '\n'
    return ret.strip()

def df_to_cotable_old(df: pd.DataFrame, cut_line = GV.DEFAULT_ROW_CUT, row_flag='row'):
    ret = ""
    col_str = f'col : ' + ' | '.join(df.columns) + '\n'
    ret += col_str
    for i in range(len(df)):
        if cut_line!=-1 and i > cut_line-1:
            ret += '......\n'
            break
        row_str = row_flag + str(i + 1) + ' : ' + ' | '.join([str(x) for x in df.iloc[i].values]) + '\n'
        ret += row_str

    return ret.strip()
    

def cut_cottable_prompt(prompt, max_tok = 4096):
    lines = prompt.split('\n')
    last_beg, last_end = -1, -1
    for i, line in enumerate(lines):
        if line.strip() == '/*':
            last_beg = i
        if line.strip() == '*/':
            last_end = i
    assert last_beg != -1 and last_end != -1 and last_beg < last_end

    cur_tok = cal_tokens(prompt)
    need_to_space = cur_tok - max_tok
    mid_index = (last_beg + last_end) // 2
    for del_line_cnt in range(1, mid_index - last_beg):
        del_lines = lines[mid_index-del_line_cnt:mid_index+del_line_cnt]
        del_tok = cal_tokens('\n'.join(del_lines))
        if del_tok >= need_to_space:
            break
    
    del_idx_beg = mid_index - del_line_cnt
    del_idx_end = mid_index + del_line_cnt
    new_prompt = '\n'.join(lines[:del_idx_beg] + ['......'] + lines[del_idx_end+1:])
    return new_prompt


def add_row_number_to_df(df: pd.DataFrame, col_name='row_id'):
    if col_name in df.columns:
        df = df.drop(columns=[col_name])
    df.insert(0, col_name, range(1, len(df)+1)) 
    return df

def _float_is_int(df: pd.DataFrame, col):
    tol = 0
    is_int = 0
    for val in df[col]:
        try:
            int(val)
            if '.' in str(val):
                return False
            is_int += 1
        except:
            tol += 1
    return float(is_int) / (tol+1e-6) > GV.TYPE_DEDUCE_RATIO

def ansketch_nl2sql_prompt(data:TQAData, cut_line=GV.DEFAULT_ROW_CUT, specify_line=False):

    col_and_type = []
    for col in data.tbl.columns:
        # A. if col is in col_type
        if col in data.col_type:
            type = data.col_type[col]
            # (1). string --> text
            if type == 'string':
                type = 'text'
            # (2). numerical --> int/float
            elif type == 'numerical':
                if _float_is_int(data.tbl, col):
                    type = 'int'
                    for val in data.tbl[col]:
                        # covert to int
                        try:
                            new_val = int(val)
                            data.tbl[col] = data.tbl[col].replace(val, new_val)
                        except:
                            pass
                else:
                    type = 'float'
                    for val in data.tbl[col]:
                        # covert to float
                        try:
                            new_val = float(val)
                            data.tbl[col] = data.tbl[col].replace(val, new_val)
                        except:
                            pass

            # (3). datetime --> datetime
            elif type == 'datetime':
                type = 'text'
            # (4). others --> text
            else:
                type = 'text'
        # B. if col is not in col_type
        else:
            type = 'text'

        col_and_type.append(f'\t{col} {type}')

    col_and_type_str = '\n'.join(col_and_type)
    create_table = f"CREATE TABLE w(\n{col_and_type_str}\n)"

    table_ret = ''
    # column name
    col_str = '\t'.join(data.tbl.columns) + '\n'
    table_ret += col_str
    # each row
    for i in range(len(data.tbl)):
        if cut_line!=-1 and i > cut_line-1:
            if not specify_line:
                table_ret += '......\n'
            break
        row_str = '\t'.join([str(x) for x in data.tbl.iloc[i].values]) + '\n'
        table_ret += row_str
    table_ret = table_ret.strip()

    return create_table, table_ret