import sys
sys.path.append("utils")
sys.path.append("ml_models")

from report_generator import generate_report
from resume_parser import parse_resume
from ats_scorer import calculate_ats_score
from text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf(pdf_bytes)
parsed = parse_resume(text)
ats_result = calculate_ats_score(parsed, text)

output_path = generate_report(
    parsed_data=parsed,
    ats_result=ats_result,
    similarity_score=78.5,  # dummy value for testing
    output_path="test_output_report.pdf"
)

print(f"Report generated at: {output_path}")