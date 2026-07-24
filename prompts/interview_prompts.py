def build_interview_questions_prompt(resume_text: str, jd_text: str = None) -> tuple:
    """
    Builds prompts requesting interview questions as structured JSON.
    Returns (system_prompt, user_prompt).
    """
    system_prompt = """You are an expert technical interviewer who creates \
personalized interview questions based on a candidate's resume and (optionally) \
a target job description.

You MUST respond with ONLY valid JSON - no markdown code fences, no explanation \
text before or after, just the raw JSON object itself. The JSON must follow \
EXACTLY this structure:

{
  "hr_questions": [
    {"question": "...", "difficulty": "Easy|Medium|Hard"}
  ],
  "technical_questions": [
    {"question": "...", "difficulty": "Easy|Medium|Hard"}
  ],
  "behavioral_questions": [
    {"question": "...", "difficulty": "Easy|Medium|Hard"}
  ],
  "project_based_questions": [
    {"question": "...", "difficulty": "Easy|Medium|Hard"}
  ],
  "scenario_based_questions": [
    {"question": "...", "difficulty": "Easy|Medium|Hard"}
  ]
}

Generate exactly 3 questions per category (15 total), with a mix of difficulty \
levels within each category (at least one Easy, one Medium, one Hard per category). \
Base technical and project questions on the SPECIFIC skills/projects mentioned in \
the resume - do not ask generic questions unrelated to what the candidate has \
actually worked on."""

    if jd_text:
        user_prompt = f"""Candidate's resume:
---RESUME---
{resume_text}
---END RESUME---

Target job description:
---JOB DESCRIPTION---
{jd_text}
---END JOB DESCRIPTION---

Generate interview questions tailored to both this candidate's background AND \
this specific role, following the exact JSON structure specified."""
    else:
        user_prompt = f"""Candidate's resume:
---RESUME---
{resume_text}
---END RESUME---

No specific job description provided. Generate interview questions based on \
this candidate's background and apparent skill level, following the exact \
JSON structure specified."""

    return system_prompt, user_prompt