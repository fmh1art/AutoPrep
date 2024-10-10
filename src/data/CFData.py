from .BaseData import *

class CFData(BaseData):
    
    def __init__(self, dataset_name:str, tbl:dict, 
                 clue, column_name, data_type:str, task_type:str='CF', id='NO_ID'):
        super(CFData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.clue = clue
        self.column_name = column_name
        self.data_type = data_type
        self.task_type = task_type
        self.id = id
        self.offset = 0

        if self.data_type == 'number[i]':
            self.data_description = f'Output the Column Name of {self.clue}{get_ord_prefix(self.clue)} Column.'
        elif self.data_type == 'exact':
            self.data_description = f'Output the Column Name of the Cell with Value "{self.clue}".'
        else:
            self.offset = int(self.data_type.split('_')[1])
            if self.data_type.startswith('left'):
                self.data_description = f'Output the Name of the Column {self.offset} Columns Left to the Column with Value "{self.clue}".'
            else:
                self.data_description = f'Output the Name of the Column {self.offset} Columns Right to the Column with Value "{self.clue}".'
        
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