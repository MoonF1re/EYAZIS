from collections import Counter

def build_statistics(results, method="ngram"):
    counter = Counter(r[method] for r in results)
    return dict(counter)
