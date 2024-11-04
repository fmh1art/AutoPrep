
import pandas as pd

def truncate_content(content, max_words=3):
    if isinstance(content, str):  # Check if content is a string
        words = content.split()
        if len(words) > max_words:
            return ' '.join(words[:max_words]) + '...'
        return content
    return str(content)  # Convert non-string types to string

def set_max_row_col(df, max_row=5, max_col=5):
    # set the maximum number of rows and columns to display
    # use ... to indicate that there are more rows and columns
    truncated_df = df.iloc[:max_row, :max_col]
    if len(df) > max_row:
        truncated_df = truncated_df.append(pd.Series(['...'] * len(truncated_df.columns), index=truncated_df.columns), ignore_index=True)
    if len(df.columns) > max_col:
        # add an additional column to indicate that there are more columns
        truncated_df['...'] = ['...'] * len(truncated_df)
    return truncated_df

def return_display_df(df):
    # Apply truncation to each cell
    truncated_data = df.applymap(truncate_content)
    truncated_data = set_max_row_col(truncated_data)
    return truncated_data