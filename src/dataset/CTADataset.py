from .BaseDataset import *
class CTADataset(BaseDataset):
    def __init__(self, dataset_name:str):
        super(CTADataset, self).__init__(dataset_name)
        
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        def load_CTAData_from_split(data_path:str, splid:str, dn:str, with_label=True):
            
            instances = []
            
            src_file_path = os.path.join(data_path, f'{splid}-source.jsonl')
            lab_file_path = os.path.join(data_path, f'{splid}-label.jsonl')
            
            src_list, lab_list = [], []
            
            with open(src_file_path, 'r') as file:
                for line in file:
                    src_list.append(json.loads(line))
            with open(lab_file_path, 'r') as file:
                for line in file:
                    lab_list.append(json.loads(line))
            
            if with_label:
                for src, lab in zip(src_list, lab_list):
                    instance = CTAData(dataset_name=dn, columns=src, labels=lab)
                    instances.append(instance)
            else:        
                for src in src_list:
                    instance = CTAData(dataset_name=dn, columns=src, labels=None)
                    instances.append(instance)
            
            return instances
            
        if data_path == None:
            data_path = f'{DATA_PATH}/CTA/{self.dataset_name}/'
        
        self.train_data = load_CTAData_from_split(data_path, splid='train', dn=self.dataset_name, with_label=True)
        self.valid_data = load_CTAData_from_split(data_path, splid='valid', dn=self.dataset_name, with_label=True)
        self.test_data = load_CTAData_from_split(data_path, splid='test', dn=self.dataset_name, with_label=True)
        
        self.tol_data = self.train_data + self.valid_data + self.test_data
