from .BaseData import *

class EMData(BaseData):
    def __init__(self, dataset_name:str, e1:dict, e2:dict, label=None, entity_type:str=None, task_type:str='em'):
        
        super(EMData, self).__init__(task_type='em')
        self.dataset_name = dataset_name
        if entity_type is None:
            if self.dataset_name in EM_ENTITY_TYPE:
                self.entity_type = EM_ENTITY_TYPE[self.dataset_name]
            else:
                self.entity_type = 'Object'
        else:
            self.entity_type = entity_type
        self.e1 = e1
        self.e2 = e2
        self.label = label
        self.task_type = task_type
    
    def eval_prediction(self, predicted):
        """Evaluate the prediction is correct or not.

        Args:
            predicted (int): 1/0, represent whether the prediction is match or not.

        Returns:
            bool: True/Flase, represent whether the prediction is correct or not.
        """
        return True if self.label == predicted else False
        
    def serialize_without_label(self, mode=3):
        if mode==1: # COL k1 VAL v1 COL k2 VAL v2
            e1_s = ' '.join([f'COL {k} VAL {v}' for k, v in self.e1.items()])
            e2_s = ' '.join([f'COL {k} VAL {v}' for k, v in self.e2.items()])
            return f'Entity1: {e1_s}. Entity2: {e2_s}.'
        elif mode==2: # k1: v1, k2: v2
            e1_s = ', '.join([f'{k}: {v}' for k, v in self.e1.items()])
            e2_s = ', '.join([f'{k}: {v}' for k, v in self.e2.items()])
            return f'{self.entity_type} A is {e1_s}; {self.entity_type} B is {e2_s}'
        elif mode==3: # {k1: {1:v1}, k2: {1:v2}}
            new_e1 = {k: {1: v} for k, v in self.e1.items()}
            new_e2 = {k: {1: v} for k, v in self.e2.items()}
            return f'{self.entity_type} A is\n{new_e1}; {self.entity_type} B is\n{new_e2}'
        
    def serialize_with_label(self, mode=1):
        assert self.label is not None
        
        serialized_entities = self.serialize_without_label(mode)
        match_s = 'matched' if self.label==1 else 'not matched'
        return f'{serialized_entities};\n{self.entity_type} A and B is {match_s}'