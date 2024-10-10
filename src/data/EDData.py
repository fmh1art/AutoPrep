from .BaseData import *

class EDData(BaseData):
    def __init__(self, dataset_name:str, tuple:dict, labels=List[str], task_type:str='ed'):
        
        super(EDData, self).__init__(task_type='ed')
        self.dataset_name = dataset_name
        
        self.tuple = tuple
        self.labels = labels
        self.task_type = task_type
    
    def serialize_without_label(self, mode=1):
        if mode==1:
            return f'Tuple: {self.tuple}.'
        else:
            return 'NOT IMPLEMENTED YET'
        
    def serialize_with_label(self, mode=1):
        assert self.labels is not None
        
        serialized_tuple = self.serialize_without_label(mode)
        
        if len(self.labels) == 0:
            return f'The tuple is: {serialized_tuple}. The tuple has no errors.'
        else:
            if len(self.labels) == 1:
                label_s = self.labels[0]
            else:
                label_s = ', '.join(self.labels[:-1]) + ' and ' + self.labels[-1]
            return f'The tuple is: {serialized_tuple}. The tuple has error in Attribute: {label_s}.'