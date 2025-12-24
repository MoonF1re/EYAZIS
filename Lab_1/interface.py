import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from file_loader import load_documents_from_folder
from search import Search



class SearchGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Information Retrieval System")
        self.root.geometry("900x650")

        self.folder_label = tk.Label(self.root, text="Documents folder:")
        self.folder_label.pack()
        self.folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.folder_button.pack()

        self.query_label = tk.Label(self.root, text="Enter search query:")
        self.query_label.pack()
        self.query_entry = tk.Entry(self.root, width=80)
        self.query_entry.pack()
        self.search_button = tk.Button(self.root, text="Search", command=self.perform_search)
        self.search_button.pack()

        self.results_box = scrolledtext.ScrolledText(self.root, width=100, height=20)
        self.results_box.pack()

        # Для хранения всех запросов и результатов
        self.query_results = {}

        self.root.mainloop()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            try:
                count = load_documents_from_folder(folder)
                messagebox.showinfo("Info", f"{count} documents loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def perform_search(self):
        query = self.query_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return

        search = Search(query)
        results = search.search()
        self.results_box.delete("1.0", tk.END)

        if not results:
            self.results_box.insert(tk.END, "No results found.\n")
            return

        retrieved_ids = set()
        for r in results:
            self.results_box.insert(tk.END, f"Title: {r.title}\nRank: {r.rank:.4f}\n")
            self.results_box.insert(tk.END, f"Matched terms: {r.matched_terms}\nSnippet: {r.snippet}\n\n")
            retrieved_ids.add(r.documentId)

        if query in predefined_relevant_docs:
            relevant_ids = predefined_relevant_docs[query]
        else:
            relevant_ids = set()  # пусто, если нет заранее определённых документов

        self.query_results[query] = {
            "relevant": relevant_ids,
            "retrieved": retrieved_ids
        }