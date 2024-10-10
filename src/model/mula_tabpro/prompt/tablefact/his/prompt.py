from global_values import NAMES

DESC_END = f"""If it is no need to use the above operators, return {NAMES['END']}."""
HEAD_OP_GEN = "You are a agent to use operators to process the table for determine whether the statement is True or False. Since the statement could be false, make sure the processed table is not empty."

#! without func_str is better
op_desc_with_fun_str = False