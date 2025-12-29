import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3


class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: Синтез речи (CS/German)")
        self.root.geometry("620x550")

        # Список для хранения данных о голосах
        self.available_voices = []
        self.get_system_voices()

        self.create_widgets()

    def get_system_voices(self):
        """Получаем список голосов один раз при запуске"""
        temp_engine = pyttsx3.init()
        voices = temp_engine.getProperty('voices')
        for voice in voices:
            if "german" in voice.name.lower() or "deu" in voice.id.lower():
                self.available_voices.append({
                    'id': voice.id,
                    'name': f"Deutsch: {voice.name}"
                })

        # Если немецких нет, берем все доступные
        if not self.available_voices:
            for voice in voices:
                self.available_voices.append({'id': voice.id, 'name': voice.name})

        del temp_engine

    def create_widgets(self):
        # Заголовок
        tk.Label(self.root, text="Синтез речи: Научные статьи (Computer Science)",
                 font=("Arial", 11, "bold")).pack(pady=10)

        # Текстовое поле
        self.txt_input = scrolledtext.ScrolledText(self.root, width=70, height=10, font=("Verdana", 10))
        self.txt_input.pack(pady=5, padx=15)

        # Пример текста на немецком
        sample = ("Verteilte Systeme bestehen aus mehreren autonomen Computern, "
                  "die über ein Netzwerk miteinander kommunizieren. In einer "
                  "Microservices-Architektur wird eine Anwendung in kleine, "
                  "unabhängige Dienste aufgeteilt, die über definierte Schnittstellen wie REST oder "
                  "gRPC interagieren. "
                  "Dies verbessert die Skalierbarkeit und Fehlertoleranz des Gesamtsystems erheblich.")
        self.txt_input.insert(tk.END, sample)

        # Фрейм настроек
        settings_frame = tk.LabelFrame(self.root, text="Настройки голоса")
        settings_frame.pack(pady=10, padx=15, fill="x")

        # 1. Выбор голоса
        tk.Label(settings_frame, text="Голос:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.voice_combo = ttk.Combobox(settings_frame, state="readonly", width=50)
        self.voice_combo['values'] = [v['name'] for v in self.available_voices]
        if self.available_voices:
            self.voice_combo.current(0)
        self.voice_combo.grid(row=0, column=1, padx=5, pady=5)

        # 2. Ползунок Темпа (Rate)
        tk.Label(settings_frame, text="Темп:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rate_slider = tk.Scale(settings_frame, from_=50, to=300, orient=tk.HORIZONTAL)
        self.rate_slider.set(175)
        self.rate_slider.grid(row=1, column=1, sticky="we")

        # 3. Ползунок Громкости (Volume)
        tk.Label(settings_frame, text="Громкость:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.volume_slider = tk.Scale(settings_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_slider.set(80)  # По умолчанию 80%
        self.volume_slider.grid(row=2, column=1, sticky="we")

        # Кнопка воспроизведения
        self.btn_speak = tk.Button(self.root, text="▶ Воспроизвести",
                                   command=self.speak_text,
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 11, "bold"), height=2)
        self.btn_speak.pack(pady=15, fill="x", padx=100)

    def speak_text(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Внимание", "Введите текст для чтения")
            return

        # Блокируем кнопку
        self.btn_speak.config(state=tk.DISABLED, text="Читаю...")
        self.root.update()

        try:
            # Инициализация нового экземпляра
            engine = pyttsx3.init()

            # Применяем выбранный голос
            selected_idx = self.voice_combo.current()
            voice_id = self.available_voices[selected_idx]['id']
            engine.setProperty('voice', voice_id)

            # Применяем темп
            engine.setProperty('rate', self.rate_slider.get())

            # Применяем громкость (переводим из 0-100 в 0.0-1.0)
            volume_level = self.volume_slider.get() / 100
            engine.setProperty('volume', volume_level)

            # Синтез
            engine.say(text)
            engine.runAndWait()

            # Очистка
            engine.stop()
            del engine

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка воспроизведения: {e}")

        finally:
            # Разблокируем кнопку
            self.btn_speak.config(state=tk.NORMAL, text="▶ Воспроизвести")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()