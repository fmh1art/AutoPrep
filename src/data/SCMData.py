from .BaseData import *

class SCMTable(BaseData):
    def __init__(self, dataset_name:str, src_tbl:pd.DataFrame, tgt_tbl:pd.DataFrame,
                 col_mappings:List[tuple], scm_type:str, labels:List=None, task_type:str='scm'):
        super(SCMTable, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.src_tbl = src_tbl
        self.tgt_tbl = tgt_tbl
        self.scm_type = scm_type
                
        self.labels = labels
        self.task_type = task_type
        self.col_mapping = col_mappings
        self.column_num = len(col_mappings)
        
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
        
    def serialize_without_label(self, sample_num=10, mode=1):
        return f'Table A is:\n{self._smaple_table(self.src_tbl, sample_num).to_markdown()}\nTable B is:\n{self._smaple_table(self.tgt_tbl, sample_num).to_markdown()}\n'
        
    def serialize_with_label(self, sample_num=10, mode=1):
        assert self.labels is not None
        
        no_lab_s = self.serialize_without_label(sample_num)
        
        label_s = []
        for col_map, lab in zip(self.col_mapping, self.labels):
            src_col, tgt_col = col_map
            match_s = 'matched' if lab==1 else 'not matched'
            label_s.append(f'{src_col} in Table A and {tgt_col} in Table B are {match_s}')
        label_s = '\n'.join(label_s)
        return f'{no_lab_s}\n{label_s}'
    
class SCMData(BaseData):
    def __init__(self, dataset_name:str, col1: dict, col2: dict, label: int, task_type:str='scm'):
        super(SCMData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.col1 = col1
        self.col2 = col2
        self.label = label
        self.task_type = task_type
        
    def serialize_without_label(self, mode=1):
        return f'Column A is {self.col1} and Column B is {self.col2}'.replace('{', '').replace('}', '')
    
    def serialize_with_label(self, mode=1):
        with_label_s = self.serialize_without_label()
        match_s = 'matched' if self.label==1 else 'not matched'
        return f'{with_label_s} and they are {match_s}'