from typing import List
from src.tools.utils import *
import pandas as pd

class BaseData:
    def __init__(self, task_type:str):
        self.task_type = task_type
    
    def serialize_with_label(self, mode=1):
        raise NotImplementedError
        
    def serialize_without_label(self, mode=1):
        raise NotImplementedError
    
    def __str__(self):
        if self.labels is not None or self.label is not None:
            return f'{self.serialize_with_label()}'
        else:
            return f'{self.serialize_without_label()}'