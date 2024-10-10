from .BaseData import *

class SubTblEData(BaseData):
    
    def __init__(self, dataset_name:str, tbl:dict, 
                 clue, subtbl, data_type:str, task_type:str='SubTblE', id='NO_ID'):
        super(SubTblEData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.clue = clue
        self.subtbl = subtbl
        self.data_type = data_type
        self.task_type = task_type
        self.id = id

        if self.data_type == 'subt_i1i2':
            i1, i2 = self.clue
            self.data_description = f'Output the {i1}{get_ord_prefix(i1)} to {i2}{get_ord_prefix(i2)} Rows.'
        elif self.data_type == 'subt_rowids':
            rowids = self.clue
            self.data_description = f'Output the Rows with row_id in {rowids}.'
        elif self.data_type == 'subt_j1j2':
            j1, j2 = self.clue
            self.data_description = f'Output the Subtales from {j1}{get_ord_prefix(j1)} to {j2}{get_ord_prefix(j2)} Columns.'
        elif self.data_type == 'subt_cols':
            cols = self.clue
            self.data_description = f'Output the Subtales with Columns: {cols}.'
        elif self.data_type == 'subt_ij':
            i1, i2, j1, j2 = self.clue
            self.data_description = f'Output the Subtales from {i1}{get_ord_prefix(i1)} to {i2}{get_ord_prefix(i2)} Rows, {j1}{get_ord_prefix(j1)} to {j2}{get_ord_prefix(j2)} Columns.'
        elif self.data_type == 'subt_i1i2cols':
            i1, i2 = self.clue[0], self.clue[1]
            cols = self.clue[2]
            self.data_description = f'Output the Subtales from {i1}{get_ord_prefix(i1)} to {i2}{get_ord_prefix(i2)} Rows with Columns: {cols}.'


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