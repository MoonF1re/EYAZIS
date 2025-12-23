import re
import math
from collections import Counter, defaultdict


class SentenceExtractionSummarizer:
    """Классический алгоритм извлечения предложений"""

    def __init__(self):
        self.documents = []
        self.db_size = 0
        self.term_doc_freq = defaultdict(int)

    def detect_language(self, text):
        """Определение языка текста"""
        text_lower = text.lower()

        french_stopwords = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est'}
        german_stopwords = {'der', 'die', 'das', 'und', 'ist', 'in', 'zu', 'den'}

        fr_count = sum(1 for w in french_stopwords if w in text_lower)
        de_count = sum(1 for w in german_stopwords if w in text_lower)

        return 'french' if fr_count > de_count else 'german'

    def tokenize_sentences(self, text, language):
        """Токенизация текста на предложения"""
        # Простая токенизация по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # Удаляем короткие предложения (менее 3 слов)
        sentences = [s for s in sentences if len(s.split()) >= 3]

        return sentences

    def tokenize_words(self, sentence, language):
        """Токенизация предложения на слова"""
        # Удаляем знаки препинания и приводим к нижнему регистру
        sentence_lower = sentence.lower()
        sentence_clean = re.sub(r'[^\w\s\.\?!]', ' ', sentence_lower)
        words = sentence_clean.split()

        # Список стоп-слов для французского и немецкого
        stopwords_fr = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est', 'dans', 'pour'}
        stopwords_de = {'der', 'die', 'das', 'und', 'ist', 'in', 'zu', 'den', 'von', 'mit'}

        stopwords = stopwords_fr if language == 'french' else stopwords_de

        # Фильтруем стоп-слова и короткие слова
        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]

        return filtered_words

    def compute_tfidf(self, documents):
        """Вычисление TF-IDF весов для терминов"""
        term_weights = {}

        for doc_id, doc_info in enumerate(documents):
            all_terms = []
            for sentence_words in doc_info['sentences_words']:
                all_terms.extend(sentence_words)

            term_freq = Counter(all_terms)
            max_freq = max(term_freq.values()) if term_freq else 1

            for term, tf in term_freq.items():
                # Формула из задания: w(t, D) = 0.5 * (1 + tf(t, D)/tf_max(D)) * log(DB/df(t))
                idf = math.log(self.db_size / (self.term_doc_freq.get(term, 1) + 1))
                tf_norm = tf / max_freq
                term_weights[term] = 0.5 * (1 + tf_norm) * idf

        return term_weights

    def compute_sentence_score(self, sentence_words, term_weights, position, total_length):
        """Вычисление веса предложения"""
        # TF-IDF часть
        tfidf_score = sum(term_weights.get(word, 0) for word in sentence_words)

        # Позиционная часть (упрощенная)
        position_score = 1 - (position / total_length) if total_length > 0 else 0.5

        # Комбинированный вес
        return tfidf_score * 0.8 + position_score * 0.2

    def generate_summary(self, text, num_sentences=10):
        """Генерация классического реферата"""
        # Определяем язык
        language = self.detect_language(text)

        # Токенизация предложений
        sentences = self.tokenize_sentences(text, language)

        # Токенизация слов в каждом предложении
        sentences_words = []
        for sent in sentences:
            words = self.tokenize_words(sent, language)
            sentences_words.append(words)

        # Добавляем документ в коллекцию
        doc_info = {
            'sentences': sentences,
            'sentences_words': sentences_words,
            'language': language
        }

        self.documents.append(doc_info)
        self.db_size = len(self.documents)

        # Обновляем частоту документов для терминов
        for sentence_words in sentences_words:
            for term in set(sentence_words):
                self.term_doc_freq[term] += 1

        # Вычисляем веса терминов
        term_weights = self.compute_tfidf([doc_info])

        # Вычисляем веса предложений
        sentence_scores = []
        for i, (sent, words) in enumerate(zip(sentences, sentences_words)):
            score = self.compute_sentence_score(words, term_weights, i, len(sentences))
            sentence_scores.append((i, sent, score))

        # Сортируем по весу и выбираем топ-N
        top_sentences = sorted(sentence_scores, key=lambda x: x[2], reverse=True)[:num_sentences]

        # Восстанавливаем исходный порядок
        top_sentences.sort(key=lambda x: x[0])

        # Формируем реферат
        summary = ' '.join([sent for _, sent, _ in top_sentences])

        # Извлекаем ключевые слова
        keywords = self.extract_keywords(term_weights)

        return {
            'summary': summary,
            'keywords': keywords,
            'language': language,
            'algorithm': 'sentence_extraction'
        }

    def extract_keywords(self, term_weights, num_keywords=15):
        """Извлечение ключевых слов"""
        sorted_terms = sorted(term_weights.items(), key=lambda x: x[1], reverse=True)
        return [term for term, score in sorted_terms[:num_keywords]]