from .BaseData import *

class MVIData(BaseData):
    def __init__(self, dataset_name:str, tbl:dict, 
                 labels:List, text_bef_tbl='', text_aft_tbl='', task_type:str='MVI', id='NO_ID'):
        super(MVIData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.labels = labels
        self.task_type = task_type
        self.id = id
        self.text_bef_tbl = text_bef_tbl
        self.text_aft_tbl = text_aft_tbl
        
    def eval_prediction(self, predicted):
        """Evaluate the prediction is correct or not.

        Args:
            predicted (dict): an example is {'0': "type", '1': "name"}. !! the value is not a list

        Returns:
            bool: True/Flase, represent whether the prediction is totally correct or not.
        """
        pass
    

    def serialize_without_label(self, mode=1):
        if mode==1:
            pass
        
    def serialize_with_label(self, mode=1):
        pass