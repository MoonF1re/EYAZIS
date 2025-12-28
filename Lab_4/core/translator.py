import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

POS_DESC = {
    "NOUN": "Существительное",
    "PROPN": "Имя собственное",
    "VERB": "Глагол",
    "AUX": "Вспомогательный глагол",
    "ADJ": "Прилагательное",
    "ADV": "Наречие",
    "PRON": "Местоимение",
    "DET": "Артикль / определитель",
    "ADP": "Предлог",
    "CCONJ": "Сочинительный союз",
    "SCONJ": "Подчинительный союз",
    "NUM": "Числительное",
    "PART": "Частица",
    "INTJ": "Междометие",
    "SYM": "Символ",
    "X": "Прочее",
    "PUNCT": "Знак препинания"
}


def translate(text, dictionary):
    doc = nlp(text)

    tokens = [t for t in doc if t.is_alpha]
    words = [t.text.lower() for t in tokens]
    freq = Counter(words)

    translated = []
    translated_count = 0
    unknown = set()

    # ---- перевод текста ----
    for token in doc:
        if token.is_alpha:
            w = token.text.lower()
            if w in dictionary:
                translated.append(dictionary[w]["translation"])
                translated_count += 1
            else:
                translated.append(f"[{w}]")
                unknown.add(w)
        else:
            translated.append(token.text)

    # ---- ЧАСТОТНЫЙ СЛОВАРЬ (БЕЗ ПОВТОРОВ) ----
    table = []
    for word, count in freq.items():
        pos_tag = nlp(word)[0].pos_
        pos_desc = POS_DESC.get(pos_tag, "Неизвестно")

        translation = dictionary.get(word, {}).get("translation", f"[{word}]")

        table.append(
            (word, translation, pos_tag, pos_desc, count)
        )

    table.sort(key=lambda x: x[4], reverse=True)

    return {
        "translated_text": " ".join(translated),
        "total_words": len(words),
        "translated_words": translated_count,
        "table": table,
        "doc": doc,
        "unknown": unknown
    }
