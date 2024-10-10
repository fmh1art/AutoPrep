from .BaseDataset import *

class MVIDataset(BaseDataset):
    def __init__(self, dataset_name:str, sample_limit=4000):
        super(MVIDataset, self).__init__(dataset_name)
        
        self.sample_limit = sample_limit
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def load_data(self, data_path=None):
        
        if data_path == None:
            data_path = f'{DATA_PATH}/MVI/{self.dataset_name}/'
        else:
            data_path = f'{data_path}/MVI/{self.dataset_name}/'
        
        cnts = {
            'Cell': int(self.sample_limit / 2),
            'Column': self.sample_limit - int(self.sample_limit / 2),
        }
        
        for mask_type in cnts:
            cnt = cnts[mask_type]
            file_num = cnt // 1000
            if cnt % 1000 != 0:
                file_num += 1
            
            loaded_ds = []
            for i in range(file_num):
                file_name = f'M{mask_type}V_inses_{i}.jsonl'
                ds = load_jsonl(os.path.join(data_path, file_name))
                for line_id, d in enumerate(ds):
                    d['table'] = chage_tableidx_to_int(d['table'])
                    mvi_data = MVIData(self.dataset_name, tbl=d['table'], text_bef_tbl=d['textBeforeTable'], text_aft_tbl=d['textAfterTable'], 
                                        labels=d['label'], task_type='MVI', id=f'{file_name}:{line_id}')
                    loaded_ds.append(mvi_data)
            loaded_ds = loaded_ds[:cnt]
            self.tol_data += loaded_ds

        shuffle(self.tol_data)

        # 随机划分数据集  3：1：1
        self.train_data = self.tol_data[:int(0.6*self.sample_limit)]
        self.valid_data = self.tol_data[int(0.6*self.sample_limit):int(0.8*self.sample_limit)]
        self.test_data = self.tol_data[int(0.8*self.sample_limit):]
