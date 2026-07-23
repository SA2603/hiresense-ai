import sys
sys.path.append("ml_models")
sys.path.append("utils")

from ml_models.resume_parser import parse_resume
from utils.text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf(pdf_bytes)

result = parse_resume(text)

print("Name:", result["name"])
print("Email:", result["email"])
print("Phone:", result["phone"])
print("\nSkills found:", result["skills"])
print("\n--- Education section ---")
print(result["education"])
print("\n--- Experience section ---")
print(result["experience"])
print("\n--- Projects section ---")
print(result["projects"])
print("\n--- Certifications section ---")
print(result["certifications"])