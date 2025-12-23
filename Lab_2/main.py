import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

from utils.html_parser import extract_text_from_html
from detectors.alphabetic import detect_alphabetic
from detectors.ngram import detect_ngram, load_profile
from detectors.neural import detect_neural
from utils.io import save_to_file
from utils.statistics import build_statistics


class LanguageDetectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Language Detector")
        self.geometry("900x500")

        self.fr_profile = load_profile("profiles/fr_ngrams.json")
        self.de_profile = load_profile("profiles/de_ngrams.json")

        self.results = []

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Button(frame, text="Выбрать HTML файлы", command=self.open_files).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Сохранить результат", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Help", command=self.show_help).pack(side=tk.LEFT, padx=5)

        columns = ("file", "alphabetic", "ngram", "neural")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("file", text="Файл")
        self.tree.heading("alphabetic", text="Алфавитный")
        self.tree.heading("ngram", text="N-грамм")
        self.tree.heading("neural", text="Нейросеть")

        self.tree.pack(expand=True, fill=tk.BOTH)

    def open_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("HTML files", "*.html")])

        for path in paths:
            text = extract_text_from_html(path)

            result = {
                "file": os.path.basename(path),
                "alphabetic": detect_alphabetic(text),
                "ngram": detect_ngram(text, self.fr_profile, self.de_profile),
                "neural": "Processing..."
            }

            self.results.append(result)

            row_id = self.tree.insert("", tk.END, values=tuple(result.values()))

            threading.Thread(
                target=self.run_neural,
                args=(text, row_id),
                daemon=True
            ).start()

    def run_neural(self, text, row_id):
        lang = detect_neural(text)

        # Обновляем интерфейс безопасно
        self.after(0, self.update_neural_result, row_id, lang)

    def update_neural_result(self, row_id, lang):
        values = list(self.tree.item(row_id, "values"))
        values[3] = lang
        self.tree.item(row_id, values=values)

        for r in self.results:
            if r["file"] == values[0]:
                r["neural"] = lang

    def save(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json")]
        )

        if not path:
            return

        if not path.lower().endswith(".json"):
            path += ".json"

        save_to_file(self.results, path)

        messagebox.showinfo(
            "Сохранено",
            "Результаты анализа успешно сохранены в формате JSON."
        )

    def show_help(self):
        messagebox.showinfo(
            "Справка",
            "Назначение программы:\n"
            "Программа предназначена для автоматического определения языка "
            "HTML-документов.\n\n"

            "Поддерживаемые языки:\n"
            "• Французский\n"
            "• Немецкий\n\n"

            "Используемые методы:\n"
            "1. Алфавитный — анализ национальных символов алфавита.\n"
            "2. N-граммный — сравнение частот символных 5-грамм.\n"
            "3. Нейросетевой — использование языковой модели Ollama.\n\n"

            "Порядок работы:\n"
            "1. Выберите один или несколько HTML-файлов.\n"
            "2. Дождитесь завершения анализа.\n"
            "3. Сохраните результаты в файл."
        )


if __name__ == "__main__":
    app = LanguageDetectorApp()
    app.mainloop()
