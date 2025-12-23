import os
import json
from collections import Counter
from utils.html_parser import extract_text_from_html

N = 5
TOP_K = 300


def get_ngrams(text, n=N):
    return [text[i:i+n] for i in range(len(text) - n + 1)]


def build_language_profile(folder_path):
    counter = Counter()

    for file in os.listdir(folder_path):
        if file.endswith(".html"):
            full_path = os.path.join(folder_path, file)
            text = extract_text_from_html(full_path)
            ngrams = get_ngrams(text)
            counter.update(ngrams)

    # превращаем в профиль "грамма → позиция"
    most_common = counter.most_common(TOP_K)
    profile = {gram: idx for idx, (gram, _) in enumerate(most_common)}
    return profile


def save_profile(profile, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)


def main():
    print("Обучение N-граммных профилей...")

    fr_profile = build_language_profile("data/train/fr")
    de_profile = build_language_profile("data/train/de")

    os.makedirs("profiles", exist_ok=True)

    save_profile(fr_profile, "profiles/fr_ngrams.json")
    save_profile(de_profile, "profiles/de_ngrams.json")

    print("Готово!")
    print("Созданы файлы:")
    print(" - profiles/fr_ngrams.json")
    print(" - profiles/de_ngrams.json")


if __name__ == "__main__":
    main()
