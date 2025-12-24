import os
from file_loader import load_documents_from_folder
from search import Search
from metrics import precision, recall, f1_score, plot_metrics_for_queries

# Папка с документами
DOCUMENTS_FOLDER = "tests"

# Словарь тестовых запросов и релевантных документов
# documentID соответствует ID документов после загрузки
predefined_relevant_docs = {
    "artificial intelligence": {0, 2, 6},
    # 0_AI.txt, 2_Python.txt, 6_Machine_Learning.txt

    "data science": {3, 9},
    # 3_Data_Science.txt, 9_Statistics.txt

    "python programming": {2, 3, 8},
    # 2_Python.txt, 3_Data_Science.txt, 8_Programming.txt

    "computer networks": {1, 7},
    # 1_Networks.txt, 7_Security.txt


}

def run_tests():
    # Загрузка документов из папки
    if not os.path.exists(DOCUMENTS_FOLDER):
        print(f"Folder not found: {DOCUMENTS_FOLDER}")
        return

    count = load_documents_from_folder(DOCUMENTS_FOLDER)
    print(f"{count} documents loaded successfully!\n")

    results = {}

    for query, relevant_docs in predefined_relevant_docs.items():
        search = Search(query)
        search_results = search.search()
        retrieved_ids = set(r.documentId for r in search_results)
        for r in  search_results:
            print(f" ДОКУМЕНТЫ НАЙДЕНЫ: {r.title}")

        p = precision(relevant_docs, retrieved_ids)
        r = recall(relevant_docs, retrieved_ids)
        f = f1_score(p, r)

        results[query] = {"Precision": p, "Recall": r, "F1": f}

        print(f"Query: {query}")
        print(f"Retrieved: {retrieved_ids}")
        print(f"Relevant: {relevant_docs}")
        print(f"Precision: {p:.2f}, Recall: {r:.2f}, F1: {f:.2f}\n")

    # Построение графиков для всех запросов
    plot_metrics_for_queries(results)

if __name__ == "__main__":
    run_tests()
