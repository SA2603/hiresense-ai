import re


def score_skills(parsed_data: dict) -> float:
    """
    Scores based on the NUMBER of recognized skills found.
    Returns a value from 0-100.
    Heuristic: 10+ recognized skills = full score, scaled linearly below that.
    """
    num_skills = len(parsed_data.get("skills", []))
    score = min(num_skills / 10 * 100, 100)  # cap at 100 even if more than 10 skills
    return round(score, 1)


def score_formatting(parsed_data: dict, raw_text: str) -> float:
    """
    Scores based on structural signals that indicate a well-formatted,
    ATS-parseable resume:
    - Contact info detected (name, email, phone) - 40 points
    - At least 2 of the 4 main sections detected - 40 points
    - Reasonable length (not too short, not absurdly long) - 20 points
    """
    score = 0.0

    # Contact info check (40 points total, ~13.3 each)
    if parsed_data.get("name"):
        score += 13.3
    if parsed_data.get("email"):
        score += 13.3
    if parsed_data.get("phone"):
        score += 13.4

    # Section presence check (40 points total)
    sections_present = sum([
        bool(parsed_data.get("education")),
        bool(parsed_data.get("experience")),
        bool(parsed_data.get("projects")),
        bool(parsed_data.get("certifications"))
    ])
    score += min(sections_present / 2, 1) * 40  # full 40 points if 2+ sections found

    # Length check (20 points) - a resume that's too short likely lacks detail,
    # too long may not be well-structured for a 1-2 page ATS-friendly format
    word_count = len(raw_text.split())
    if 150 <= word_count <= 1200:
        score += 20
    elif word_count > 0:
        score += 10  # partial credit - present but outside ideal range

    return round(min(score, 100), 1)


def score_keywords(raw_text: str) -> float:
    """
    Scores based on presence of ATS-friendly keyword patterns:
    - Action verbs (led, developed, managed, built, etc.)
    - Quantifiable results (numbers, percentages)
    """
    text_lower = raw_text.lower()

    action_verbs = [
        "led", "developed", "built", "managed", "created", "designed",
        "implemented", "improved", "increased", "reduced", "launched",
        "optimized", "achieved", "delivered", "coordinated", "analyzed"
    ]
    verb_hits = sum(1 for verb in action_verbs if verb in text_lower)
    verb_score = min(verb_hits / 8 * 50, 50)  # up to 50 points for action verbs

    # Look for numbers/percentages - a common sign of quantified achievements
    # e.g. "increased sales by 20%" or "managed a team of 5"
    number_pattern = r"\d+%|\$\d+|\d+\+|\bteam of \d+"
    number_matches = re.findall(number_pattern, text_lower)
    number_score = min(len(number_matches) / 3 * 50, 50)  # up to 50 points

    return round(verb_score + number_score, 1)


def score_experience(parsed_data: dict) -> float:
    """
    Scores based on presence AND substance of the experience section.
    """
    experience_text = parsed_data.get("experience", "")
    if not experience_text:
        return 0.0

    word_count = len(experience_text.split())
    # More content generally suggests more detailed experience descriptions
    score = min(word_count / 50 * 100, 100)
    return round(score, 1)


def score_education(parsed_data: dict) -> float:
    """Scores based on presence of an education section."""
    return 100.0 if parsed_data.get("education") else 0.0


def score_projects_certifications(parsed_data: dict) -> float:
    """
    Bonus category - scores based on presence of projects OR certifications.
    Having either gives full marks here since they're complementary signals.
    """
    has_projects = bool(parsed_data.get("projects"))
    has_certifications = bool(parsed_data.get("certifications"))
    if has_projects and has_certifications:
        return 100.0
    elif has_projects or has_certifications:
        return 60.0
    return 0.0


def calculate_ats_score(parsed_data: dict, raw_text: str) -> dict:
    """
    Main entry point - calculates the overall weighted ATS score and
    returns a full breakdown for display.
    """
    weights = {
        "skills": 0.30,
        "formatting": 0.20,
        "keywords": 0.20,
        "experience": 0.15,
        "education": 0.10,
        "projects_certifications": 0.05
    }

    breakdown = {
        "skills": score_skills(parsed_data),
        "formatting": score_formatting(parsed_data, raw_text),
        "keywords": score_keywords(raw_text),
        "experience": score_experience(parsed_data),
        "education": score_education(parsed_data),
        "projects_certifications": score_projects_certifications(parsed_data)
    }

    overall_score = sum(breakdown[key] * weights[key] for key in weights)

    return {
        "overall_score": round(overall_score, 1),
        "breakdown": breakdown,
        "weights": weights
    }