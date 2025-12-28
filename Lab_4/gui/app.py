import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import font as tkfont
import webbrowser

from core.translator import translate
from core.syntax_visual import TreeDrawer
from core.syntax import build_dependency_tree
from storage.dictionary import load_dict, save_dict
from storage.exporter import save_txt, save_pdf
from storage.examples import load_example


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Машинный перевод: Английский → Французский")
        self.root.geometry("1100x750")
        self.root.configure(bg='#f0f0f0')

        # Современный стиль
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', background='#d0d0d0', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#4a86e8')])

        self.dictionary = load_dict()
        self.result = None

        self._build_menu()
        self._build_status_bar()
        self._build_gui()

    # ---------- МЕНЮ ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root, bg='#e0e0e0', fg='black')
        self.root.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0, bg='#e0e0e0')
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть файл...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить перевод...", command=self.export_txt, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit, accelerator="Ctrl+Q")

        # Меню Словарь
        dict_menu = tk.Menu(menubar, tearoff=0, bg='#e0e0e0')
        menubar.add_cascade(label="Словарь", menu=dict_menu)
        dict_menu.add_command(label="Просмотр словаря", command=self.view_dictionary)
        dict_menu.add_command(label="Добавить слово", command=self.add_word_manually)
        dict_menu.add_command(label="Импорт словаря...", command=self.import_dictionary)
        dict_menu.add_command(label="Экспорт словаря...", command=self.export_dictionary)

        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0, bg='#e0e0e0')
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Руководство", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)

        # Горячие клавиши
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.export_txt())
        self.root.bind('<Control-q>', lambda e: self.root.quit())

    # ---------- СТРОКА СОСТОЯНИЯ ----------
    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#e0e0e0',
            font=('Arial', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # ---------- ОСНОВНОЙ ИНТЕРФЕЙС ----------
    def _build_gui(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#4a86e8', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="Система машинного перевода (Английский → Французский)",
            font=('Arial', 16, 'bold'),
            bg='#4a86e8',
            fg='white'
        )
        title_label.pack(pady=15)

        # Вкладки
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._tab_input()
        self._tab_translation()
        self._tab_frequency()
        self._tab_syntax()
        self._tab_export()

    # ---------- ВКЛАДКА ВВОДА ----------
    def _tab_input(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Ввод текста")

        # Панель кнопок
        control_frame = tk.Frame(tab, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки с иконками (текстовыми)
        buttons = [
            ("Пример CS", lambda: self.load_example("data/examples_cs.txt")),
            ("Пример Lit", lambda: self.load_example("data/examples_lit.txt")),
            ("Открыть файл", self.open_file),
            ("Очистить", lambda: self.input_text.delete("1.0", tk.END)),
            ("Быстрый перевод", self.quick_translate)
        ]

        for text, command in buttons:
            btn = tk.Button(
                control_frame,
                text=text,
                command=command,
                bg='#4a86e8',
                fg='white',
                font=('Arial', 10),
                relief=tk.RAISED,
                bd=2,
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Поле ввода с прокруткой
        input_frame = tk.Frame(tab)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(input_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_text = tk.Text(
            input_frame,
            font=('Courier New', 12),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg='white',
            relief=tk.SUNKEN,
            bd=2
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.input_text.yview)

        # Подсказка
        hint_label = tk.Label(
            tab,
            text="Введите текст на английском или загрузите пример",
            font=('Arial', 9),
            fg='gray',
            bg='#f0f0f0'
        )
        hint_label.pack(pady=5)

        # Кнопка перевода
        translate_btn = tk.Button(
            tab,
            text="Начать перевод",
            command=self.run_translation,
            bg='#2e7d32',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10
        )
        translate_btn.pack(pady=10)

    # ---------- ВКЛАДКА ПЕРЕВОДА ----------
    def _tab_translation(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Перевод")

        # Статистика
        stats_frame = tk.Frame(tab, bg='#e3f2fd', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_label = tk.Label(
            stats_frame,
            text="Всего слов: 0 | Переведено: 0 | Неизвестных: 0",
            font=('Arial', 10),
            bg='#e3f2fd'
        )
        self.stats_label.pack(pady=5)

        # Поле вывода с прокруткой
        output_frame = tk.Frame(tab)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(
            output_frame,
            font=('Courier New', 12),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg='#f8f9fa',
            relief=tk.SUNKEN,
            bd=2
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)

        # Кнопки действий
        action_frame = tk.Frame(tab, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            action_frame,
            text="Копировать перевод",
            command=self.copy_translation,
            bg='#ff9800',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="Проверить неизвестные слова",
            command=self.check_unknown_words,
            bg='#f44336',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

    # ---------- ВКЛАДКА ЧАСТОТНОГО СЛОВАРЯ ----------
    def _tab_frequency(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Частотный словарь")

        # Фильтры
        filter_frame = tk.Frame(tab, bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Сортировать по:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)

        self.sort_var = tk.StringVar(value="frequency")
        ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=["frequency", "word", "pos"],
            state="readonly",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        self.sort_var.trace('w', self.sort_table)

        tk.Button(
            filter_frame,
            text="Экспорт таблицы",
            command=self.export_table
        ).pack(side=tk.RIGHT, padx=5)

        # Таблица с двойной прокруткой
        table_frame = tk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Горизонтальная прокрутка
        h_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Вертикальная прокрутка
        v_scroll = tk.Scrollbar(table_frame)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Таблица
        columns = ("word", "translation", "pos", "pos_desc", "freq")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        headers = [
            ("word", "Слово", 150),
            ("translation", "Перевод", 200),
            ("pos", "POS", 80),
            ("pos_desc", "Расшифровка", 200),
            ("freq", "Частота", 80)
        ]

        for col, text, width in headers:
            self.table.heading(col, text=text)
            self.table.column(col, width=width, anchor=tk.CENTER)

        self.table.pack(fill=tk.BOTH, expand=True)
        v_scroll.config(command=self.table.yview)
        h_scroll.config(command=self.table.xview)

        # Подсказка при наведении
        def show_tooltip(event):
            item = self.table.identify_row(event.y)
            if item:
                values = self.table.item(item)['values']
                tooltip_text = f"Слово: {values[0]}\nПеревод: {values[1]}\nЧасть речи: {values[3]}"
                self.update_status(tooltip_text)

        self.table.bind('<Motion>', show_tooltip)

    # ---------- ВКЛАДКА СИНТАКСИЧЕСКОГО ДЕРЕВА ----------
    def _tab_syntax(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Синтаксическое дерево")

        # Управление
        control_frame = tk.Frame(tab, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(control_frame, text="Предложение №:", bg='#f0f0f0').pack(side=tk.LEFT)

        self.sent_spin = tk.Spinbox(
            control_frame,
            from_=0,
            to=20,
            width=5,
            font=('Arial', 10)
        )
        self.sent_spin.pack(side=tk.LEFT, padx=5)

        tk.Button(
            control_frame,
            text="Построить дерево",
            command=self.show_tree,
            bg='#4caf50',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            control_frame,
            text="Сброс",
            command=self.reset_tree
        ).pack(side=tk.LEFT, padx=5)

        # Холст с прокруткой
        canvas_frame = tk.Frame(tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Прокрутки
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scroll = tk.Scrollbar(canvas_frame)

        # Холст
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            width=900,
            height=500,
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )

        # Размещение
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        # Перетаскивание
        def start_drag(event):
            self.canvas.scan_mark(event.x, event.y)

        def do_drag(event):
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        self.canvas.bind("<ButtonPress-1>", start_drag)
        self.canvas.bind("<B1-Motion>", do_drag)

        # Масштабирование колесиком мыши
        def zoom(event):
            scale = 1.1 if event.delta > 0 else 0.9
            self.canvas.scale("all", event.x, event.y, scale, scale)

        self.canvas.bind("<MouseWheel>", zoom)

        self.drawer = TreeDrawer(self.canvas)

        # Подсказка
        hint_label = tk.Label(
            tab,
            text="Используйте колесико мыши для масштабирования, ЛКМ для перемещения",
            font=('Arial', 9),
            fg='gray'
        )
        hint_label.pack(pady=5)

    # ---------- ВКЛАДКА ЭКСПОРТА ----------
    def _tab_export(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Экспорт")

        # Центральный фрейм
        center_frame = tk.Frame(tab, bg='#f0f0f0')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Кнопки экспорта
        buttons = [
            ("Сохранить как TXT", self.export_txt, "#2196f3"),
            ("Сохранить как PDF", self.export_pdf, "#f44336"),
            ("Экспорт словаря", self.export_dictionary, "#4caf50"),
            ("Печать", self.print_results, "#ff9800")
        ]

        for text, command, color in buttons:
            btn = tk.Button(
                center_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Arial', 11, 'bold'),
                width=25,
                height=2,
                relief=tk.RAISED,
                bd=3
            )
            btn.pack(pady=10)

        # Настройки экспорта
        settings_frame = tk.Frame(tab, bg='#f0f0f0')
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        self.include_table = tk.BooleanVar(value=True)
        self.include_tree = tk.BooleanVar(value=False)

        tk.Checkbutton(
            settings_frame,
            text="Включать частотную таблицу",
            variable=self.include_table,
            bg='#f0f0f0'
        ).pack(anchor=tk.W)

        tk.Checkbutton(
            settings_frame,
            text="Включать синтаксическое дерево",
            variable=self.include_tree,
            bg='#f0f0f0'
        ).pack(anchor=tk.W)

    # ---------- ОСНОВНАЯ ЛОГИКА ----------
    def run_translation(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Внимание", "Введите текст для перевода")
            return

        self.update_status("Идет перевод...")

        try:
            self.result = translate(text, self.dictionary)

            # Перевод
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, self.result["translated_text"])

            # Статистика
            unknown_count = len(self.result["unknown"])
            stats_text = (f"Всего слов: {self.result['total_words']} | "
                          f"Переведено: {self.result['translated_words']} | "
                          f"Неизвестных: {unknown_count}")
            self.stats_label.config(text=stats_text)

            # Таблица
            for i in self.table.get_children():
                self.table.delete(i)

            for w, tr, pos, pos_desc, fr in self.result["table"]:
                self.table.insert("", tk.END, values=(w, tr, pos, pos_desc, fr))

            # Предложения для дерева
            if self.result["doc"]:
                sent_count = len(list(self.result["doc"].sents))
                self.sent_spin.config(to=max(0, sent_count - 1))

            self.update_status("Перевод завершен")

            # Предложение добавить неизвестные слова
            if unknown_count > 0:
                self.tabs.select(1)  # Переключиться на вкладку перевода
                if messagebox.askyesno(
                        "Неизвестные слова",
                        f"Найдено {unknown_count} неизвестных слов. Добавить их в словарь?"
                ):
                    self.add_unknown_words()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при переводе: {str(e)}")
            self.update_status("Ошибка при переводе")

    def quick_translate(self):
        """Быстрый перевод без деталей"""
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return

        self.result = translate(text, self.dictionary)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, self.result["translated_text"])
        self.update_status("Быстрый перевод выполнен")

    def add_unknown_words(self):
        if not self.result or not self.result.get("unknown"):
            return

        for word in self.result["unknown"]:
            pos_tag = "X"
            for token in self.result["doc"]:
                if token.text.lower() == word.lower() and token.is_alpha:
                    pos_tag = token.pos_
                    break

            print(f"Слово: {word}, POS: {pos_tag}")

            # спрашиваем перевод
            tr = simpledialog.askstring("Словарь", f"Перевод для '{word}' ({pos_tag}):")
            if tr:
                self.dictionary[word] = {"translation": tr, "pos": pos_tag}

        # сохраняем словарь
        try:
            save_dict(self.dictionary)
            messagebox.showinfo("Словарь", "Словарь успешно обновлён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить словарь:\n{e}")

    def show_tree(self):
        if not self.result:
            messagebox.showwarning("Внимание", "Сначала выполните перевод")
            return

        try:
            sent_id = int(self.sent_spin.get())
            tree = build_dependency_tree(self.result["doc"], sent_id)
            self.drawer.draw(tree)
            self.update_status(f"Построено дерево для предложения {sent_id}")
        except IndexError:
            messagebox.showerror("Ошибка", "Нет предложения с таким номером")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить дерево: {str(e)}")

    def reset_tree(self):
        self.canvas.delete("all")
        self.sent_spin.delete(0, tk.END)
        self.sent_spin.insert(0, "0")

    def sort_table(self, *args):
        if not self.result:
            return

        sort_by = self.sort_var.get()
        if sort_by == "frequency":
            sorted_table = sorted(self.result["table"], key=lambda x: x[4], reverse=True)
        elif sort_by == "word":
            sorted_table = sorted(self.result["table"], key=lambda x: x[0])
        elif sort_by == "pos":
            sorted_table = sorted(self.result["table"], key=lambda x: x[2])
        else:
            return

        # Обновление таблицы
        for i in self.table.get_children():
            self.table.delete(i)

        for row in sorted_table:
            self.table.insert("", tk.END, values=row)

    # ---------- МЕНЮ ФУНКЦИИ ----------
    def open_file(self):
        filetypes = [("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)

        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()

                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, text)
                self.update_status(f"Загружен файл: {path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def copy_translation(self):
        if self.result:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.result["translated_text"])
            self.update_status("Перевод скопирован в буфер обмена")

    def check_unknown_words(self):
        if self.result and self.result["unknown"]:
            unknown_list = "\n".join(self.result["unknown"])
            messagebox.showinfo(
                "Неизвестные слова",
                f"Следующие слова не найдены в словаре:\n\n{unknown_list}"
            )
        else:
            messagebox.showinfo("Неизвестные слова", "Неизвестные слова отсутствуют")

    def view_dictionary(self):
        dict_window = tk.Toplevel(self.root)
        dict_window.title("Просмотр словаря")
        dict_window.geometry("600x400")

        # Таблица словаря
        columns = ("english", "french")
        tree = ttk.Treeview(dict_window, columns=columns, show="headings")
        tree.heading("english", text="Английский")
        tree.heading("french", text="Французский")

        for word, data in self.dictionary.items():
            tree.insert("", tk.END, values=(word, data["translation"]))

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            dict_window,
            text=f"Всего слов в словаре: {len(self.dictionary)}",
            font=('Arial', 10)
        ).pack(pady=5)

    def add_word_manually(self):
        word = simpledialog.askstring("Добавить слово", "Английское слово:")
        if not word:
            return

        translation = simpledialog.askstring("Добавить слово", "Французский перевод:")
        if translation:
            self.dictionary[word.lower()] = {"translation": translation, "pos": ""}
            save_dict(self.dictionary)
            messagebox.showinfo("Успех", f"Слово '{word}' добавлено в словарь")
            self.update_status(f"Добавлено слово: {word}")

    def import_dictionary(self):
        path = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    import json
                    imported = json.load(f)

                self.dictionary.update(imported)
                save_dict(self.dictionary)
                messagebox.showinfo("Успех", f"Импортировано {len(imported)} слов")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_dictionary(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Текстовые файлы", "*.txt")]
        )
        if path:
            save_dict(self.dictionary)
            messagebox.showinfo("Успех", f"Словарь экспортирован в {path}")

    def export_table(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path and self.result:
            try:
                import csv
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Слово', 'Перевод', 'POS', 'Расшифровка', 'Частота'])
                    for row in self.result["table"]:
                        writer.writerow(row)
                messagebox.showinfo("Успех", f"Таблица экспортирована в {path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

    def print_results(self):
        if not self.result:
            messagebox.showwarning("Внимание", "Нет данных для печати")
            return

        print_text = self._export_text()
        print_window = tk.Toplevel(self.root)
        print_window.title("Печать")
        print_window.geometry("500x400")

        text_widget = tk.Text(print_window, font=('Courier New', 10))
        text_widget.insert(tk.END, print_text)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(
            print_window,
            text="Распечатать",
            command=lambda: self._do_print(print_text)
        ).pack(pady=10)

    def _do_print(self, text):
        messagebox.showinfo("Печать", "Имитация печати - текст готов к выводу")
        # В реальной системе здесь был бы вызов принтера

    def show_help(self):
        help_text = """
        Руководство пользователя:

        1. Введите текст на английском языке во вкладке "Ввод текста"
        2. Нажмите "Начать перевод" для обработки текста
        3. Результаты появятся во вкладке "Перевод"
        4. Во вкладке "Частотный словарь" можно увидеть статистику слов
        5. Во вкладке "Синтаксическое дерево" можно построить дерево разбора
        6. Неизвестные слова можно добавить в словарь
        7. Результаты можно экспортировать во вкладке "Экспорт"

        Горячие клавиши:
        Ctrl+O - Открыть файл
        Ctrl+S - Сохранить перевод
        Ctrl+Q - Выход
        """
        messagebox.showinfo("Руководство пользователя", help_text)

    def show_about(self):
        about_text = """
        Система машинного перевода

        Версия: 1.0
        Направление: Английский → Французский
        Предметная область: 
          • Научные статьи по Computer Science
          • Сочинения по литературе

        Разработано в рамках лабораторной работы
        по дисциплине "Системы искусственного интеллекта"
        """
        messagebox.showinfo("О программе", about_text)

    # ---------- ЭКСПОРТ ----------
    def export_txt(self):
        if not self.result:
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if path:
            export_text = self._export_text()
            save_txt(path, export_text)
            messagebox.showinfo("Успех", f"Файл сохранен: {path}")
            self.update_status(f"Экспорт в TXT: {path}")

    def export_pdf(self):
        if not self.result:
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf")]
        )
        if path:
            export_text = self._export_text()
            save_pdf(path, export_text)
            messagebox.showinfo("Успех", f"PDF файл сохранен: {path}")
            self.update_status(f"Экспорт в PDF: {path}")

    def _export_text(self):
        if not self.result:
            return ""

        lines = [
            "=" * 50,
            "МАШИННЫЙ ПЕРЕВОД: АНГЛИЙСКИЙ → ФРАНЦУЗСКИЙ",
            "=" * 50,
            "\nИСХОДНЫЙ ТЕКСТ:",
            self.input_text.get("1.0", tk.END).strip(),
            "\n" + "=" * 50,
            "\nПЕРЕВОД:",
            self.result["translated_text"],
            "\n" + "=" * 50,
            f"\nСТАТИСТИКА:",
            f"Всего слов: {self.result['total_words']}",
            f"Переведено: {self.result['translated_words']}",
            f"Процент перевода: {self.result['translated_words'] / self.result['total_words'] * 100:.1f}%",
            "\n" + "=" * 50,
        ]

        if self.include_table.get():
            lines.extend([
                "\nЧАСТОТНЫЙ СЛОВАРЬ:",
                "-" * 80
            ])
            for w, tr, pos, pos_desc, fr in self.result["table"]:
                lines.append(f"{w:20} → {tr:20} | {pos:5} ({pos_desc:15}) | {fr:3}")

        return "\n".join(lines)

    def load_example(self, path):
        try:
            text = load_example(path)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, text)
            self.update_status(f"Загружен пример из {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пример: {str(e)}")