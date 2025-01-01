import global_values as GV
from src.data import TQAData
from src.tools.logger import Logger
from src.model.mula_tabpro.agent import Ansketch, ColTypeDeducer

class QueryAnalyzer:
    def __init__(self, llm_name='gpt-3.5-turbo-0301', logger_root='tmp/table_llm_log', logger_file=f'mula_tabpro_v{GV.TABLELLM_VERSION}.log'):
        self.name = 'Query Analyzer'
        self.llm_name = llm_name
        self.ansketch = Ansketch(llm_name=self.llm_name, logger_root=logger_root, logger_file=logger_file)
        self.coltype_deducer = ColTypeDeducer(llm_name=self.llm_name, logger_root=logger_root, logger_file=logger_file)
        self.logger = Logger(name=self.name.capitalize(), root=logger_root, log_file=logger_file)

    def _get_related_coltype_1_round(self, data:TQAData):
        ansketch_sql,_,_ = self.ansketch.process(data)
        coltype_dict = self.coltype_deducer.process(data, ansketch_sql)
        return coltype_dict
    
    def get_related_coltype(self, data:TQAData, vote_round=1):
        type_vote = {}
        for _ in range(vote_round):
            coltype_dict = self._get_related_coltype_1_round(data)
            for col, coltype in coltype_dict.items():
                if col not in type_vote:
                    type_vote[col] = []
                type_vote[col].append(coltype)

        final_coltype_dict = {}
        for col, votes in type_vote.items():
            final_coltype_dict[col] = max(set(votes), key=votes.count)
            
        return final_coltype_dict