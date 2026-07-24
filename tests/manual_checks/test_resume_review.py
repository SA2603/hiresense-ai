import sys
sys.path.append("genai")
sys.path.append("prompts")
sys.path.append("ml_models")
sys.path.append("utils")

from groq_client import call_llm, parse_structured_review
from resume_review_prompts import build_resume_review_prompt
from text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()
resume_text = extract_text_from_pdf(pdf_bytes)

system_prompt, user_prompt = build_resume_review_prompt(resume_text)
raw_response = call_llm(system_prompt, user_prompt, temperature=0.5)

print("--- RAW RESPONSE ---")
print(raw_response)

parsed = parse_structured_review(raw_response)
print("\n--- PARSED SECTIONS ---")
for key, value in parsed.items():
    print(f"\n[{key.upper()}]")
    print(value)