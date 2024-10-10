from src.data.BaseData import BaseData
from typing import List
from src.tools.utils import *

class Prompter:
    
    @staticmethod
    def prompting(task_description:str, query:BaseData, question:str, demos:List[BaseData]=None, extra_info=None, docs=None, kg_tris=None, max_tok=4096-100):
        prompt = task_description + '\n'
        
        # Demonstration
        if demos is not None:
            for i, demo in enumerate(demos):
                prompt += f'Demonstration {i+1}: \n'
                prompt += demo.serialize_with_label() + '\n'
                
        # Extra info
        if extra_info is not None:
            prompt += extra_info + '\n'
            
        # Docs
        if docs is not None:
            for i, doc in enumerate(docs):
                prompt += f'Document {i+1}: \n'
                prompt += doc + '\n'
        
        # KG triples
        if kg_tris is not None:
            for i, tri in enumerate(kg_tris):
                prompt += f'KG Triple {i+1}: \n'
                prompt += tri + '\n'
            
        # Query
        prompt += 'Query: \n'
        prompt += query.serialize_without_label() + '\n'
        
        # Question
        prompt += question + '\n'
        
        assert cal_tokens(prompt) < max_tok, f'Prompt is too long: {cal_tokens(prompt)}'
        
        return prompt.strip()

    