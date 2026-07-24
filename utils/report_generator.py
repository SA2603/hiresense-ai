from fpdf import FPDF
from datetime import datetime


class ReportPDF(FPDF):
    """
    Subclassing FPDF lets us define a consistent header/footer that
    automatically appears on every page, without repeating that code
    every time we add a page.
    """
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "HireSense AI - Resume Analysis Report", ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _add_section_title(pdf: ReportPDF, title: str):
    """Helper to consistently style every section heading in the report."""
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(4)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(3)


def _add_body_text(pdf: ReportPDF, text: str):
    """Helper for consistent body paragraph styling, with word wrapping."""
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    # multi_cell automatically wraps text across multiple lines within the given width
    pdf.multi_cell(0, 6, text)
    pdf.ln(2)


def generate_report(parsed_data: dict, ats_result: dict, similarity_score: float = None,
                     skill_gap_result: dict = None, ai_review: dict = None,
                     interview_questions: dict = None, career_recommendations: dict = None,
                     output_path: str = "report.pdf") -> str:
    """
    Compiles all analysis results into a single downloadable PDF report.
    Any argument can be None if that feature wasn't run - the report
    simply skips sections with no data, rather than failing.
    Returns the file path of the generated PDF.
    """
    pdf = ReportPDF()
    pdf.add_page()

    # --- RESUME SUMMARY ---
    _add_section_title(pdf, "Resume Summary")
    _add_body_text(pdf, f"Name: {parsed_data.get('name', 'N/A')}")
    _add_body_text(pdf, f"Email: {parsed_data.get('email', 'N/A')}")
    _add_body_text(pdf, f"Phone: {parsed_data.get('phone', 'N/A')}")
    skills = parsed_data.get("skills", [])
    _add_body_text(pdf, f"Skills detected: {', '.join(skills) if skills else 'None detected'}")

    # --- ATS SCORE ---
    if ats_result:
        _add_section_title(pdf, "ATS Score")
        _add_body_text(pdf, f"Overall Score: {ats_result['overall_score']} / 100")
        breakdown = ats_result.get("breakdown", {})
        for category, score in breakdown.items():
            label = category.replace("_", " ").title()
            _add_body_text(pdf, f"  - {label}: {score}")

    # --- SIMILARITY ---
    if similarity_score is not None:
        _add_section_title(pdf, "Resume-JD Semantic Similarity")
        _add_body_text(pdf, f"Similarity Score: {similarity_score}%")

    # --- SKILL GAP ---
    if skill_gap_result:
        _add_section_title(pdf, "Skill Gap Analysis")
        _add_body_text(pdf, f"Match Percentage: {skill_gap_result['match_percentage']}%")
        matched = ", ".join(skill_gap_result.get("matched_skills", [])) or "None"
        _add_body_text(pdf, f"Matched Skills: {matched}")
        missing_items = skill_gap_result.get("missing_skills", [])
        missing = ", ".join(item["skill"] for item in missing_items) or "None"
        _add_body_text(pdf, f"Missing Skills: {missing}")

    # --- AI REVIEW ---
    if ai_review:
        _add_section_title(pdf, "AI Resume Review")
        _add_body_text(pdf, "Strengths:")
        _add_body_text(pdf, ai_review.get("strengths", "N/A"))
        _add_body_text(pdf, "Weaknesses:")
        _add_body_text(pdf, ai_review.get("weaknesses", "N/A"))
        _add_body_text(pdf, "Recruiter Feedback:")
        _add_body_text(pdf, ai_review.get("recruiter_feedback", "N/A"))

    # --- INTERVIEW QUESTIONS ---
    if interview_questions:
        pdf.add_page()  # start fresh page - this section can get long
        _add_section_title(pdf, "Interview Questions")
        for category, questions in interview_questions.items():
            label = category.replace("_", " ").title()
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 7, label, ln=True)
            for q in questions:
                _add_body_text(pdf, f"  [{q.get('difficulty', '')}] {q.get('question', '')}")

    # --- CAREER RECOMMENDATIONS ---
    if career_recommendations:
        pdf.add_page()
        _add_section_title(pdf, "Career Recommendations")

        courses = career_recommendations.get("recommended_courses", [])
        if courses:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, "Recommended Courses", ln=True)
            for c in courses:
                _add_body_text(pdf, f"  - {c['title']} ({c['platform']}): {c['reason']}")

        roadmap = career_recommendations.get("learning_roadmap", [])
        if roadmap:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, "Learning Roadmap", ln=True)
            for phase in roadmap:
                _add_body_text(pdf, f"  {phase['phase']}: {phase['focus']}")

    pdf.output(output_path)
    return output_path