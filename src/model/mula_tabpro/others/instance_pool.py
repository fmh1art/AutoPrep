
import os
from typing import List

from src.tools.utils import BM25, all_filepaths_in_dir, open_json, save_json
from src.model.mula_tabpro.others.retriever import TextSimRetriever

class BaseInstance:
    def __init__(self, id: str, context:str, q: str, a:str, type:str):
        """The base class of all instances

        Args:
            id (str): is the id of TQAData
            context (str): the serialized table
            q (str): the question or the statement
            a (str): the correct output
            type (str): the type of the instance, format: 'agnet_name-instance, e.g. 'cleaner-self_correction'
        """
        self.id = id
        self.context = context
        self.q = q
        self.a = a
        self.type = type
        self.key = q

class InstanceWithExplanation(BaseInstance):
    def __init__(self, id: str,  context:str, q: str, a:str, explanation:str, type:str):
        super().__init__(id, context, q, a, type)
        self.explanation = explanation

class OPAgentInstance(BaseInstance):
    def __init__(self, id: str, context: str, q: str, a: str, type: str):
        super().__init__(id, context, q, a, type)
        # q is the table wrangling requirement

class SelfCorrectionInstance(BaseInstance):
    def __init__(self, id: str, context:str, q: str, last_a:str, last_err:str, a:str, type:str, key='None'):
        super().__init__(id, context, q, a, type)
        self.last_a = last_a
        self.last_err = last_err

        self.key = last_err if key == 'None' or key is None else key


class InstancePool:
    """This class is used to store the instances of Self-Correction #! Currently, only for Self-Correction

    Args: 
        instance_flag (str): the flag of the instance, e.g. 'self-correction', 'coltype_deducer'
    """
    def __init__(self, pool_name:str, pool_root='tmp/instances', load_from=None):
        self.pool_name = pool_name
        self.pool_root = os.path.join(pool_root, pool_name)
        # the key is the intance type
        self.instances = {}
        self.retriever = {} 

        self._initialize_pool(pool_root=os.path.join(pool_root, load_from) if load_from is not None else None)
        self._build_retriever()

    def save_pool(self, save_root=None):

        save_root = self.pool_root if save_root is None else save_root

        if not os.path.exists(save_root):
            os.makedirs(save_root)

        for type in self.instances:
            instances = self.instances[type]
            ins_js = []
            for ins in instances:
                ins_js.append(ins.__dict__)
            save_path = os.path.join(save_root, type + '.json')
            save_json(ins_js, save_path)

    def add_instance(self, instance:BaseInstance, init=False):
        if instance.type not in self.instances:
            self.instances[instance.type] = []
        self.instances[instance.type].append(instance)

        if not init:
            if instance.type not in self.retriever:
                self.retriever[instance.type] = TextSimRetriever([instance.key], [instance.id], type=instance.type)
            else:
                self.retriever[instance.type].add_text(instance.key, instance.id)

    def remove_instance_by_ids(self, ids:List[str]):
        for type in self.instances:
            instances = self.instances[type]

            old_ins_cnt = len(instances)

            new_instances = []
            for ins in instances:
                if ins.id not in ids:
                    new_instances.append(ins)
            self.instances[type] = new_instances

            new_ins_cnt = len(new_instances)

            print(f'original {old_ins_cnt} instances, after removing {old_ins_cnt-new_ins_cnt} instances, {new_ins_cnt} instances left')
            
        
        for type in self.retriever:
            retriever = self.retriever[type]
            retriever.remove_texts_by_ids(ids)

    def retrieve(self, instance:BaseInstance, top_k=1):
        type = instance.type
        if type not in self.retriever:
            return []
        retriever = self.retriever[type]
        retrieved_indices = retriever.retrieve(instance.key, top_k)
        return [self.instances[type][i] for i in retrieved_indices]

    def _build_retriever(self):
        for type in self.instances:
            instances = self.instances[type]
            corpus = [ins.key for ins in instances]
            ids = [ins.id for ins in instances]
            self.retriever[type] = TextSimRetriever(corpus, ids, type=type)

    def _initialize_pool(self, pool_root=None):
        pool_root = self.pool_root if pool_root is None else pool_root
        if pool_root is None or not os.path.exists(pool_root):
            return
         
        all_paths = all_filepaths_in_dir(pool_root, endswith='.json')
        for file_path in all_paths:
            file_name = os.path.basename(file_path)
            type = file_name.replace('.json', '')
            instances = open_json(file_path)

            for ins_js in instances:
                ins = SelfCorrectionInstance(id=ins_js['id'], context=ins_js['context'], q=ins_js['q'], last_a=ins_js['last_a'], last_err=ins_js['last_err'], a=ins_js['a'], type=type, key=ins_js['key'])
                if 'self_correction' in file_name:
                    ins.key = ins.last_err
                
                self.add_instance(ins, init=True)

        print(f'Pool {self.pool_name} is initialized with {sum([len(inses) for k, inses in self.instances.items()])} instances')