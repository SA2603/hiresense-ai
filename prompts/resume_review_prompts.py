def build_resume_review_prompt(resume_text: str, jd_text: str = None) -> tuple:
    """
    Builds the system and user prompts for AI resume review.
    Returns a tuple: (system_prompt, user_prompt)

    If jd_text is provided, the review is tailored to that specific role.
    Otherwise, it's a general resume quality review.
    """
    system_prompt = """You are an expert technical recruiter and resume reviewer \
with 15 years of experience hiring for technology roles. You give honest, \
specific, actionable feedback - never generic platitudes like "add more detail" \
without saying exactly what detail is missing and where.

You MUST respond using EXACTLY this structure, with these exact section headers, \
so your response can be parsed programmatically:

### STRENGTHS
- (bullet points, 3-5 specific strengths)

### WEAKNESSES
- (bullet points, 3-5 specific weaknesses)

### FORMATTING_SUGGESTIONS
- (bullet points, specific formatting improvements)

### GRAMMAR_SUGGESTIONS
- (bullet points, specific grammar/wording issues found, or "No significant grammar issues found" if none)

### KEYWORD_SUGGESTIONS
- (bullet points, specific keywords/terms that should be added)

### RECRUITER_FEEDBACK
(A short paragraph, 3-5 sentences, written as if you are the recruiter giving \
final verbal feedback after reviewing this resume)

Do not include any text before ### STRENGTHS or after the RECRUITER_FEEDBACK section. \
Do not add extra commentary outside these sections."""

    if jd_text:
        user_prompt = f"""Here is a candidate's resume:

---RESUME---
{resume_text}
---END RESUME---

Here is the job description they are applying for:

---JOB DESCRIPTION---
{jd_text}
---END JOB DESCRIPTION---

Review this resume specifically for fit against this job description, \
following the exact structure specified."""
    else:
        user_prompt = f"""Here is a candidate's resume:

---RESUME---
{resume_text}
---END RESUME---

No specific job description was provided - give a general resume quality \
review, following the exact structure specified."""

    return system_prompt, user_prompt