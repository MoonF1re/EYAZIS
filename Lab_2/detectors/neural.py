import subprocess

def detect_neural(text):
    prompt = f"""
Определи язык текста. Отвечай ОДНИМ словом.
Варианты ответа: French или German.

{text[:2000]}
"""

    result = subprocess.run(
        ["ollama", "run", "llama3.2"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True
    )

    return result.stdout.strip()

