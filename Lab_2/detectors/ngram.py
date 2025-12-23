import json
from collections import Counter

N = 5
TOP_K = 300

def get_ngrams(text):
    return [text[i:i+N] for i in range(len(text)-N+1)]

def build_profile(texts):
    counter = Counter()
    for text in texts:
        counter.update(get_ngrams(text))
    return dict(counter.most_common(TOP_K))

def save_profile(profile, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False)

def load_profile(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def oop_distance(lang_profile, text_profile):
    distance = 0
    max_penalty = len(lang_profile)
    for i, gram in enumerate(text_profile):
        distance += abs(i - lang_profile.get(gram, max_penalty))
    return distance

def detect_ngram(text, fr_profile, de_profile):
    text_profile = list(build_profile([text]).keys())
    fr_dist = oop_distance(fr_profile, text_profile)
    de_dist = oop_distance(de_profile, text_profile)
    return "French" if fr_dist < de_dist else "German"
