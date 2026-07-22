import sys
sys.path.append("ml_models")
sys.path.append("utils")

from ml_models.resume_parser import extract_contact_info
from utils.text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf(pdf_bytes)

print(extract_contact_info(text))