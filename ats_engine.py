import re
from PyPDF2 import PdfReader
from docx import Document
from skills import SOFTWARE_SKILLS

# ---------- FILE PARSING ----------
def read_pdf(file):
    """Extract text from PDF file"""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def read_docx(file):
    """Extract text from DOCX file"""
    doc = Document(file)
    return " ".join(p.text for p in doc.paragraphs)

# ---------- CLEAN TEXT ----------
def clean(text):
    """Normalize text for processing"""
    text = text.lower()
    return re.sub(r"[^a-z0-9\s]", " ", text)

# ---------- SKILL EXTRACTION ----------
def extract_skills(text):
    """Extract all software skills from text"""
    text = clean(text)
    found = set()

    for category in SOFTWARE_SKILLS.values():
        for skill in category:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found.add(skill)

    return found

# ---------- BASELINE ATS SCORE (NO JOB DESCRIPTION) ----------
def baseline_ats_score(resume_text):
    """Calculate ATS score without job description"""
    resume = resume_text.lower()
    skills_found = extract_skills(resume)

    # All known software skills
    all_skills = set(
        skill for group in SOFTWARE_SKILLS.values() for skill in group
    )

    # ---- Skill coverage (45 points) ----
    skill_score = (len(skills_found) / len(all_skills)) * 45 if all_skills else 0

    # ---- Sections (25 points) ----
    sections = ["experience", "education", "projects", "skills", "github", "certifications"]
    section_score = (sum(1 for s in sections if s in resume) / len(sections)) * 25

    # ---- Length (15 points) ----
    words = len(resume.split())
    if 350 <= words <= 900:
        length_score = 15
    elif 250 <= words < 350 or 900 < words <= 1000:
        length_score = 10
    else:
        length_score = 5

    # ---- Format Quality (15 points) ----
    format_score = 15
    
    # Check for common ATS-friendly elements
    if "•" in resume_text or "-" in resume_text:  # Bullet points
        format_score += 0
    if "@" in resume_text and "." in resume_text:  # Email
        format_score += 0
    if "linkedin" in resume or "github" in resume:  # Social links
        format_score += 0

    # ---- Warnings ----
    warnings = []
    
    if "|" in resume or "│" in resume:
        warnings.append("Avoid tables – ATS systems may fail to parse them.")
        format_score -= 5
    
    if words < 250:
        warnings.append("Resume is too short for most ATS systems (aim for 350-900 words).")
    
    if words > 1000:
        warnings.append("Resume is too long; keep it concise (aim for 350-900 words).")
    
    if len(skills_found) < 5:
        warnings.append("Add more relevant technical skills to improve your ATS score.")
    
    if "experience" not in resume:
        warnings.append("Include an 'Experience' or 'Work Experience' section.")
    
    if "education" not in resume:
        warnings.append("Include an 'Education' section.")
    
    # Check for contact info
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        warnings.append("Add an email address for contact information.")
    
    # Calculate total score
    total = skill_score + section_score + length_score + format_score
    total = min(round(total, 2), 100)

    missing_skills = all_skills - skills_found

    return total, skills_found, missing_skills, warnings

# ---------- JOB MATCH SCORE ----------
def job_match_score(resume_text, job_description):
    """Calculate ATS score with job description matching"""
    # Get baseline score first
    base_score, skills_found, missing_skills, warnings = baseline_ats_score(resume_text)
    
    # Extract skills from job description
    jd_skills = extract_skills(job_description)
    
    # Calculate match percentage
    if jd_skills:
        matched_skills = skills_found.intersection(jd_skills)
        match_percentage = (len(matched_skills) / len(jd_skills)) * 100
        match_percentage = round(match_percentage, 2)
        
        # Adjust warnings based on job match
        if match_percentage < 50:
            warnings.append(f"Your resume matches only {match_percentage}% of job requirements. Add more relevant skills.")
        elif match_percentage < 75:
            warnings.append(f"Good match ({match_percentage}%), but you could add more job-specific keywords.")
    else:
        match_percentage = 0
        warnings.append("No specific skills found in job description.")
    
    return base_score, skills_found, missing_skills, warnings, match_percentage