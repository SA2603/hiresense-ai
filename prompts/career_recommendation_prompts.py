def build_career_recommendations_prompt(resume_text: str, missing_skills: list = None, jd_text: str = None) -> tuple:
    """
    Builds prompts for career recommendations.
    missing_skills: optional list of skill names from Stage 6's skill gap
    analysis - if provided, recommendations directly address these gaps.
    """
    system_prompt = """You are an expert career coach and technical mentor who \
gives practical, realistic career development advice.

You MUST respond with ONLY valid JSON - no markdown code fences, no explanation \
text before or after. Follow EXACTLY this structure:

{
  "recommended_courses": [
    {"title": "...", "platform": "...", "reason": "..."}
  ],
  "recommended_certifications": [
    {"title": "...", "issuing_body": "...", "reason": "..."}
  ],
  "recommended_projects": [
    {"title": "...", "description": "...", "skills_practiced": ["...", "..."]}
  ],
  "learning_roadmap": [
    {"phase": "Month 1-2", "focus": "...", "goals": ["...", "..."]},
    {"phase": "Month 3-4", "focus": "...", "goals": ["...", "..."]},
    {"phase": "Month 5-6", "focus": "...", "goals": ["...", "..."]}
  ],
  "suggested_career_roles": [
    {"role": "...", "why_fit": "...", "typical_next_step": true_or_false}
  ]
}

Provide exactly 3 courses, 2 certifications, 3 projects, a 3-phase roadmap \
(spanning roughly 6 months), and 3 suggested career roles. Recommendations \
should be realistic, specific (real course names/platforms where reasonable, \
e.g. Coursera, Udemy, freeCodeCamp - not vague like 'take an online course'), \
and directly tied to gaps or growth opportunities visible in the candidate's \
actual background."""

    missing_skills_text = ""
    if missing_skills:
        missing_skills_text = f"\n\nThis candidate is specifically missing these skills for a target role: {', '.join(missing_skills)}. Prioritize recommendations that address these gaps."

    if jd_text:
        user_prompt = f"""Candidate's resume:
---RESUME---
{resume_text}
---END RESUME---

Target job description:
---JOB DESCRIPTION---
{jd_text}
---END JOB DESCRIPTION---
{missing_skills_text}

Generate career recommendations tailored to helping this candidate become a \
strong fit for this specific role, following the exact JSON structure specified."""
    else:
        user_prompt = f"""Candidate's resume:
---RESUME---
{resume_text}
---END RESUME---
{missing_skills_text}

No specific job description provided. Generate general career growth \
recommendations based on this candidate's current background and trajectory, \
following the exact JSON structure specified."""

    return system_prompt, user_prompt