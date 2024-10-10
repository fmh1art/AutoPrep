
import fastbm25

class BM25:
    def __init__(self, corpus):
        tokenized_corpus = [doc.lower().split(" ") for doc in corpus]
        self.model = fastbm25(tokenized_corpus)

    def sims(self, texta, textb):
        return self.model.similarity_bm25(texta.lower().split(" "), textb.lower().split(" "))