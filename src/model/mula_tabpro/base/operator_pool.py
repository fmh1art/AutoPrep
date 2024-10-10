import copy
from global_values import NAMES
import pandas as pd
from src.tools.utils import *

#! EXT_COL
def extract_column(df, columns=['column name 1', 'column name 3']):
    # make sure the columns are in the dataframe
    for col in columns:
        if col not in df.columns:
            raise ValueError(f'E(ext_col): {col} not in the dataframe')
    # return the columns extracted
    return df[columns]

#! REM_COL
def remove_column(df, columns=['column name 1', 'column name 3']):
    # make sure the columns are in the dataframe
    return df.drop(columns, axis=1)

#! EXT_ROW
def extract_row(df, condition=[{'column':'col1', 'target_value':'val1', 'operator':'<'}, {'column':'col2', 'target_value':'val2', 'operator':'='}], logical_relation='and'):
    base_df = copy.deepcopy(df)

    for cond in condition:
        column = cond['column']
        target_value = cond['target_value']
        operator = cond['operator']
        if operator == '=':
            operator = '=='

        # make sure the column is in the dataframe
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")
        
        # filter the dataframe based on the condition
        try:
            if logical_relation == 'and':
                df = eval(f'df[df[column] {operator} target_value]')
            elif logical_relation == 'or':
                cur_df = eval(f'base_df[base_df[column] {operator} target_value]')
                if len(df) == len(base_df):
                    df = pd.DataFrame()
                df = pd.concat([df, cur_df]).drop_duplicates()
        except Exception as e:
            raise ValueError(f"Error parsing 'df[df[column] {operator} target_value]'.\n{str(e)}")
        
    return df

#! EXT_MAX_CONS_RECORD
def extract_max_consecutive_record(df, column='result', target_value='win'):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not in DataFrame.")
    # Filter rows where the column matches the target_value
    filtered_df = df[df[column] == target_value]
    # If no matches are found, return an empty DataFrame
    if filtered_df.empty:
        return pd.DataFrame()
    # Calculate breaks in consecutive indices
    breaks = filtered_df.index.to_series().diff() > 1
    
    # Create groups for consecutive sequences and Group by the identified groups and get the group with the maximum size
    groups = breaks.cumsum()
    max_group_id = filtered_df.groupby(groups).size().idxmax()

    # Return the rows corresponding to the longest consecutive group
    return filtered_df[groups == max_group_id]

#! SORT_BY
def sort_by(df, column='score', ascending=False):
    # sort the dataframe based on the column
    return df.sort_values(by=column, ascending=ascending)

#! GROUP_STATISTICS
def group_statistics(df, group_by='col1', metrics={'col2': 'count'}):

    # the possible value of the metrics including 'count', 'sum', 'mean', 'median', 'min', 'max', 'std', 'var'
    for col, metric in metrics.items():
        # if metric is numerical operator while the column is not numerical, raise an error
        if metric in ['sum', 'mean', 'min', 'max', 'std', 'var'] and not my_float(df[col].iloc[0]):
            raise ValueError(f"Column '{col}' is not numerical, cannot apply '{metric}' operator.")

    # update the metrics dictionary to have the metrics as a list
    metrics_updated = {
        col: [metric] if isinstance(metric, str) else metric 
        for col, metric in metrics.items()
    }

    # create a dictionary to store the aggregation operations
    grouped = df.groupby(group_by).agg(metrics_updated)
    
    # flatten the column names
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    
    return grouped.reset_index()

#! GEN_NEW_COL
def generate_new_column(df, new_column='new_col', func=lambda x: x['col1'] + x['col2']):
    data_dic = df.to_dict(orient='records')
    new_col = []
    for dic in data_dic:
        try:
            new_col.append(func(dic))
        except Exception as e:
            new_col.append('[n.a.]')

    df[new_column] = new_col
    return df

def extract_column(df, new_column='new_col', func=lambda x: x['col1'] + x['col2']):
    return generate_new_column(df, new_column, func)

def calculate_column(df, new_column='new_col', func=lambda x: x['col1'] + x['col2']):
    return generate_new_column(df, new_column, func)

def boolean_column(df, new_column='new_col', func=lambda x: x['col1'] + x['col2']):
    return generate_new_column(df, new_column, func)

def combine_column(df, new_column='new_col', func=lambda x: x['col1'] + x['col2']):
    return generate_new_column(df, new_column, func)



#! GEN_CON_COL
def generate_conditional_column(df, new_column='new_col', condition=lambda x: x['col1'] > 10):
    # Apply the condition to each row and create a new Series with true_value or false_value
    new_series = df.apply(lambda x: 'Yes' if condition(x) else 'No', axis=1)
    # Assign the new Series to the dataframe as a new column
    df[new_column] = new_series
    return df

#! REMOVE_SYMBOL
def remove_noisy_symbol(df, column='date', symbol='$'):
    # make sure the column is in the dataframe
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not in DataFrame.")
    # remove the text from the column
    df[column] = df[column].str.replace(symbol, '')
    return df

#! STAND_DATETIME
def standardize_datetime(df, column='date', format='%Y-%m-%d'):
    # make sure the column is in the dataframe
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not in DataFrame.")
    return standardize_to_date(df, column, format)

