import requests
import json
import re
from collections import Counter


class NeuralSummarizer:
    """Суммаризатор на основе локальной модели Ollama"""

    def __init__(self, model_name="llama3.2", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.available = self.check_ollama()

    def check_ollama(self):
        """Проверка, запущен ли Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            print("Ollama не запущена. Запустите Ollama перед использованием нейросети.")
            return False

    def summarize(self, text, max_length=150):
        """Суммаризация текста через Ollama API"""
        if not self.available:
            return None

        try:
            # Ограничиваем длину текста для промпта
            text_truncated = text[:3000]

            # Формируем промпт для суммаризации на нужном языке
            prompt = f"""
            Создай краткий реферат следующего текста.
            Реферат должен содержать 5-10 ключевых предложений, передающих основную суть.

            Текст:
            {text_truncated}

            Реферат:
            """

            # Отправляем запрос к Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_length,
                        "temperature": 0.3
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"Ошибка Ollama: {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка при запросе к Ollama: {e}")
            return None

    def extract_keywords(self, text, num_keywords=10):
        """Извлечение ключевых слов через Ollama"""
        if not self.available:
            return self.extract_keywords_fallback(text, num_keywords)

        try:
            # Промпт для извлечения ключевых слов
            prompt = f"""
            Extract {num_keywords} of the most important keywords from the following text. Return only comma-separated words (,). No explanation.

            Text:
            {text[:2000]}

            Key words:
            """

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 100,
                        "temperature": 0.1
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                keywords_text = result.get("response", "").strip()
                # Очищаем результат
                keywords = [k.strip() for k in keywords_text.split(',')]
                return keywords[:num_keywords]
            else:
                return self.extract_keywords_fallback(text, num_keywords)

        except:
            return self.extract_keywords_fallback(text, num_keywords)

    def extract_keywords_fallback(self, text, num_keywords=10):
        """Резервный метод извлечения ключевых слов"""
        words = re.findall(r'\b[a-zA-ZÀ-Üà-ü]{4,}\b', text.lower())
        stopwords = {'this', 'that', 'with', 'from', 'have', 'has', 'was', 'were'}
        filtered = [w for w in words if w not in stopwords]
        word_counts = Counter(filtered)
        return [word for word, count in word_counts.most_common(num_keywords)]

# Фолбэк-реализация
class SimpleSummarizer:
    @staticmethod
    def summarize(text, num_sentences=3):
        """Простая суммаризация - первые N предложений"""
        import re

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        return ' '.join(sentences[:num_sentences])

    @staticmethod
    def extract_keywords(text, num_keywords=10):
        """Простое извлечение ключевых слов"""
        import re
        from collections import Counter

        words = re.findall(r'\b[a-zA-ZÀ-Üà-ü]{4,}\b', text.lower())
        stopwords = {'this', 'that', 'with', 'from', 'have', 'has', 'was', 'were'}

        filtered = [w for w in words if w not in stopwords]
        word_counts = Counter(filtered)

        return [word for word, count in word_counts.most_common(num_keywords)]