from .BaseDataset import *

class EMDataset(BaseDataset):
    def __init__(self, dataset_name:str):
        super(EMDataset, self).__init__(dataset_name)
        
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        def load_EMData_from_split(tableA, tableB, splid:pd.DataFrame, dn:str, with_label=False):
            
            instances = []
            for i, row in splid.iterrows():
                # type: numpy.int64
                l_id = row['ltable_id']
                r_id = row['rtable_id']
                
                label = row['label'] if with_label else None
                
                e1 = tableA[tableA['id'] == l_id].to_dict('records')[0]
                e2 = tableB[tableB['id'] == r_id].to_dict('records')[0]
                e1.pop('id')
                e2.pop('id')
                
                instance = EMData(dataset_name=dn, 
                                e1=e1, e2=e2, label=label)

                instances.append(instance)
            return instances
            
            
        if data_path == None:
            data_path = f'{DATA_PATH}/EM/{self.dataset_name}/'
        
        tableA = pd.read_csv(data_path + 'tableA.csv')
        tableB = pd.read_csv(data_path + 'tableB.csv')
        train = pd.read_csv(data_path + 'train.csv')
        valid = pd.read_csv(data_path + 'valid.csv')
        test = pd.read_csv(data_path + 'test.csv')
            
        self.train_data = load_EMData_from_split(tableA, tableB, train, self.dataset_name, with_label=True)
        self.valid_data = load_EMData_from_split(tableA, tableB, valid, self.dataset_name, with_label=True)
        self.test_data = load_EMData_from_split(tableA, tableB, test, self.dataset_name, with_label=True)
        
        self.tol_data = self.train_data + self.valid_data + self.test_data
