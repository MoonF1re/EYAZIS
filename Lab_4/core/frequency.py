from collections import Counter

def build_frequency(tokens):
    """
    tokens: список слов (str)
    return: Counter {слово: частота}
    """
    return Counter(tokens)
