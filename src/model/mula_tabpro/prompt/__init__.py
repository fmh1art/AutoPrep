import global_values as GV

if GV.TASK_TYPE == 'tableqa':
    from .tableqa.nl2sql_prompt import *
    from .tableqa.ansketch_prompt import *
    from .tableqa.end2ender_prompt import *
    from .tableqa.cot_end2ender_prompt import *
    from .tableqa.manager_prompt import *

elif GV.TASK_TYPE == 'tablefact':
    from .tablefact.nl2sql_prompt import *
    from .tablefact.ansketch_prompt import *
    from .tablefact.end2ender_prompt import *
    from .tablefact.cot_end2ender_prompt import *
    from .tablefact.manager_prompt import *


from .coltype_deducer_prompt import *
from .imputater_prompt import *
from .cleaner_prompt import *
from .view_generator_prompt import *

from .coder_prompt import *