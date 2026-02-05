import streamlit as st
from ats_engine import read_pdf, read_docx, baseline_ats_score

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ATS Resume Scanner", page_icon="💼", layout="wide")

# ---------- BLUE DESIGN ----------
st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background-color: #e6f0ff;
    }
    /* Headings */
    h1, h2, h3, h4 {
        color: #004080;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Buttons */
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
    }
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #004080 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- TITLE ----------
st.title("💼 Software Engineer ATS Scanner")
st.markdown("Upload your resume and see how ATS-friendly it is!")

# ---------- RESUME UPLOAD ----------
resume_file = st.file_uploader(
    "Upload Your Resume (PDF / DOCX)",
    type=["pdf", "docx"]
)

# ---------- ANALYZE BUTTON ----------
if resume_file:
    if st.button("🚀 Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            if resume_file.name.endswith(".pdf"):
                resume_text = read_pdf(resume_file)
            else:
                resume_text = read_docx(resume_file)

            score, skills, missing, warnings = baseline_ats_score(resume_text)

        # ---------- RESULTS ----------
        st.subheader("📊 ATS Results")
        st.progress(score / 100)
        st.markdown(f"**ATS Score:** {score}/100")

        st.subheader("✅ Detected Skills")
        st.write(", ".join(sorted(skills)) or "None detected")

        st.subheader("❌ Missing Common Skills")
        st.write(", ".join(sorted(missing)) or "None 🎉")

        st.subheader("⚠️ ATS Warnings")
        for w in warnings:
            st.warning(w)
