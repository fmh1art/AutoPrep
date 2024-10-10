from .BaseDataset import *

class SubTblEDataset(BaseDataset):
    def __init__(self, dataset_name:str, sample_limit=4000):
        super(SubTblEDataset, self).__init__(dataset_name)
        
        self.sample_limit = sample_limit
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        if data_path == None:
            data_path = f'{DATA_PATH}/SubTblE/{self.dataset_name}/'
        else:
            data_path = f'{data_path}/SubTblE/{self.dataset_name}/'
        
        file_num = self.sample_limit // 1000
        if self.sample_limit % 1000 != 0:
            file_num += 1

        loaded_ds = []
        for i in range(file_num*2):
            tmp = self.dataset_name.replace('tables', '')
            file_name = f'{tmp}_SubTblE_inses_{i}.jsonl'
            ds = load_jsonl(os.path.join(data_path, file_name))
            for line_id, d in enumerate(ds):
                d['table'] = chage_tableidx_to_int(d['table'])
                d['subtable'] = chage_tableidx_to_int(d['subtable'])
                if len(d['table']) > 24 or len(d['table'][1]) > 10:
                    continue
                
                subtbl_data = SubTblEData(self.dataset_name, d['table'], d['clue'], d['subtable'], d['type'], id=f'{file_name}:{line_id}')
                loaded_ds.append(subtbl_data)

        self.tol_data = loaded_ds[:self.sample_limit]
        
        shuffle(self.tol_data)

        # 随机划分数据集  3：1：1
        self.train_data = self.tol_data[:int(0.6*self.sample_limit)]
        self.valid_data = self.tol_data[int(0.6*self.sample_limit):int(0.8*self.sample_limit)]
        self.test_data = self.tol_data[int(0.8*self.sample_limit):]