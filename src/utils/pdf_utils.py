import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract
import tempfile


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using PyPDF2, fallback to pdfminer if needed.
    Returns a list of (page_num, text) tuples.
    """
    texts = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    texts.append((i + 1, page_text))
                else:
                    # Fallback to pdfminer for this page
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_page:
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(page)
                        writer.write(tmp_page)
                        tmp_page_path = tmp_page.name
                    try:
                        miner_text = pdfminer_extract(tmp_page_path)
                        if miner_text and miner_text.strip():
                            texts.append((i + 1, miner_text))
                    finally:
                        import os
                        os.unlink(tmp_page_path)
        return texts
    except Exception:
        # Fallback to pdfminer for the whole file
        try:
            full_text = pdfminer_extract(pdf_path)
            return [(1, full_text)]
        except Exception:
            return [] 