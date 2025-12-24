import os
from document import Document

def load_documents_from_folder(folder_path):
    """Загрузка всех .txt документов из указанной папки"""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    doc_id = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            doc = Document(doc_id, filename, text)
            doc.add_to_base()
            doc_id += 1
    return doc_id  # количество загруженных документов
