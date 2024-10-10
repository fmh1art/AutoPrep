from .BaseDataset import *

class DIDataset(BaseDataset):
    def __init__(self, dataset_name:str):
        super(DIDataset, self).__init__(dataset_name)
        
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        def load_DIData_from_split(data_path, split:str, dn:str):
            
            instances = []
            table = pd.read_csv(os.path.join(data_path, f'{split}_table.csv'))
            labels = pd.read_csv(os.path.join(data_path, f'{split}_label.csv'))
            
            for idx in table.index:
                tuple = table.loc[idx].to_dict()
                label = labels.loc[idx].to_dict()
                
                ins = DIData(dataset_name=dn, tuple=tuple, labels=label)
                instances.append(ins)
                
            return instances
            
            
        if data_path == None:
            data_path = f'{DATA_PATH}/DI/{self.dataset_name}/'
        
        self.train_data = load_DIData_from_split(data_path, 'train', self.dataset_name)
        self.valid_data = load_DIData_from_split(data_path, 'valid', self.dataset_name)
        self.test_data = load_DIData_from_split(data_path, 'test', self.dataset_name)        
        
        self.tol_data = self.train_data + self.valid_data + self.test_data
