import sys
sys.path.append("ml_models")

from skill_gap import analyze_skill_gap, recommend_skills_to_learn

resume_text = """
Experienced software engineer skilled in Python, SQL, and Git.
Built REST APIs using Flask and worked with PostgreSQL databases.
"""

jd_text = """
We are looking for a software engineer proficient in Python, SQL, Docker,
and AWS. Experience with React and Kubernetes is a strong plus. Familiarity
with Git and CI/CD pipelines required. Python experience is essential -
you will write Python daily.
"""

result = analyze_skill_gap(resume_text, jd_text)

print("Matched skills:", result["matched_skills"])
print("Missing skills (sorted by importance):")
for item in result["missing_skills"]:
    print(f"  {item['skill']} (mentioned {item['importance']}x)")
print("\nMatch percentage:", result["match_percentage"], "%")

print("\nTop skills to learn:", recommend_skills_to_learn(result["missing_skills"]))