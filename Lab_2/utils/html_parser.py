from bs4 import BeautifulSoup

def extract_text_from_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup.get_text().lower()
