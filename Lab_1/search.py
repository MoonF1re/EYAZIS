import math
from document import Document
from utils import tokenize

class SearchResult:
    def __init__(self, document, rank, matched_terms):
        self.documentId = document.documentID
        self.title = document.title
        self.rank = rank
        self.matched_terms = matched_terms
        self.snippet = document.text[:300]

class Search:
    def __init__(self, query):
        self.query = query
        # токенизация запроса
        self.query_terms = tokenize(query)


    def get_query_vector(self, doc_vector):
        return {term: 1 for term in self.query_terms if term in doc_vector}

    @staticmethod
    def scalar_product(a, b):
        return sum(a[t] * b[t] for t in a if t in b)

    @staticmethod
    def norm(v):
        return math.sqrt(sum(x * x for x in v.values()))

    def search(self):
        results = []

        for doc in Document.documents.values():
            doc_vector = doc.get_vector()
            query_vector = self.get_query_vector(doc_vector)
            if not query_vector:
                continue
            numerator = self.scalar_product(doc_vector, query_vector)
            denominator = self.norm(doc_vector) * self.norm(query_vector)
            if denominator == 0:
                continue
            rank = numerator / denominator
            matched = list(query_vector.keys())
            results.append(SearchResult(doc, rank, matched))
        return sorted(results, key=lambda x: x.rank, reverse=True)
