import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import threading


class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASR System: Computer Science (DE)")
        self.root.geometry("700x550")

        self.recognizer = sr.Recognizer()

        # Попытка инициализации микрофона
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Микрофон не найден: {e}")
            self.microphone = None

        self.is_listening = False
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Распознавание речи: Научные статьи (DE)",
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Окно вывода
        self.text_area = scrolledtext.ScrolledText(self.root, width=80, height=15, font=("Verdana", 11))
        self.text_area.pack(pady=10, padx=20)

        # Статус
        self.status_label = tk.Label(self.root, text="Статус: Готов", fg="blue")
        self.status_label.pack(pady=5)

        # Кнопка
        self.btn_toggle = tk.Button(self.root, text="🎤 Начать запись", command=self.toggle_capture,
                                    bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2, width=25)
        self.btn_toggle.pack(pady=15)

    def toggle_capture(self):
        if self.microphone is None:
            messagebox.showerror("Ошибка", "Микрофон недоступен")
            return

        if not self.is_listening:
            self.is_listening = True
            self.btn_toggle.config(text="🛑 Остановить запись", bg="#f44336")
            self.status_label.config(text="Статус: Слушаю...", fg="red")
            threading.Thread(target=self.listen_process, daemon=True).start()
        else:
            self.is_listening = False
            self.btn_toggle.config(text="🎤 Начать запись", bg="#4CAF50")
            self.status_label.config(text="Статус: Остановлено", fg="blue")

    def listen_process(self):
        """Процесс распознавания в отдельном потоке"""
        with self.microphone as source:
            # Калибровка под шум (улучшает точность для научных текстов)
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_listening:
                try:
                    # Захват фразы
                    audio = self.recognizer.listen(source, phrase_time_limit=10)

                    # Используем getattr, чтобы IDE не подсвечивала 'recognize_google' желтым
                    recognize_func = getattr(self.recognizer, 'recognize_google')
                    text = recognize_func(audio, language="de-DE")

                    self.update_text(text)

                except (sr.UnknownValueError, AttributeError):
                    # Если речь не распознана или метод не найден
                    continue
                except sr.RequestError as e:
                    self.update_text(f"\n[Ошибка сети: {e}]\n")
                    break
                except Exception as e:
                    print(f"Критическая ошибка: {e}")
                    break

    def update_text(self, new_text):
        """Обновление GUI"""
        self.text_area.insert(tk.END, f"{new_text.capitalize()}. ")
        self.text_area.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()