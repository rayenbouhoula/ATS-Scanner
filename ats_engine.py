import re
from PyPDF2 import PdfReader
from docx import Document
from skills import SOFTWARE_SKILLS

# ---------- FILE PARSING ----------
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def read_docx(file):
    doc = Document(file)
    return " ".join(p.text for p in doc.paragraphs)

# ---------- CLEAN TEXT ----------
def clean(text):
    text = text.lower()
    return re.sub(r"[^a-z0-9\s]", " ", text)

# ---------- SKILL EXTRACTION ----------
def extract_skills(text):
    text = clean(text)
    found = set()

    for category in SOFTWARE_SKILLS.values():
        for skill in category:
            if skill in text:
                found.add(skill)

    return found

# ---------- BASELINE ATS SCORE (NO JOB DESCRIPTION) ----------
def baseline_ats_score(resume_text):
    resume = resume_text.lower()
    skills_found = extract_skills(resume)

    # All known software skills
    all_skills = set(
        skill for group in SOFTWARE_SKILLS.values() for skill in group
    )

    # ---- Skill coverage (45) ----
    skill_score = (len(skills_found) / len(all_skills)) * 45 if all_skills else 0

    # ---- Sections (25) ----
    sections = ["experience", "education", "projects", "skills", "github"]
    section_score = (sum(1 for s in sections if s in resume) / len(sections)) * 25

    # ---- Length (15) ----
    words = len(resume.split())
    length_score = 15 if 350 <= words <= 900 else 7

    # ---- Warnings ----
    warnings = []
    if "|" in resume:
        warnings.append("Avoid tables – ATS systems may fail to parse them.")
    if words < 250:
        warnings.append("Resume is too short for most ATS systems.")
    if words > 1000:
        warnings.append("Resume is too long; keep it concise.")

    total = skill_score + section_score + length_score
    total = min(round(total, 2), 100)

    missing_skills = all_skills - skills_found

    return total, skills_found, missing_skills, warnings
