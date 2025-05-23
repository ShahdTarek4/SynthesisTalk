from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import uuid

def generate_pdf(content: str, title="SynthesisTalk Export"):
    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join("exports", filename)

    os.makedirs("exports", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)

    c.setFont("Helvetica", 12)
    y = height - 100

    for line in content.split("\n"):
        if y < 72:
            c.showPage()
            y = height - 72
        c.drawString(72, y, line)
        y -= 18

    c.save()
    return filepath
