from skills_database import ALL_SKILLS


def extract_skills_from_text(text: str) -> set:
    """
    Same skill-matching logic as resume_parser.extract_skills(),
    but returns a SET (not a list) since we need set operations
    (intersection, difference) for gap analysis.
    Reusable for both resume text and JD text - skill matching logic
    doesn't care which type of document it's looking at.
    """
    text_lower = text.lower()
    found = {skill for skill in ALL_SKILLS if skill in text_lower}
    return found


def calculate_skill_importance(jd_text: str, skill: str) -> int:
    """
    Counts how many times a skill keyword appears in the JD text.
    Used as a simple proxy for "importance" - more mentions suggests
    the role weights that skill more heavily.
    """
    return jd_text.lower().count(skill.lower())


def analyze_skill_gap(resume_text: str, jd_text: str) -> dict:
    """
    Main entry point - compares resume skills against JD skills.
    Returns matched skills, missing skills (with importance scores,
    sorted by importance), and a simple match percentage.
    """
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(jd_text)

    matched = resume_skills & jd_skills       # intersection - in both
    missing = jd_skills - resume_skills       # in JD but not resume
    extra = resume_skills - jd_skills         # in resume but not JD (bonus skills)

    # Build missing skills list with importance scores, sorted highest importance first
    missing_with_importance = [
        {"skill": skill, "importance": calculate_skill_importance(jd_text, skill)}
        for skill in missing
    ]
    missing_with_importance.sort(key=lambda x: x["importance"], reverse=True)

    # Match percentage: what fraction of JD-required skills does the resume cover?
    if len(jd_skills) > 0:
        match_percentage = round(len(matched) / len(jd_skills) * 100, 1)
    else:
        match_percentage = 0.0  # no skills detected in JD at all - can't compute meaningfully

    return {
        "matched_skills": sorted(matched),
        "missing_skills": missing_with_importance,
        "extra_skills": sorted(extra),
        "match_percentage": match_percentage,
        "total_jd_skills": len(jd_skills),
        "total_matched": len(matched)
    }


def recommend_skills_to_learn(missing_with_importance: list, top_n: int = 5) -> list:
    """
    Simple recommendation: just the top N missing skills by importance.
    This is intentionally simple for now - Stage 11 (Career Recommendations)
    will use the GenAI/LLM to give richer, more contextual suggestions
    (courses, projects, roadmap) built on top of this raw list.
    """
    return [item["skill"] for item in missing_with_importance[:top_n]]