#! STAND_NUMERICAL
def standardize_numerical(df, column='score', func=lambda x: x.replace('pt', '').strip()):
    # make sure the column is in the dataframe
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not in DataFrame.")
    for val in df[column]:
        try:
            new_val = func(str(val))
        except Exception as e:
            new_val = str(val) + "[n.a.]" if "[n.a.]" not in str(val) else str(val)
        
        df[column] = df[column].replace(val, new_val)
    return df

#! REMOVE_UNIT
def remove_unit(df, column='date', unit='cm'):
    # make sure the column is in the dataframe
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not in DataFrame.")
    # remove the text from the column and rename the column
    new_column = f"{column}_{unit}".replace(' ', '')
    df[new_column] = df[column].str.replace(unit, '').str.strip()
    # remove the original column
    df = df.drop(column, axis=1)
    return df

#! Other Code
OP_FUNC_STRING = {
    # EXT_COL
    'EXT_COL': """def extract_column(df, columns=['column name 1', 'column name 3']):
    return df[columns]""", 

    # EXT_ROW
    'EXT_ROW': """def extract_row(df, condition=[{'column':'col1', 'target_value':'val1', 'operator':'<'}, {'column':'col2', 'target_value':'val2', 'operator':'='}], logical_relation='and'):
    base_df = copy.deepcopy(df)
    
    for cond in condition:
        column = cond['column']
        target_value = cond['target_value']
        operator = cond['operator']

        # filter the dataframe based on the condition
        if logical_relation == 'and':
            df = eval(f'df[df[column] {operator} target_value]')
        elif logical_relation == 'or':
            cur_df = eval(f'base_df[base_df[column] {operator} target_value]')
            if len(df) == len(base_df):
                df = pd.DataFrame()
            df = pd.concat([df, cur_df]).drop_duplicates()

    return df""", 

    # EXT_MAX_CONS_RECORD
    'EXT_MAX_CONS_RECORD': """def extract_max_consecutive_record(df, column='result', target_value='win'):
    # Filter rows where the column matches the target_value
    filtered_df = df[df[column] == target_value]
    # Calculate breaks in consecutive indices
    breaks = filtered_df.index.to_series().diff() > 1
    # Create groups for consecutive sequences and Group by the identified groups and get the group with the maximum size
    groups = breaks.cumsum()
    max_group_id = filtered_df.groupby(groups).size().idxmax()

    # Return the rows corresponding to the longest consecutive group
    return filtered_df[groups == max_group_id]""",


    # SORT_BY
    'SORT_BY': """def sort_by(df, column='score', ascending=False):
    # sort the dataframe based on the column
    return df.sort_values(by=column, ascending=ascending)""",

    # GROUP_STATISTICS
    'GROUP_STATISTICS': """def group_statistics(df, group_by='col1', metrics={'col2': 'count'}):

    # update the metrics dictionary to have the metrics as a list
    metrics_updated = {
        col: [metric] if isinstance(metric, str) else metric 
        for col, metric in metrics.items()
    }

    # create a dictionary to store the aggregation operations
    grouped = df.groupby(group_by).agg(metrics_updated)
    
    # flatten the column names
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    
    return grouped.reset_index()""",

    # GEN_NEW_COL
    'GEN_NEW_COL': """def generate_new_column(df, new_column='new_col', operation=lambda x: x['col1'] + x['col2']):
    # Apply the operation to each row and create a new Series
    new_series = df.apply(operation, axis=1)
    # Assign the new Series to the dataframe as a new column
    df[new_column] = new_series
    return df""",

    # GEN_CON_COL
    'GEN_CON_COL': """def generate_conditional_column(df, new_column='new_col', condition=lambda x: x['col1'] > 10):
    # Apply the condition to each row and create a new Series with true_value or false_value
    new_series = df.apply(lambda x: 'Yes' if condition(x) else 'No', axis=1)
    # Assign the new Series to the dataframe as a new column
    df[new_column] = new_series
    return df""",
}

ARG_REQUIRED_DICT = {
    NAMES['EXT_COL']: ['columns'],
    NAMES['EXT_ROW']: ['condition', 'logical_relation'],

    NAMES['EXT_MAX_CONS_RECORD']: ['column', 'target_value'],
    NAMES['SORT_BY']: ['column', 'ascending'],
    NAMES['GROUP_STATISTICS']: ['group_by', 'metrics'],

    NAMES['GEN_NEW_COL']: ['new_column', 'func', 'source_cols'],
    NAMES['EXT_COL']: ['new_column', 'func', 'source_cols'],
    NAMES['CAL_COL']: ['new_column', 'func', 'source_cols'],
    NAMES['BOOL_COL']: ['new_column', 'func', 'source_cols'],
    NAMES['COMB_COL']: ['new_column', 'func', 'source_cols'],

    NAMES['INF_COL']: ['new_column', 'func'],

    NAMES['REMOVE_SYMBOL']: ['column', 'symbol'],
    NAMES['STAND_DATETIME']: ['column', 'format'],
    NAMES['REMOVE_UNIT']: ['column', 'unit'],
    NAMES['STAND_NUMERICAL']: ['column', 'func'],
}