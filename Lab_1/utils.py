import re

STOP_WORDS = {
    "the", "a", "an", "and", "or", "is", "are", "to", "of", "in", "on", "for", "with", "by"
}

def tokenize(text: str):
    """Токенизация текста: нижний регистр + удаление стоп-слов"""
    text = text.lower()
    words = re.findall(r"[a-z]+", text)
    return [w for w in words if w not in STOP_WORDS]
