from .BaseData import *

class CTAData(BaseData):
    def __init__(self, dataset_name:str, columns:dict, labels:dict, task_type:str='cta'):
        super(CTAData, self).__init__('cta')
        self.dataset_name = dataset_name
        self.columns = columns
        self.labels = labels
        self.task_type = task_type
        self.column_num = len(columns.keys())
        
    def eval_prediction(self, predicted):
        """Evaluate the prediction is correct or not.

        Args:
            predicted (dict): an example is {'0': "type", '1': "name"}. !! the value is not a list

        Returns:
            bool: True/Flase, represent whether the prediction is totally correct or not.
        """
        result = True
        for i in predicted.keys():
            if predicted[i].lower() not in [label.lower() for label in self.labels[i]]:
                result = False
        return result
        
    def serialize_without_label(self, mode=1):
        def with_single_column(columns):
            column = columns['0']
            print(column)
            return f'The Column is {" | ".join([str(v) for v in column.values() if v is not None])}'
        
        def with_multiple_column(columns):
            column_s_list = []
            for i in columns.keys():
                idx = int(i)+1
                column = columns[i]
                column_s_list.append(f'Column {idx}: {" | ".join([str(v) for v in column.values() if v is not None])}')
            return '\n'.join(column_s_list)
                
        if self.column_num == 1:
            return with_single_column(self.columns)
        else:
            return with_multiple_column(self.columns)
        
    def serialize_with_label(self, mode=1):
        assert self.labels is not None
        
        column_s = self.serialize_without_label(mode)
        if self.column_num == 1:
            label_s = f'The Column Name is {"or".join(self.labels["0"])}'
        else:
            label_s = []
            for i in self.labels.keys():
                idx = int(i)+1
                label_s.append(f'The name of Column {idx} is {"or".join(self.labels["0"])}')
            label_s = '\n'.join(label_s)
        return f'{column_s}\n{label_s}'