from .BaseDataset import *

class TFVDataset(BaseDataset):
    def __init__(self, dataset_name:str, max_row=-1, max_col=-1):
        super(TFVDataset, self).__init__(dataset_name)

        self.max_row = max_row
        self.max_col = max_col
        self.tol_data, self.train_data, self.test_data, self.valid_data = [], [], [], []

    def load_data(self, data_path=None):

        # this data is processed by Dater

        if data_path == None:
            data_path = f'{DATA_PATH}/TFV/{self.dataset_name}/chain_of_table/test.jsonl'
        print(data_path) 

        datas = []
        with open(data_path, 'r') as file:
            for line in file:
                json_object = json.loads(line)
                datas.append(json_object)

        instances = []
        # print(datas[0])
        for i,row in enumerate(datas):
            # print(row)
            cols = row["table_text"][0]
            rows = row["table_text"][1:]
            table = pd.DataFrame(columns=cols, data=rows)
            table_caption = row["table_caption"]
            statement = row["statement"]
            label = str(row["label"])
            id = str(i)
            if self.max_row > 0 and len(table) > self.max_row:
                table = table[:self.max_row]
            if self.max_col > 0 and len(table[0]) > self.max_col:
                table = [row[:self.max_col] for row in table]
            instance = TFVData(dataset_name=self.dataset_name, tbl=table, question=statement, label=label, id=id,caption = table_caption)
            instances.append(instance)
            
        self.test_data = instances

        self.tol_data = self.train_data + self.valid_data + self.test_data

    def load_data_org(self, data_path=None):

        if data_path == None:
            data_path = f'{DATA_PATH}/TFV/{self.dataset_name}'

        def load_TFVData_from_split(split:str, dn:str):

            instances = []

            example_path = f'{DATA_PATH}/TFV/{dn}/origin/tokenized_data/{split}_examples.json'
            print(example_path)
            with open(example_path,"r") as f:
                data = json.load(f)
            for idx, table_name in enumerate(data):
                tbl = pd.read_csv(f'{DATA_PATH}/TFV/{dn}/origin/data/all_csv/'+table_name, delimiter="#")

                entry = data[table_name]
                # print(entry)
                caption = entry[2]
                if self.max_row > 0:
                    tbl = tbl.head(self.max_row)
                if self.max_col > 0:
                    tbl = tbl.iloc[:, :self.max_col]

                for sent, label, _ in zip(entry[0], entry[1], entry[2]):
                    instance = TFVData(dataset_name=dn, tbl=tbl, question=sent, label=label, id=table_name+str(idx),caption = caption)
                    instances.append(instance)

            return instances

        self.train_data = load_TFVData_from_split("train", self.dataset_name)
        self.test_data = load_TFVData_from_split("test", self.dataset_name)

        self.tol_data = self.train_data + self.test_data