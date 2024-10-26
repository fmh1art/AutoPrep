from src.tools.utils import parse_any_string
import global_values as GV
from .generate_new_column import GenNewCol, ExtractColumn, CalculateColumn, BooleanColumn, CombineColumn

class AutoOP:
    class_dic = {
        GV.NAMES['GEN_NEW_COL']: GenNewCol,
        GV.NAMES['EXT_COL']: ExtractColumn,
        GV.NAMES['CAL_COL']: CalculateColumn,
        GV.NAMES['BOOL_COL']: BooleanColumn,
        GV.NAMES['COMB_COL']: CombineColumn,
    }

    def deduce_op(op_str:str):
        op_str = parse_any_string(op_str).strip()
        for key in AutoOP.class_dic:
            if op_str.startswith(key):
                return AutoOP.class_dic[key]
        raise ValueError(f'E: Function name not found in the output. The function name should be one of the {AutoOP.class_dic.keys()}')
