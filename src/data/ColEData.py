from .BaseData import *

class ColEData(BaseData):
    
    def __init__(self, dataset_name:str, tbl:dict, 
                 clue, column, offset, data_type:str, task_type:str='ColE', id='NO_ID'):
        super(ColEData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.clue = clue
        self.column = column
        self.data_type = data_type
        self.task_type = task_type
        self.id = id
        self.offset = offset

        if self.data_type == 'col_all':
            self.data_description = f'Output the Values of Column "{self.clue}".'
        elif self.data_type == 'col_mn':
            m, n = self.offset
            self.data_description = f'Output the Values of Column "{self.clue}" from Row {m} to Row {n}.'
        else:
            col1, val = self.clue
            self.data_description = f'Output the Values of Column "{self.clue}" where the Value of Column "{col1}" is "{val}".'


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