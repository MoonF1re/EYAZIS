import requests
from bs4 import BeautifulSoup
import PyPDF2
import docx
import re


class DocumentLoader:
    """Класс для загрузки и предобработки документов"""

    @staticmethod
    def load_from_file(file_path):
        """Загрузка текста из файла"""
        ext = file_path.lower().split('.')[-1]

        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == 'pdf':
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text

        elif ext == 'docx':
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")

    @staticmethod
    def load_from_url(url):
        """Загрузка и очистка текста с веб-страницы, особенно для Wikipedia"""
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. УДАЛЯЕМ ВСЁ ЛИШНЕЕ (скрипты, стили, навигация, шапка, футер)
        for element in soup(['script', 'style', 'nav', 'footer', 'header',
                             'table', 'ul', 'ol',  # Часто списки - это навигация
                             'div#mw-navigation', 'div#footer',  # Специфично для MediaWiki (движок Вики)
                             'div.mw-jump-link', 'div.vector-header-container']):
            if element:
                element.decompose()

        # 2. ПЫТАЕМСЯ НАЙТИ ОСНОВНОЙ КОНТЕНТ СТАТЬИ
        #    У Википедии основной текст обычно в div#bodyContent или div#mw-content-text
        main_content = None
        for selector in ['div#bodyContent', 'div#mw-content-text', 'main', 'article']:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # Если не нашли по селекторам, берём весь soup
        if not main_content:
            main_content = soup

        # 3. ИЗВЛЕКАЕМ ТЕКСТ, но теперь только из найденного блока
        text = main_content.get_text(separator=' ', strip=True)

        # 4. УСИЛЕННАЯ ОЧИСТКА ПОЛУЧЕННОГО ТЕКСТА
        lines = []
        for line in text.splitlines():
            clean_line = line.strip()
            # Отбрасываем строки, которые являются типичным "мусором":
            # - Очень короткие (менее 2 символов)
            # - Содержат только цифры и пунктуацию (например, "[1]")
            # - Явно служебные слова (навигация)
            if (len(clean_line) > 20 and  # Берём только достаточно длинные строки
                    not re.match(r'^[\d\s\[\]\(\)]*$', clean_line) and  # Не только цифры/скобки
                    not any(word in clean_line.lower() for word in ['springen', 'navigation', 'benutzerkonto',
                                                                    'lesen', 'bearbeiten', 'quelltext',
                                                                    'ansehen', 'hauptmenü'])):
                lines.append(clean_line)

        # 5. Склеиваем обратно в единый текст
        clean_text = ' '.join(lines)

        # 6. Дополнительно: объединяем разорванные слова, убираем лишние пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text)  # Множественные пробелы -> один
        clean_text = re.sub(r'\s([.,!?;:])', r'\1', clean_text)  # Убираем пробел перед знаками препинания

        # Ограничиваем размер на случай очень больших статей
        return clean_text[:100000]

    @staticmethod
    def preprocess_text(text, language='auto'):
        """Предобработка текста"""
        # Удаляем лишние пробелы и переносы
        text = re.sub(r'\s+', ' ', text)

        # Определяем язык
        if language == 'auto':
            text_lower = text.lower()
            fr_words = ['le', 'la', 'les', 'de', 'des', 'du']
            de_words = ['der', 'die', 'das', 'und', 'ist', 'in']

            fr_count = sum(text_lower.count(word) for word in fr_words)
            de_count = sum(text_lower.count(word) for word in de_words)

            language = 'french' if fr_count > de_count else 'german'

        return text, language
