from .BaseData import *

class DIData(BaseData):
    def __init__(self, dataset_name:str, tuple:dict, labels=dict, task_type:str='di'):
        
        super(DIData, self).__init__(task_type='di')
        self.dataset_name = dataset_name
        
        self.tuple = tuple
        self.labels = labels
        self.task_type = task_type
    
    def eval_prediction(self, predicted):
        """Evaluate the prediction is correct or not.

        Args:
            predicted (int): 1/0, represent whether the prediction is match or not.

        Returns:
            bool: True/Flase, represent whether the prediction is correct or not.
        """
        return True if self.label == predicted else False
        
    def serialize_without_label(self, mode=1):
        if mode==1:
            return f'Tuple: {self.tuple}.'
        else:
            return 'NOT IMPLEMENTED YET'
        
    def serialize_with_label(self, mode=1):
        assert self.labels is not None
        
        serialized_tuple = self.serialize_without_label(mode)
        label_s = ', '.join([f'The missing value of {k} is {v}' for k, v in self.labels.items()])
        return f'{serialized_tuple} {label_s}'