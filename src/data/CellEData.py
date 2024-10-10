from .BaseData import *

class CellEData(BaseData):
    
    def __init__(self, dataset_name:str, tbl:dict, 
                 clue, cell, offset, data_type:str, task_type:str='CellE', id='NO_ID'):
        super(CellEData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.clue = clue
        self.cell = cell
        self.data_type = data_type
        self.task_type = task_type
        self.id = id
        self.offset = offset

        if self.data_type == 'cell_icol':
            rowid, colname = self.clue
            self.data_description = f'Output the Value of the Cell in Row {rowid} and Column "{colname}".'
        elif self.data_type == 'col2cell_col1val':
            col1, val = self.clue
            col2 = self.offset
            self.data_description = f'Output the Value of the Column "{col2}" where the Value of Column "{col1}" is "{val}".'
        else:
            col1, val = self.clue
            k, col2 = self.offset
            shift = 'Above' if k<0 else 'Below'
            self.data_description = f'Output the Value of the Column "{col2}" where the Value of Column "{col1}" is "{val}" {shift} {abs(k)} Rows.'


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