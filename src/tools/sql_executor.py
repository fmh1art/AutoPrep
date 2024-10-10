import sqlite3
import pandas as pd




class SQLExecutor:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = ':memory:'
        self.conn = sqlite3.connect(db_path)

    def execute(self, df:pd.DataFrame, sql:str):
        df.to_sql('w', self.conn, index=False, if_exists='replace')
        return pd.read_sql(sql, self.conn)
        
    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()