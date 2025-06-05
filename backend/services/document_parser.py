
#document_parser.py 

import docx
import pdfplumber


def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

def extract_text_from_docx(file_path):
    """Extract text from Word documents (.docx)"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        return text
    except Exception as e:
        return f"Error reading Word document: {str(e)}"

def extract_text_from_document(file_path, file_extension):
    """
    Universal document text extractor
    """
    file_extension = file_extension.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    else:
        return f"Unsupported file type: {file_extension}"