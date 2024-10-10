from .BaseData import *
from .TQAData import TQAData

class TFVData(TQAData):
    def __init__(self, dataset_name:str, tbl:pd.DataFrame, 
                 question:str, label:str, task_type:str='TFV', id='NO_ID',caption = ""):
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.question = question
        self.label = label
        self.task_type = task_type
        self.id = id
        self.caption = caption
        self.title = caption
        self.col_type = {}

    def eval_prediction(self, predicted):
        """Evaluate the prediction is correct or not.
        Args:
            predicted (dict): an example is {'0': "type", '1': "name"}. !! the value is not a list
        Returns:
            bool: True/Flase, represent whether the prediction is totally correct or not.
        """
        pass

    def _smaple_table(self, table:pd.DataFrame, sample_num):
        sample_num = sample_num if sample_num < len(table) else len(table)
        emp_num = table.isnull().sum(axis=1)
        weight = (1-emp_num/len(table.columns))
        return table.sample(sample_num, weights=weight).reset_index(drop=True)
