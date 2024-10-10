from .BaseDataset import *

class EDDataset(BaseDataset):
    def __init__(self, dataset_name:str):
        super(EDDataset, self).__init__(dataset_name)
        
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        def load_EDData_from_split(table:pd.DataFrame, split:pd.DataFrame, dn:str):
            
            instances = []
            
            for i, row in split.iterrows():
                row_id, col_name, is_clean = row['row_id'], row['col_name'], row['is_clean']
                if int(is_clean)==1:
                    labels = []
                else:
                    labels = [col_name]
                tuple = table.iloc[row_id].to_dict()
                ins = EDData(dataset_name=dn, tuple=tuple, labels=labels, task_type='ed')
                instances.append(ins)
            
            return instances
            
        if data_path == None:
            data_path = f'{DATA_PATH}/ED/{self.dataset_name}/'
        
        table = pd.read_csv(f'{data_path}/table.csv', index_col='Unnamed: 0')
        train = pd.read_csv(f'{data_path}/train.csv')
        test = pd.read_csv(f'{data_path}/test.csv')
        valid = pd.read_csv(f'{data_path}/valid.csv')
        
        self.train_data = load_EDData_from_split(table, train, self.dataset_name)
        self.valid_data = load_EDData_from_split(table, train, self.dataset_name)
        self.test_data = load_EDData_from_split(table, train, self.dataset_name)        
        
        self.tol_data = self.train_data + self.valid_data + self.test_data
