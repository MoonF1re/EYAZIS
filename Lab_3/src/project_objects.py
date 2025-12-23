from sentence_extraction import SentenceExtractionSummarizer
from neural_summarizer import NeuralSummarizer, SimpleSummarizer


class ProjectObjects:
    """Класс для управления объектами проекта"""

    def __init__(self, use_neural=True):
        self.use_neural = use_neural
        self.sentence_extractor = SentenceExtractionSummarizer()
        self.simple_summarizer = SimpleSummarizer()

        if use_neural:
            try:
                self.neural_summarizer = NeuralSummarizer(use_gpu=False)
            except:
                self.neural_summarizer = None
                self.use_neural = False

        if use_neural:
            try:
                self.neural_summarizer = NeuralSummarizer(model_name="llama3.2")
                if not self.neural_summarizer.available:
                    print("Ollama не доступен, нейросеть отключена")
                    self.neural_summarizer = None
                    self.use_neural = False
            except Exception as e:
                print(f"Ошибка инициализации нейросети: {e}")
                self.neural_summarizer = None
                self.use_neural = False

    def process_document(self, text, algorithm='both'):
        """
        Обработка документа выбранным алгоритмом

        Args:
            text: Текст для обработки
            algorithm: 'sentence_extraction', 'neural', или 'both'

        Returns:
            Словарь с результатами
        """
        results = {}

        # Обработка алгоритмом извлечения предложений
        if algorithm in ['sentence_extraction', 'both']:
            try:
                se_result = self.sentence_extractor.generate_summary(text)
                results['sentence_extraction'] = se_result
            except Exception as e:
                results['sentence_extraction'] = {'error': str(e)}

        # Обработка нейросетевым алгоритмом
        if algorithm in ['neural', 'both'] and self.use_neural and self.neural_summarizer:
            try:
                neural_summary = self.neural_summarizer.summarize(text)
                neural_keywords = self.neural_summarizer.extract_keywords(text)

                if neural_summary:
                    results['neural'] = {
                        'summary': neural_summary,
                        'keywords': neural_keywords,
                        'algorithm': 'neural'
                    }
            except Exception as e:
                results['neural'] = {'error': str(e)}

        # Если нейросеть недоступна, используем простой метод
        elif algorithm in ['neural', 'both']:
            simple_summary = self.simple_summarizer.summarize(text)
            simple_keywords = self.simple_summarizer.extract_keywords(text)

            results['neural'] = {
                'summary': simple_summary,
                'keywords': simple_keywords,
                'algorithm': 'simple_fallback'
            }

        return results