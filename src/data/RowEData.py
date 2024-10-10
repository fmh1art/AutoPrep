from .BaseData import *

class RowEData(BaseData):
    
    def __init__(self, dataset_name:str, tbl:dict, 
                 clue, row, offset, data_type:str, task_type:str='RowE', id='NO_ID'):
        super(RowEData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.clue = clue
        self.row = row
        self.data_type = data_type
        self.task_type = task_type
        self.id = id
        self.offset = offset
        
        if self.data_type == 'row_i':
            row_id = self.clue
            self.data_description = f'Output the {row_id}{get_ord_prefix(row_id)} Row.'
        elif self.data_type == 'row_val':
            col, val = self.clue
            self.data_description = f'Output the Row where the Value of Column "{col}" is "{val}".'
        elif self.data_type == 'krow_val':
            col, val = self.clue
            k = self.offset
            tmp = 'Above' if k<0 else 'Below'
            self.data_description = f'Output the {tmp} {abs(k)}{get_ord_prefix(k)} Row where the Value of Column "{col}" is "{val}".'
        elif self.data_type == 'row_imn':
            row_id = self.clue
            m, n = self.offset
            self.data_description = f'Output the value of {m}{get_ord_prefix(m)} to {n}{get_ord_prefix(n)} columns of the {row_id}{get_ord_prefix(row_id)} Row.'
        elif self.data_type == 'row_icols':
            row_id = self.clue
            cols = self.offset
            self.data_description = f'Output the value of {cols} of the {row_id}{get_ord_prefix(row_id)} Row.'
        elif self.data_type == 'row_valk':
            col, val = self.clue
            k = abs(self.offset)
            self.data_description = f'Output the {k}{get_ord_prefix(k)} Row where the Value of Column "{col}" is "{val}".'
        elif self.data_type == 'row_val-k':
            col, val = self.clue
            k = abs(self.offset)
            self.data_description = f'Output the {k}{get_ord_prefix(k)} Last Row where the Value of Column "{col}" is "{val}".'



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