import sys
sys.path.append("genai")
sys.path.append("prompts")
sys.path.append("utils")

from groq_client import call_llm, parse_json_response
from interview_prompts import build_interview_questions_prompt
from text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()
resume_text = extract_text_from_pdf(pdf_bytes)

system_prompt, user_prompt = build_interview_questions_prompt(resume_text)
raw_response = call_llm(system_prompt, user_prompt, temperature=0.6)

print("--- RAW RESPONSE (first 300 chars) ---")
print(raw_response[:300])

try:
    parsed = parse_json_response(raw_response)
    print("\n--- PARSED SUCCESSFULLY ---")
    for category, questions in parsed.items():
        print(f"\n{category.upper()} ({len(questions)} questions):")
        for q in questions:
            print(f"  [{q['difficulty']}] {q['question']}")
except Exception as e:
    print(f"\n❌ PARSING FAILED: {e}")
    print("Full raw response for debugging:")
    print(raw_response)