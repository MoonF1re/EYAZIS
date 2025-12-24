import math
from collections import Counter, defaultdict
from utils import tokenize

class Document:
    documents = {}
    inverted_index = defaultdict(set)
    term_doc_freq = defaultdict(int)

    def __init__(self, doc_id, title, text):
        self.documentID = doc_id
        self.title = title
        self.text = text
        self.tokens = tokenize(text)
        self.term_freq = Counter(self.tokens)

    def add_to_base(self):
        Document.documents[self.documentID] = self
        for term in set(self.tokens):
            Document.inverted_index[term].add(self.documentID)
            Document.term_doc_freq[term] += 1

    @staticmethod
    def get_idf(term):
        N = len(Document.documents)
        Pi = Document.term_doc_freq.get(term, 0)
        if Pi == 0:
            return 0
        return math.log(N / Pi)

    def get_vector(self):
        vector = {}
        for term, q in self.term_freq.items():
            vector[term] = q * Document.get_idf(term)
        return vector
