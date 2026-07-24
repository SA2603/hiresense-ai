import streamlit as st
import json
import re
from groq import Groq

# Initialize the client once - reused across all calls in this module
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# We centralize the model name here so if we ever want to swap models,
# we change it in exactly one place
MODEL_NAME = "llama-3.1-8b-instant"


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """
    The core function every GenAI feature will call.
    system_prompt: sets the AI's role/persona/instructions (sent once, sets context)
    user_prompt: the actual request/content for this specific call
    temperature: controls randomness (0 = very consistent/deterministic,
                 1 = more creative/varied) - we'll tune this per use case
    Returns the model's text response as a plain string.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=1500
    )
    return response.choices[0].message.content

def parse_structured_review(review_text: str) -> dict:
    """
    Splits the LLM's structured response into separate fields based on
    our ### SECTION_NAME markers from the prompt.
    Returns a dict with keys: strengths, weaknesses, formatting_suggestions,
    grammar_suggestions, keyword_suggestions, recruiter_feedback.
    """
    sections = {
        "strengths": "",
        "weaknesses": "",
        "formatting_suggestions": "",
        "grammar_suggestions": "",
        "keyword_suggestions": "",
        "recruiter_feedback": ""
    }

    section_markers = {
        "### STRENGTHS": "strengths",
        "### WEAKNESSES": "weaknesses",
        "### FORMATTING_SUGGESTIONS": "formatting_suggestions",
        "### GRAMMAR_SUGGESTIONS": "grammar_suggestions",
        "### KEYWORD_SUGGESTIONS": "keyword_suggestions",
        "### RECRUITER_FEEDBACK": "recruiter_feedback"
    }

    current_key = None
    for line in review_text.split("\n"):
        stripped = line.strip()
        if stripped in section_markers:
            current_key = section_markers[stripped]
            continue
        if current_key:
            sections[current_key] += line + "\n"

    # Clean up trailing whitespace on each section
    return {key: value.strip() for key, value in sections.items()}

def parse_json_response(raw_response: str) -> dict:
    """
    Defensively parses a JSON response from the LLM, handling common
    formatting quirks:
    - Strips markdown code fences (```json ... ``` or ``` ... ```) if present
    - Strips leading/trailing whitespace or stray text outside the JSON braces
    Raises json.JSONDecodeError if the result still isn't valid JSON after cleanup.
    """
    cleaned = raw_response.strip()

    # Remove markdown code fences if the model added them despite instructions
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # If there's stray text before/after the JSON object, try to isolate
    # the outermost { ... } block
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1:
        cleaned = cleaned[first_brace:last_brace + 1]

    return json.loads(cleaned)  # will raise json.JSONDecodeError if still invalid