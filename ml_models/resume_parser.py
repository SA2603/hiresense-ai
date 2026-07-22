import re
import spacy

# Load the spaCy model once when this module is imported (not on every function call -
# loading a model is slow, so we want to do it exactly once, not repeatedly)
nlp = spacy.load("en_core_web_sm")


def extract_email(text: str) -> str:
    """
    Finds the first email-shaped string in the text using regex.
    Returns empty string if none found.
    """
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """
    Finds the first phone-number-shaped string using regex.
    Handles common formats: (123) 456-7890, 123-456-7890, +1 123 456 7890, etc.
    """
    pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else ""


def extract_name(text: str) -> str:
    """
    Uses spaCy's Named Entity Recognition to find the most likely name.
    Heuristic: the name is almost always in the first few lines of a resume,
    so we only run NER on the first chunk of text rather than the whole
    document (faster, and avoids accidentally picking up a referenced
    person's name from later in the resume, e.g. in a reference section).
    """
    first_chunk = text[:300]  # first ~300 characters, where names almost always appear
    doc = nlp(first_chunk)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    return ""  # spaCy found no PERSON entity - we'll handle this gracefully in the UI


def extract_contact_info(text: str) -> dict:
    """
    Convenience function that bundles all contact extraction together.
    This is what the rest of the app will actually call.
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }

from skills_database import ALL_SKILLS  # add this import at the top of the file


# Common section header variants we expect to see in resumes
SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"]
}


def split_into_sections(text: str) -> dict:
    """
    Splits resume text into sections based on detected headers.
    Returns a dict like {"skills": "...text...", "education": "...text...", ...}
    Any text before the first detected header is ignored (usually contact info).
    """
    lines = text.split("\n")
    sections = {key: "" for key in SECTION_HEADERS}
    current_section = None

    for line in lines:
        clean_line = line.strip().lower()

        # Check if this line matches any known section header
        matched_section = None
        for section_key, variants in SECTION_HEADERS.items():
            # A line counts as a header if it's short (headers are brief)
            # AND matches one of our known variants
            if clean_line in variants and len(clean_line) < 40:
                matched_section = section_key
                break

        if matched_section:
            current_section = matched_section
            continue  # don't include the header line itself in the section content

        if current_section:
            sections[current_section] += line + "\n"

    return sections


def extract_skills(text: str) -> list:
    """
    Checks the full resume text against our known skills list.
    Returns a list of matched skills (deduplicated, original casing from our list).
    We search the FULL text (not just the skills section) because skills are
    often also mentioned inside experience/project bullet points.
    """
    text_lower = text.lower()
    found_skills = []

    for skill in ALL_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)

    return sorted(set(found_skills))


def extract_education(text: str) -> str:
    """
    Returns the raw text of the education section, cleaned up.
    We keep this as readable text (not further parsed into fields like
    'degree' and 'university') since education formatting varies too much
    to reliably split further with simple rules.
    """
    sections = split_into_sections(text)
    return sections["education"].strip()


def extract_experience(text: str) -> str:
    """Returns the raw text of the experience section."""
    sections = split_into_sections(text)
    return sections["experience"].strip()


def extract_projects(text: str) -> str:
    """Returns the raw text of the projects section."""
    sections = split_into_sections(text)
    return sections["projects"].strip()


def extract_certifications(text: str) -> str:
    """Returns the raw text of the certifications section."""
    sections = split_into_sections(text)
    return sections["certifications"].strip()


def parse_resume(text: str) -> dict:
    """
    The main entry point - runs ALL extraction functions and returns
    one unified dictionary. This is what the rest of the app will call.
    """
    contact_info = extract_contact_info(text)

    return {
        "name": contact_info["name"],
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "projects": extract_projects(text),
        "certifications": extract_certifications(text)
    }