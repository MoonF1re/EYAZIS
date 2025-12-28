import tkinter as tk
from gui.app import TranslatorApp

def main():

    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
