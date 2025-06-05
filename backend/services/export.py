from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
import os
import uuid

def generate_pdf(content: str, title="SynthesisTalk Export"):
    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join("exports", filename)

    os.makedirs("exports", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)

    c.setFont("Helvetica", 12)
    y = height - 100
    max_width = width - 144  # 1 inch margin left and right

    # Split content into lines and wrap them if too long
    for paragraph in content.split("\n"):
        lines = simpleSplit(paragraph, "Helvetica", 12, max_width)
        for line in lines:
            if y < 72:  # New page if too low
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 72
            c.drawString(72, y, line)
            y -= 18

    c.save()
    return filepath