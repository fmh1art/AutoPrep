from .BaseDataset import *

class SCMDataset(BaseDataset):
    def __init__(self, dataset_name:str):
        super(SCMDataset, self).__init__(dataset_name=dataset_name)
        
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        
    def _covert_tbl_data(self, tbl_datas:List[SCMTable]):
        
        def _sample_dfserise(df:pd.DataFrame, key:str, sample_num:int):
            df = pd.DataFrame(df[key])
            sample_num = sample_num if sample_num < len(df) else len(df)
            emp_num = df.isnull().sum(axis=1)
            weight = (1-emp_num/len(df.columns))
            # 确保权重不为0
            weight = weight.apply(lambda x: 0.1 if x==0 else x)
            return df.sample(sample_num, weights=weight).reset_index(drop=True)
        
        scm_datas = []
        for tbl_data in tbl_datas:
            src_colnames = list(tbl_data.src_tbl.columns)
            tgt_colnames = list(tbl_data.tgt_tbl.columns)
            for src_colname in src_colnames:
                # src_col = pd.DataFrame(tbl_data.src_tbl[src_colname]).to_dict(orient='list')
                src_col = _sample_dfserise(tbl_data.src_tbl, src_colname, 10).to_dict(orient='list')
                for tgt_colname in tgt_colnames:
                    tgt_col = _sample_dfserise(tbl_data.tgt_tbl, tgt_colname, 10).to_dict(orient='list')
                    label = 1 if (src_colname, tgt_colname) in tbl_data.col_mapping else 0
                    scm_datas.append(SCMData(dataset_name=self.dataset_name, col1=src_col, col2=tgt_col, label=label))
        return scm_datas
    
    def convert_tbl_data(self):
        self.train_data = self._covert_tbl_data(self.train_data)
        self.valid_data = self._covert_tbl_data(self.valid_data)
        self.test_data = self._covert_tbl_data(self.test_data)
        self.tol_data = self._covert_tbl_data(self.tol_data)
        
    def load_data(self, data_path=None):
        
        if data_path == None:
            data_path = f'{DATA_PATH}/SCM/{SCM_Benchmark[self.dataset_name]}/{self.dataset_name}/'
        
        mappling_file_path = os.path.join(data_path, f'{self.dataset_name}_mapping.json')
        
        # 加载json文件
        with open(mappling_file_path, 'r') as file:
            mappings = json.load(file)
        print('dataset_name', self.dataset_name)
        if mappings['has_split']:
            self.has_split = True
            
            split_map = {
                'train': self.train_data,
                'valid': self.valid_data,
                'test': self.test_data
            }
            
            tbl_map = {}
            for mapping in mappings['matches']:
                k = (mapping['source_table'], mapping['target_table'], mapping['schema_matching_type'], mapping['split'])
                if k not in tbl_map:
                    tbl_map[k] = []
                    
                tbl_map[k].append((mapping['source_column'], mapping['target_column']))
            
            for k, v in tbl_map.items():
                src_tbl, tgt_tbl, scm_type, split = k
                src_df = pd.read_csv(os.path.join(data_path, f'{src_tbl}.csv'))
                tgt_df = pd.read_csv(os.path.join(data_path, f'{tgt_tbl}.csv'))
                
                col_lis = v
                labs = [1 for _ in range(len(col_lis))]
                
                split_map[split].append(SCMTable(dataset_name=self.dataset_name, 
                                                src_tbl=src_df, tgt_tbl=tgt_df, col_mappings=col_lis, labels=labs, 
                                                scm_type=scm_type))
                    
            self.tol_data = self.train_data + self.valid_data + self.test_data
        else:
            self.has_split = False
            
            tbl_map = {}
            for mapping in mappings['matches']:
                k = (mapping['source_table'], mapping['target_table'], mapping['schema_matching_type'])
                if k not in tbl_map:
                    tbl_map[k] = []
                    
                tbl_map[k].append((mapping['source_column'], mapping['target_column']))
            
            for k, v in tbl_map.items():
                src_tbl, tgt_tbl, scm_type = k
                src_df = pd.read_csv(os.path.join(data_path, f'{src_tbl}.csv'))
                tgt_df = pd.read_csv(os.path.join(data_path, f'{tgt_tbl}.csv'))
                
                col_lis = v
                labs = [1 for _ in range(len(col_lis))]
                
                self.tol_data.append(SCMTable(dataset_name=self.dataset_name, 
                                            src_tbl=src_df, tgt_tbl=tgt_df, col_mappings=col_lis, labels=labs, 
                                            scm_type=scm_type))
                
                # shuffle后，按照 3:1:1 的比例划分数据集
                shuffle(self.tol_data)
                self.train_data = self.tol_data[:int(len(self.tol_data)*0.6)]
                self.valid_data = self.tol_data[int(len(self.tol_data)*0.6):int(len(self.tol_data)*0.8)]
                self.test_data = self.tol_data[int(len(self.tol_data)*0.8):]
                
        self.convert_tbl_data()