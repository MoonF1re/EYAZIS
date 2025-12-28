def build_dependency_tree(doc, sent_id=0):
    sent = list(doc.sents)[sent_id]

    root = [t for t in sent if t.head == t][0]

    def walk(token):
        return {
            "text": f"{token.text} ({token.dep_})",
            "children": [walk(child) for child in token.children]
        }

    return walk(root)
