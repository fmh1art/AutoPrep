import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

SAVE_STEP = 3000

CURRENT_YEAR = '2024'
DATASET_YEAR = '2014'

TYPE_DEDUCE_RATIO = 0.8
DATE_RATIO_ERR = 0.5

DEFAULT_ROW_CUT = 22
MAX_INPUT_LIMIT = 8192-200
MAX_OUTPUT_LIMIT = 4000

DATE_SYMBOLS_SORT = 'YymbBd'
TIME_SYMBOLS_SORT = 'pHIMSfaA'

LLM_HYPER_PARAMS = {
    'temperature': 0,
    'max_tok': MAX_OUTPUT_LIMIT,
}

WEEKDAY_DIC = {
    'friday': True,
    'fri.': True,
    'fri': True,
    'monday': True,
    'mon.': True,
    'mon': True,
    'saturday': True,
    'sat.': True,
    'sat': True,
    'sunday': True,
    'sun.': True,
    'sun': True,
    'thursday': True,
    'thu.': True,
    'thu': True,
    'tuesday': True,
    'tue.': True,
    'tue': True,
    'wednesday': True,
    'wed.': True,
    'wed': True,
}

SPECIAL_CHAR_DICT = {
    '%': 'percent',
    '★': 'star',
    '￥': 'yuan',
    '#': 'number',
    '<': 'less than',
    '>': 'greater than',
    '=': 'equal',
    '²': ' square ',
    '€': 'euro',
    'm/s': 'meters per second',
    'km/h': 'kilometers per hour',
    '°C': 'degrees Celsius',
    '°F': 'degrees Fahrenheit',
    'km/s': 'kilometers per second',
}

NAMES = {
    'EXT_COL': 'extract_column', #!
    'CAL_COL': 'calculate_column', #!
    'BOOL_COL': 'boolean_column', #!
    'COMB_COL': 'combine_column', #!
    'INF_COL': 'infer_column', #!
    'END': 'end', #!
    'GEN_NEW_COL': 'generate_new_column', #!


    'STAND': 'standardization',
    
    'EXT_ROW': 'extract_row',
    'EXT_MAX_CONS_RECORD': 'extract_max_consecutive_record',

    'SORT_BY': 'sort_by',
    'GROUP_STATISTICS': 'group_statistics',

    'GEN_CON_COL': 'generate_conditional_column',
    'SPLIT_COL': 'split_column',

    'INIT': '<init>',
    'END': '<assign_other_agent>',

    'STAND_DATETIME': 'standardize_datetime',
    'REMOVE_SYMBOL': 'remove_noisy_symbol',
    'REMOVE_UNIT': 'remove_unit',
    'STAND_NUMERICAL': 'standardize_numerical',
}

EM_ENTITY_TYPE = {
    'abt_buy': 'Product',
    'itunes_amazon': 'Song',
    'fodors_zagats': 'Restaurant',
    'dblp_acm': 'Publication',
    'dbpl_scholar': 'Publication',
    'amazon_google': 'Software',
    'walmart_amazon': 'Product',
    'beer': 'Beer',
    
    'company': 'Company',
    'clothing': 'Clothing',  
}

SCM_Benchmark = {
    'amazon_google': 'deepm',
    'beeradvo_ratebeer': 'deepm',
    'dblp_acm': 'deepm',
    'dblp_scholar': 'deepm',
    'fodors_zagats': 'deepm',
    'itunes_amazon': 'deepm',
    'walmart_amazon': 'deepm',
    
    'chembl': 'fabricated',
    'open_data': 'fabricated',
    'tpc_di': 'fabricated',
    
    'v100': 'sotab',
    'v300': 'sotab',
    'v500': 'sotab',
    
    'no_headers': 't2d',
    't2d_sm_supplement_metadata': 't2d',
    'with_headers': 't2d',
    
    'musicians': 'wikidata',
}

DATASETS = {
    'SCM': list(SCM_Benchmark.keys()),
    'CTA': ['efthymiou', 'limaye', 'sotab_depedia', 'sotab_shemaorg', 'viznet', 'wikitable'],
    'DI': ['buy', 'restaurant'], 
    'ED': ['adult', 'hospital'],
    'EM': ['abt_buy', 'amazon_google', 'beer', 'dblp_acm', 'dblp_scholar', 'fodors_zagat', 'itunes_amazon', 'walmart_amazon']
}

ord_pref = {
    1: 'st',
    2: 'nd',
    3: 'rd',
    4: 'th',
    5: 'th',
    6: 'th',
    7: 'th',
    8: 'th',
    9: 'th',
    0: 'th',
    11: 'th',
    12: 'th',
    13: 'th',
    14: 'th',
    15: 'th',
    16: 'th',
    17: 'th',
    18: 'th',
    19: 'th',
    20: 'th',
}

CLAUSE_KEYWORDS = (
        "select",
        "from",
        "where",
        "group",
        "order",
        "limit",
        "intersect",
        "union",
        "except",
    )
