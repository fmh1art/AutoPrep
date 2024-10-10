import os
from typing import List

from Levenshtein import ratio
import numpy as np

from global_values import MEMORY_RETREIVE_FUNC

class TextSimRetriever:
    def __init__(self, texts:List[str], ids, sim_func=MEMORY_RETREIVE_FUNC, type=None):
        self.texts = texts
        self.ids = ids
        self.sim_func = sim_func
        if self.sim_func == 'SBERT_EMB_SIM':
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens')
            if os.path.exists(fr'tmp\instances\{type}_texts_emb.npy'):
                self.texts_emb = np.load(fr'tmp\instances\{type}_texts_emb.npy')
                # assert len(self.texts) == len(self.texts_emb)
                if len(self.texts) != len(self.texts_emb):
                    raise ValueError(f'texts and texts_emb have different length, texts: {len(self.texts)}, texts_emb: {len(self.texts_emb)}')
                print(f'load {type} texts embeddings from npy file, shape is {self.texts_emb.shape}')
            else:
                self.texts_emb = self.encoder.encode(texts) # shape is (n_texts, 768)
                # save to npy file
                np.save(fr'tmp\instances\{type}_texts_emb.npy', self.texts_emb)
                print(f'save {type} texts embeddings from npy file, shape is {self.texts_emb.shape}')
    
    def retrieve(self, query, topk=1):
        if self.sim_func == 'LEVEN_RATION':
            return self.retrieve_ratio(query, topk)
        elif self.sim_func == 'SBERT_EMB_SIM':
            return self.retrieve_sbert_emb_sim(query, topk)
    
    def retrieve_ratio(self, query, topk=1):
        # return the index(not ids) of most similar text
        scores = [ratio(query, text) for text in self.texts]
        topk = min(topk, len(scores))
        topk_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:topk]

        return topk_indices
    
    def retrieve_sbert_emb_sim(self, query, topk=1):
        query_emb = self.encoder.encode(query) # shape is (768,)
        # calculate cosine similarity between query_emb and texts_emb
        scores = np.dot(self.texts_emb, query_emb) / (np.linalg.norm(self.texts_emb, axis=1) * np.linalg.norm(query_emb)) # this similarity is cosine similarity
        topk = min(topk, len(scores))
        topk_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:topk]

        return topk_indices
    
    def add_text(self, text, id):
        self.texts.append(text)
        self.ids.append(id)
        if self.sim_func == 'SBERT_EMB_SIM':
            new_emb = self.encoder.encode(text)
            # stack new_emb to texts_emb, where new_emb is (768,) and texts_emb is (n_texts, 768)
            self.texts_emb = np.vstack([self.texts_emb, new_emb])
    
    def remove_texts_by_ids(self, ids:List[str]):
        old_texts_cnt = len(self.texts)
        new_texts = []
        new_ids = []
        if self.sim_func == 'SBERT_EMB_SIM':
            new_texts_emb = []
        for i, id in enumerate(self.ids):
            if id not in ids:
                new_texts.append(self.texts[i])
                new_ids.append(self.ids[i])
                if self.sim_func == 'SBERT_EMB_SIM':
                    new_texts_emb.append(self.texts_emb[i])
        self.texts = new_texts
        self.ids = new_ids
        if self.sim_func == 'SBERT_EMB_SIM':
            self.texts_emb = np.array(new_texts_emb)
        new_texts_cnt = len(self.texts)
        print(f'original {old_texts_cnt} texts, after removing {old_texts_cnt-new_texts_cnt} texts, {new_texts_cnt} texts left')