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