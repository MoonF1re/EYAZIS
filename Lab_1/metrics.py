import matplotlib.pyplot as plt

def precision(relevant, retrieved):
    if not retrieved:
        return 0
    # используем set, чтобы убрать дубли
    return len(set(relevant) & set(retrieved)) / len(set(retrieved))    #Точность

def recall(relevant, retrieved):
    if not relevant:
        return 0
    return len(set(relevant) & set(retrieved)) / len(set(relevant))    #Полнота

def f1_score(precision, recall):
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0      #Сбалансированная метрика

def plot_metrics_for_queries(metrics_per_query):
    """
    metrics_per_query: dict
    {
        "query1": {"Precision": 0.8, "Recall": 0.6, "F1": 0.69},
        "query2": {"Precision": 1.0, "Recall": 0.5, "F1": 0.67},
        ...
    }
    """
    queries = list(metrics_per_query.keys())
    precision_vals = [metrics_per_query[q]["Precision"] for q in queries]
    recall_vals = [metrics_per_query[q]["Recall"] for q in queries]
    f1_vals = [metrics_per_query[q]["F1"] for q in queries]

    x = range(len(queries))
    width = 0.25

    plt.figure(figsize=(max(8, len(queries)), 5))  # автоматически увеличиваем ширину графика

    plt.bar([i - width for i in x], precision_vals, width=width, color='blue', label='Precision')
    plt.bar(x, recall_vals, width=width, color='green', label='Recall')
    plt.bar([i + width for i in x], f1_vals, width=width, color='red', label='F1-score')

    # Подписи оси X
    plt.xticks(x, queries, rotation=45, ha='right')  # наклон подписей и выравнивание
    plt.ylim(0, 2)
    plt.ylabel("Оценка")
    plt.title("Метрики")
    plt.legend()
    plt.tight_layout()
    plt.show()

