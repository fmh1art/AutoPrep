from .BaseData import *

class TQAData(BaseData):
    def __init__(self, dataset_name:str, tbl:pd.DataFrame, 
                 question:str, label:str, task_type:str='tqa', id='NO_ID', title=None, caption=None):
        super(TQAData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.question = question
        self.label = label
        self.task_type = task_type
        self.id = id
        self.title = title
        self.caption = caption
        self.pred = None
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
        
    def serialize_without_label(self, mode=1):
        if mode==1:
            tbl_dic = {}
            # tbl_dic from self.tbl, get {col:{1:val1, 2:val2, ...}, ...}
            for col in self.tbl.columns:
                # 得到 {col:{0:val1, 1:val2, ...}, ...}
                tmp = self.tbl[col].to_dict()
                # 得到 {col:{1:val1, 2:val2, ...}, ...}
                tbl_dic[col] = {k+1:v for k,v in tmp.items()}
            return json.dumps(tbl_dic)
        elif mode==2:
            # get {1: {col1: val1, col2: val2, ...}, 2: {col1: val1, col2: val2, ...}, ...}
            tbl_dic = {}
            for i, row in self.tbl.iterrows():
                tbl_dic[i+1 if isinstance(i, int) else i] = row.to_dict()
            return json.dumps(tbl_dic)
        elif mode==3:
            # get markdown table: | col1 | col2 | ... |\n|---|---|...|\n|val1|val2|...|
            tbl_s = '|'
            tbl_s += '|'.join(self.tbl.columns) + '|\n'
            tbl_s += '|---'*len(self.tbl.columns) + '|\n'
            for i, row in self.tbl.iterrows():
                tbl_s += '|'
                tbl_s += '|'.join([str(val) for val in row]) + '|\n'
            return tbl_s
        
    def serialize_with_label(self, sample_num=10, mode=1):
        assert self.labels is not None
        
        no_lab_s = self.serialize_without_label(sample_num, mode=mode)
        
        label_s = []
        for col_map, lab in zip(self.col_mapping, self.labels):
            src_col, tgt_col = col_map
            match_s = 'matched' if lab==1 else 'not matched'
            label_s.append(f'{src_col} in Table A and {tgt_col} in Table B are {match_s}')
        label_s = '\n'.join(label_s)
        return f'{no_lab_s}\n{label_s}'