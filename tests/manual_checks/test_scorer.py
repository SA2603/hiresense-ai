import sys
sys.path.append("ml_models")
sys.path.append("utils")

from ml_models.resume_parser import parse_resume
from utils.text_extraction import extract_text_from_pdf
from ml_models.ats_scorer import calculate_ats_score

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf(pdf_bytes)
parsed = parse_resume(text)

result = calculate_ats_score(parsed, text)

print("Overall ATS Score:", result["overall_score"])
print("\nBreakdown:")
for category, score in result["breakdown"].items():
    print(f"  {category}: {score}")