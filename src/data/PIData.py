from .BaseData import *

class PIData(BaseData):
    def __init__(self, dataset_name:str, tbl:dict, 
                 selected_cells:List, labels:List, task_type:str='PI', id='NO_ID'):
        super(PIData, self).__init__(task_type)
        self.dataset_name = dataset_name
        self.tbl = tbl
        self.selected_cells = selected_cells
        self.labels = labels
        self.task_type = task_type
        self.id = id
        
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
            cells_ser = '\n'.join([f'{i+1}. {cell}' for i, cell in enumerate(self.selected_cells)])
            ser = f'The table is:\n{str(self.tbl)}\nthe Selected cells are:\n{cells_ser}'
            return ser
        
    def serialize_with_label(self, mode=1):
        assert self.labels is not None
        
        no_lab_s = self.serialize_without_label(mode=mode)
        
        label_s = 'The positions of the selected cells are:\n' +\
                     '\n'.join([f'{i+1}. row {label[0]}, column {label[1]}' for i, label in enumerate(self.labels)])
        return f'{no_lab_s}\n{label_s}'