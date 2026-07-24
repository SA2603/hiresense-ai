import sys
sys.path.append("genai")
sys.path.append("prompts")
sys.path.append("ml_models")
sys.path.append("utils")

from groq_client import call_llm, parse_json_response
from career_recommendation_prompts import build_career_recommendations_prompt
from text_extraction import extract_text_from_pdf

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()
resume_text = extract_text_from_pdf(pdf_bytes)

# Simulating missing skills as if they came from Stage 6's skill gap analysis
sample_missing_skills = ["docker", "aws", "kubernetes"]

system_prompt, user_prompt = build_career_recommendations_prompt(
    resume_text, missing_skills=sample_missing_skills
)
raw_response = call_llm(system_prompt, user_prompt, temperature=0.6)

try:
    parsed = parse_json_response(raw_response)
    print("--- COURSES ---")
    for c in parsed["recommended_courses"]:
        print(f"  {c['title']} ({c['platform']}) - {c['reason']}")

    print("\n--- CERTIFICATIONS ---")
    for c in parsed["recommended_certifications"]:
        print(f"  {c['title']} ({c['issuing_body']})")

    print("\n--- PROJECTS ---")
    for p in parsed["recommended_projects"]:
        print(f"  {p['title']}: {p['description']}")

    print("\n--- ROADMAP ---")
    for phase in parsed["learning_roadmap"]:
        print(f"  {phase['phase']}: {phase['focus']}")

    print("\n--- CAREER ROLES ---")
    for role in parsed["suggested_career_roles"]:
        print(f"  {role['role']} - {role['why_fit']}")

except Exception as e:
    print(f"PARSING FAILED: {e}")
    print(raw_response)