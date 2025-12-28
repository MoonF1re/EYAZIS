from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def save_pdf(path, text):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 40

    for line in text.split("\n"):
        c.drawString(40, y, line)
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()


def save_txt(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
