import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os

from project_objects import ProjectObjects
from document_loader import DocumentLoader


class SummarizerGUI:
    """Графический интерфейс системы реферирования"""

    def __init__(self):
        self.doc_loader = DocumentLoader()
        self.project_objects = ProjectObjects(use_neural=True)
        self.current_text = ""

        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("Система автоматического реферирования - Вариант 11")
        self.root.geometry("1000x700")

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            title_frame,
            text="Система автоматического реферирования документов",
            font=('Arial', 14, 'bold')
        ).pack()

        ttk.Label(
            title_frame,
            text="Вариант 11: Французский 🇫🇷 | Немецкий 🇩🇪 | Медицина 🏥 | Искусство 🎨",
            font=('Arial', 10)
        ).pack(pady=5)

        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки загрузки
        ttk.Button(control_frame, text="Загрузить файл",
                   command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Загрузить URL",
                   command=self.load_url).pack(side=tk.LEFT, padx=2)

        # Выбор алгоритма
        self.algorithm_var = tk.StringVar(value="both")
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(algo_frame, text="Алгоритм:").pack(side=tk.LEFT)
        ttk.Radiobutton(algo_frame, text="Оба", variable=self.algorithm_var,
                        value="both").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(algo_frame, text="Sentence Extraction", variable=self.algorithm_var,
                        value="sentence_extraction").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(algo_frame, text="Нейросеть", variable=self.algorithm_var,
                        value="neural").pack(side=tk.LEFT, padx=5)

        # Область с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Вкладка 1: Исходный текст
        source_tab = ttk.Frame(notebook)
        notebook.add(source_tab, text="Исходный документ")

        self.source_text = scrolledtext.ScrolledText(
            source_tab,
            wrap=tk.WORD,
            font=('Courier', 10)
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Вкладка 2: Результаты
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="Результаты")

        # Панель для двух колонок
        results_panel = ttk.Frame(results_tab)
        results_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая колонка - Sentence Extraction
        se_frame = ttk.LabelFrame(results_panel, text="Sentence Extraction")
        se_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)

        ttk.Label(se_frame, text="Классический реферат:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=(5, 0))

        self.se_summary = scrolledtext.ScrolledText(
            se_frame,
            wrap=tk.WORD,
            height=8
        )
        self.se_summary.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(se_frame, text="Ключевые слова:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5)

        self.se_keywords = scrolledtext.ScrolledText(
            se_frame,
            wrap=tk.WORD,
            height=4
        )
        self.se_keywords.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Правая колонка - Нейросеть
        nn_frame = ttk.LabelFrame(results_panel, text="Нейросетевой подход")
        nn_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)

        ttk.Label(nn_frame, text="Классический реферат:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=(5, 0))

        self.nn_summary = scrolledtext.ScrolledText(
            nn_frame,
            wrap=tk.WORD,
            height=8
        )
        self.nn_summary.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(nn_frame, text="Ключевые слова:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5)

        self.nn_keywords = scrolledtext.ScrolledText(
            nn_frame,
            wrap=tk.WORD,
            height=4
        )
        self.nn_keywords.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Нижняя панель
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(bottom_frame, text="Сгенерировать реферат",
                   command=self.generate_summary).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_frame, text="Сохранить результаты",
                   command=self.save_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_frame, text="Очистить",
                   command=self.clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_frame, text="Справка",
                   command=self.show_help).pack(side=tk.LEFT, padx=2)

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

    def load_file(self):
        """Загрузка файла"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("PDF файлы", "*.pdf"),
                ("Word документы", "*.docx"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                text = self.doc_loader.load_from_file(file_path)
                self.current_text = text
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, text)
                self.status_var.set(f"Загружен файл: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_url(self):
        """Загрузка URL"""
        import tkinter.simpledialog as sd

        url = sd.askstring("Загрузка URL", "Введите URL документа:")
        if url:
            try:
                text = self.doc_loader.load_from_url(url)
                self.current_text = text
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, text)
                self.status_var.set(f"Загружено с URL: {url[:50]}...")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить URL: {str(e)}")

    def generate_summary(self):
        """Генерация реферата"""
        if not self.current_text:
            messagebox.showwarning("Предупреждение", "Сначала загрузите документ")
            return

        try:
            self.status_var.set("Обработка документа...")
            self.root.update()

            # Обрабатываем документ
            results = self.project_objects.process_document(
                self.current_text,
                self.algorithm_var.get()
            )

            # Отображаем результаты
            if 'sentence_extraction' in results:
                se_result = results['sentence_extraction']
                self.se_summary.delete(1.0, tk.END)
                self.se_summary.insert(1.0, se_result.get('summary', ''))

                self.se_keywords.delete(1.0, tk.END)
                keywords = se_result.get('keywords', [])
                self.se_keywords.insert(1.0, ', '.join(keywords))

            if 'neural' in results:
                nn_result = results['neural']
                self.nn_summary.delete(1.0, tk.END)
                self.nn_summary.insert(1.0, nn_result.get('summary', ''))

                self.nn_keywords.delete(1.0, tk.END)
                keywords = nn_result.get('keywords', [])
                self.nn_keywords.insert(1.0, ', '.join(keywords))

            self.status_var.set("Реферат успешно сгенерирован")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации: {str(e)}")
            self.status_var.set("Ошибка генерации")

    def save_results(self):
        """Сохранение результатов"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Текстовые файлы", "*.txt")]
        )

        if file_path:
            try:
                # Собираем данные
                data = {
                    "original_text": self.current_text[:1000] + "...",
                    "algorithm_used": self.algorithm_var.get(),
                    "results": {}
                }

                if self.se_summary.get(1.0, tk.END).strip():
                    data["results"]["sentence_extraction"] = {
                        "summary": self.se_summary.get(1.0, tk.END).strip(),
                        "keywords": self.se_keywords.get(1.0, tk.END).strip()
                    }

                if self.nn_summary.get(1.0, tk.END).strip():
                    data["results"]["neural_network"] = {
                        "summary": self.nn_summary.get(1.0, tk.END).strip(),
                        "keywords": self.nn_keywords.get(1.0, tk.END).strip()
                    }

                # Сохраняем
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.status_var.set(f"Результаты сохранены в {os.path.basename(file_path)}")
                messagebox.showinfo("Успех", "Результаты успешно сохранены")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def show_help(self):
        """Показать справку"""
        help_text = """
        СИСТЕМА АВТОМАТИЧЕСКОГО РЕФЕРИРОВАНИЯ

        Инструкция:
        1. Загрузите документ (файл или URL)
        2. Выберите алгоритм:
           - Sentence Extraction: классический алгоритм
           - Нейросеть: нейросетевой подход
           - Оба: сравнение двух алгоритмов
        3. Нажмите 'Сгенерировать реферат'
        4. Сохраните результаты при необходимости

        Требования к документам:
        - Поддерживаются форматы: TXT, PDF, DOCX
        - Поддерживаемые языки: французский, немецкий
        - Предметные области: медицина, критика искусства

        Рекомендации:
        - Оптимальный размер: 5-10 страниц А4

        Вариант 11: Французский 🇫🇷 | Немецкий 🇩🇪
        """

        messagebox.showinfo("Справка", help_text)

    def clear_all(self):
        """Очистить все поля"""
        self.current_text = ""
        self.source_text.delete(1.0, tk.END)
        self.se_summary.delete(1.0, tk.END)
        self.se_keywords.delete(1.0, tk.END)
        self.nn_summary.delete(1.0, tk.END)
        self.nn_keywords.delete(1.0, tk.END)
        self.status_var.set("Готов к работе")

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    print("=" * 60)
    print("СИСТЕМА АВТОМАТИЧЕСКОГО РЕФЕРИРОВАНИЯ")
    print("=" * 60)

    # Запускаем GUI
    app = SummarizerGUI()
    app.run()


if __name__ == "__main__":
    main()