JOIN_KEYWORDS = ("join", "on", "as")
WHERE_OPS = (
    "not",
    "between",
    "=",
    ">",
    "<",
    ">=",
    "<=",
    "!=",
    "in",
    "like",
    "is",
    "exists",
)
UNIT_OPS = ("none", "-", "+", "*", "/")
AGG_OPS = ("none", "max", "min", "count", "sum", "avg")
ALL_KEY_WORDS = CLAUSE_KEYWORDS + JOIN_KEYWORDS + WHERE_OPS + UNIT_OPS + AGG_OPS
KEPT_WHERE_OP = ('not', 'in', 'exists')
COND_OPS = ('and', 'or')

OP_STRING2CLASS = {
    NAMES['INIT']: "InitOP",

    NAMES['EXT_COL']: "ExtCol",
    NAMES['EXT_ROW']: "ExtRow",
    NAMES['EXT_MAX_CONS_RECORD']: "ExtMaxConsRecord",

    NAMES['SORT_BY']: "SortBy",
    NAMES['GROUP_STATISTICS']: "GroupStatistics",

    NAMES['GEN_NEW_COL']: "GenNewCol",
    NAMES['GEN_CON_COL']: "GenConCol",

    NAMES['END']: "EndOP",
    NAMES['STAND_DATETIME']: 'StandDatetime',
    NAMES['REMOVE_SYMBOL']: 'RemoveSymbol',
    NAMES['REMOVE_UNIT']: 'RemoveUnit',
    NAMES['STAND_NUMERICAL']: 'StandNumerical',
}

AGENT_STRING2CLASS = {
    "simple_agent": "SimpleAgent",
    "cleaner": "Cleaner",
    "view_generator": "ViewGenerator",
    "nl2sqler": "NL2SQLer",
}

OP2AGENT = {
    # NAMES['ADD_COL_BY_CALCULATING']: "synthesizer",
    # NAMES['ADD_COL_BY_TRANSFORMING']: "synthesizer",
    # NAMES['SELECT_COL']: "extractor",
    # NAMES['SELECT_ROW']: "extractor",
    # NAMES['COUNT_BY']: "analyzer",
    # NAMES['SORT_BY']: "analyzer",
}

NEXT_AGENT_DICT = {
    "INIT": ["cleaner", "view_generator", "nl2sqler"],
    "cleaner": ["view_generator", "nl2sqler"],
    "view_generator": ["cleaner", "nl2sqler"],
}

AGENT_NAME2LARGE_NAME = {
    "INIT": "INIT", 
    "analyzer": "Analyzer",
    "answer_generator": "AnswerGenerator",
    "cleaner": "Cleaner",
    "view_generator": "ViewGenerator",
    "nl2sqler": "NL2SQLer",
}

TASK_TYPE = 'tableqa'
# TASK_TYPE = 'tablefact'

SPLIT = 'test'
INS_LOAD_FROM = None
# INS_LOAD_FROM = f'correct_instances-{TASK_TYPE}'

MEMORY_RETREIVE_FUNC = 'LEVEN_RATION'
# MEMORY_RETREIVE_FUNC = 'SBERT_EMB_SIM'

SELF_CORRECTION = False
SELF_CORRECTION_NUM = 1 if SELF_CORRECTION else 0

RETRIEVE_DEMO = False
RETRIEVE_DEMO_NUM = 1 if RETRIEVE_DEMO else 0

AGENTS = ['nl2sqler', 'view_generator', 'cleaner', 'coltype_deducer', 'binder', 'imputater']
# LLM_NAME = 'gpt-3.5-turbo-0613'
# LLM_NAME = 'o1-preview-2024-09-12'
# LLM_NAME = 'gpt-4'
# LLM_NAME = 'deepseek-coder'
LLM_NAME = 'deepseek-chat'
LLM_DICT = {agent: LLM_NAME for agent in AGENTS}
DEMO_MODE = {
    # agent: 'retrieved' 
    agent: 'manual' 
    for agent in AGENTS
}

EXT_REL_COL = True
BASE_STAND = False

DATA_PATH = r'E:\fmh\data'
PROJ_PATH = r'E:\fmh\MulA_Tabpro'
# DATA_PATH = r'D:\1th-D\Firefly\RAG_LLM_DM\data'
# PROJ_PATH = r'D:\0th-D\MulA_Tabpro'

TABLELLM_VERSION = f'3.11-{TASK_TYPE}-{LLM_NAME}-selfc{SELF_CORRECTION_NUM}-retd{RETRIEVE_DEMO_NUM}-{MEMORY_RETREIVE_FUNC[:5]}-RetDFirst'

MULTIA_TEMP_DATA_PATH = f'tmp/mul-dp_temp_data_v{TABLELLM_VERSION}.pkl'

debug = True
cut_log = False

# KEY_FILE = 'keys.txt'
# OPENAI_BASE_URL = None

# KEY_FILE = 'keys_CHN.txt'
# OPENAI_BASE_URL = "https://35.aigcbest.top/v1"

KEY_FILE = 'keys_deepseek.txt'
OPENAI_BASE_URL = "https://api.deepseek.com"