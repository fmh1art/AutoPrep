import time
from src.model.mula_tabpro import MultiAgentDataPrep

def generate_logical_operators(model:MultiAgentDataPrep=None):
    time.sleep(0.2)
    return ['Remove duplicates', 'Fill missing values', 'Standardize columns']

def generate_final_code(model:MultiAgentDataPrep=None):
    time.sleep(0.2)
    return "SELECT * FROM uploaded_data WHERE condition_based_on('user_question')"

def generate_physical_operators(model:MultiAgentDataPrep=None):
    time.sleep(0.2)
    return ['SQL: DELETE duplicates', 'SQL: UPDATE missing values', 'SQL: ALTER TABLE for standardization']