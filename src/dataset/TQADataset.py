from .BaseDataset import *

class TQADataset(BaseDataset):
    def __init__(self, dataset_name:str, max_row=-1, max_col=-1):
        super(TQADataset, self).__init__(dataset_name)
        
        self.max_row = max_row
        self.max_col = max_col
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []
        self.test_seen_data, self.test_unseen_data = [], []
        
        
    def load_data(self, data_path=None):
        
        def load_TQAData_from_split(split:pd.DataFrame, dn:str):

            instances = []

            for i, row in split.iterrows():
                # id,table_id,table,answer
                tbl_path = row['table']
                question = row['question']
                answer = row['answer']
                id = row['id']
                try:
                    tbl=pd.read_csv(os.path.join(data_path, tbl_path), sep=',')
                except:
                    tbl=pd.read_csv(os.path.join(data_path, tbl_path).replace('.csv', '.tsv'), sep='\t')

                # Truncate the table
                if self.max_row > 0:
                    tbl = tbl.head(self.max_row)
                if self.max_col > 0:
                    tbl = tbl.iloc[:, :self.max_col]
                
                # search metadata based on tbl_path
                meta_data_row = meta_data.loc[tbl_path]
                tbl_title = meta_data_row['title']
                tbl_caption = meta_data_row['caption']

                instance = TQAData(dataset_name=dn, tbl=tbl, question=question, label=answer, id=id, title=tbl_title, caption=tbl_caption)
                instances.append(instance)
                
            return instances
            
        if data_path == None:
            data_path = f'{DATA_PATH}/TQA/{self.dataset_name}/'
        print(data_path)
        
        train = pd.read_csv(data_path + 'train.csv')
        test_seen = pd.read_csv(data_path + 'test_seen.csv')
        test_unseen = pd.read_csv(data_path + 'test_unseen.csv')
        meta_data = pd.read_csv(data_path + 'table-metadata.tsv', sep='\t')
        # index column: contextId
        meta_data.set_index('contextId', inplace=True)

        self.train_data = load_TQAData_from_split(train, self.dataset_name)
        self.test_seen_data = load_TQAData_from_split(test_seen, self.dataset_name)
        self.test_unseen_data = load_TQAData_from_split(test_unseen, self.dataset_name)
        self.test_data = self.test_seen_data + self.test_unseen_data
        
        self.tol_data = self.train_data + self.valid_data + self.test_data
