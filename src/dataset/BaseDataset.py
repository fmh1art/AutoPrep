import json, os
import pandas as pd
from random import shuffle

from global_values import *
from src.tools.utils import *

from ..data import *


class BaseDataset:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
    
    def load_data(self):
        raise NotImplementedError