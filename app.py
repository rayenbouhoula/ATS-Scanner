import streamlit as st
from ats_engine import read_pdf, read_docx, baseline_ats_score, job_match_score
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="ATS Resume Scanner Pro", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- IMPROVED DESIGN WITH BETTER CONTRAST ----------
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Gradient - Lighter */
    .stApp {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e7ff 100%);
    }
    
    /* Main Content Area - Pure White */
    .main .block-container {
        background: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    /* Headings - Dark for Contrast */
    h1 {
        color: #1e293b !important;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #334155 !important;
        font-weight: 600;
    }
    
    h3 {
        color: #475569 !important;
        font-weight: 600;
    }
    
    /* Regular Text - Dark Gray */
    p, span, div {
        color: #334155;
    }
    
    /* Buttons - High Contrast */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: #ffffff !important;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* File Uploader */
    .uploadedFile {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #6366f1;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Metrics - Better Contrast */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #059669 !important;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background-color: #d1fae5 !important;
        color: #065f46 !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border-left: 4px solid #f59e0b !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Sidebar - Dark Theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Radio buttons in sidebar */
    section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }
    
    /* Code/Tag styling - Better contrast */
    code {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #334155;
    }
    
    /* Text input */
    input, textarea {
        color: #1e293b !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("⚙️ Settings")
    
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Quick Scan", "Job Match", "Detailed Analysis"]
    )
    
    st.markdown("---")
    
    st.subheader("📊 About")
    st.markdown("""
    **ATS Scanner Pro** helps you optimize your resume for Applicant Tracking Systems.
    """)
    
    # Features list with custom styling for visibility
    st.markdown("""
    <div style="color: #ffffff; background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-top: 10px;">
    <strong style="color: #ffffff;">Features:</strong><br>
    <span style="color: #d1fae5;">✅ ATS Score Analysis</span><br>
    <span style="color: #d1fae5;">✅ Skill Detection</span><br>
    <span style="color: #d1fae5;">✅ Job Description Matching</span><br>
    <span style="color: #d1fae5;">✅ Keyword Optimization</span><br>
    <span style="color: #d1fae5;">✅ Visual Analytics</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Made with ❤️ by Rayen Bouhoula")

# ---------- HEADER ----------
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💼 ATS Resume Scanner Pro")
    st.markdown("**Optimize your resume for Applicant Tracking Systems**")

with col2:
    st.metric("Total Scans", "1,234", "+12%")

st.markdown("---")

# ---------- UPLOAD SECTION ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Resume")
    resume_file = st.file_uploader(
        "Upload Your Resume (PDF / DOCX)",
        type=["pdf", "docx"],
        help="Upload your resume in PDF or DOCX format"
    )

with col2:
    if analysis_mode == "Job Match":
        st.subheader("📋 Job Description (Optional)")
        job_description = st.text_area(
            "Paste Job Description",
            height=150,
            placeholder="Paste the job description here to get a match score..."
        )
    else:
        job_description = None

# ---------- ANALYZE BUTTON ----------
if resume_file:
    if st.button("🚀 Analyze Resume", use_container_width=True):
        with st.spinner("🔍 Analyzing your resume..."):
            # Read resume
            if resume_file.name.endswith(".pdf"):
                resume_text = read_pdf(resume_file)
            else:
                resume_text = read_docx(resume_file)

            # Get ATS score
            if job_description:
                score, skills, missing, warnings, match_score = job_match_score(resume_text, job_description)
            else:
                score, skills, missing, warnings = baseline_ats_score(resume_text)
                match_score = None

        st.success("✅ Analysis Complete!")
        
        # ---------- RESULTS DASHBOARD ----------
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("ATS Score", f"{score}/100", f"+{score-70}" if score > 70 else f"{score-70}")
        
        with col2:
            st.metric("Skills Found", len(skills))
        
        with col3:
            st.metric("Missing Skills", len(missing))
        
        with col4:
            if match_score:
                st.metric("Job Match", f"{match_score}%")
            else:
                st.metric("Word Count", len(resume_text.split()))
        
        # Score Gauge Chart
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create gauge chart with better colors
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ATS Score", 'font': {'size': 24, 'color': '#1e293b'}},
                delta={'reference': 70, 'increasing': {'color': "#10b981"}},
                number={'font': {'size': 40, 'color': '#1e293b'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#64748b"},
                    'bar': {'color': "#6366f1", 'thickness': 0.8},
                    'bgcolor': "#f8fafc",
                    'borderwidth': 3,
                    'bordercolor': "#cbd5e1",
                    'steps': [
                        {'range': [0, 50], 'color': '#fee2e2'},
                        {'range': [50, 75], 'color': '#fef3c7'},
                        {'range': [75, 100], 'color': '#d1fae5'}
                    ],
                    'threshold': {
                        'line': {'color': "#ef4444", 'width': 4},
                        'thickness': 0.8,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="#ffffff",
                font={'color': "#1e293b", 'family': "Inter"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Score Breakdown")
            
            if score >= 80:
                st.success("🎉 Excellent! Your resume is ATS-friendly.")
            elif score >= 60:
                st.warning("⚠️ Good, but needs improvement.")
            else:
                st.error("❌ Needs significant optimization.")
            
            st.markdown(f"""
            **Score Components:**
            - Skills Coverage: {min(45, len(skills) * 2)}%
            - Sections: {min(25, len([s for s in ['experience', 'education', 'projects'] if s in resume_text.lower()]) * 8)}%
            - Length: {15 if 350 <= len(resume_text.split()) <= 900 else 7}%
            """)
        
        # Skills Analysis
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Detected Skills")
            if skills:
                # Create skill categories
                skill_list = list(skills)
                cols = st.columns(3)
                for idx, skill in enumerate(sorted(skill_list)):
                    with cols[idx % 3]:
                        st.markdown(f"✓ `{skill.title()}`")
            else:
                st.info("No skills detected. Add relevant technical skills!")
        
        with col2:
            st.subheader("❌ Missing Common Skills")
            if missing:
                # Show top 10 missing skills
                missing_list = list(missing)[:10]
                for skill in sorted(missing_list):
                    st.markdown(f"○ `{skill.title()}`")
            else:
                st.success("🎉 Great! You have all common skills covered!")
        
        # Skills Distribution Chart
        if skills:
            st.markdown("---")
            st.subheader("📈 Skills Distribution")
            
            from skills import SOFTWARE_SKILLS
            
            categories_count = {
                "Languages": 0,
                "Frameworks": 0,
                "Databases": 0,
                "Tools": 0
            }
            
            for skill in skills:
                if skill in SOFTWARE_SKILLS["languages"]:
                    categories_count["Languages"] += 1
                elif skill in SOFTWARE_SKILLS["frameworks"]:
                    categories_count["Frameworks"] += 1
                elif skill in SOFTWARE_SKILLS["databases"]:
                    categories_count["Databases"] += 1
                elif skill in SOFTWARE_SKILLS["tools"]:
                    categories_count["Tools"] += 1
            
            fig = px.bar(
                x=list(categories_count.keys()),
                y=list(categories_count.values()),
                labels={'x': 'Category', 'y': 'Count'},
                title="Skills by Category",
                color=list(categories_count.values()),
                color_continuous_scale=['#6366f1', '#8b5cf6']
            )
            
            fig.update_layout(
                showlegend=False,
                height=300,
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font={'family': "Inter", 'color': '#1e293b'},
                title_font_color='#1e293b',
                xaxis={'gridcolor': '#e2e8f0', 'color': '#1e293b'},
                yaxis={'gridcolor': '#e2e8f0', 'color': '#1e293b'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Warnings
        if warnings:
            st.markdown("---")
            st.subheader("⚠️ ATS Warnings & Recommendations")
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
        
        # Optimization Tips
        st.markdown("---")
        st.subheader("💡 Optimization Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Do's:**
            - ✅ Use standard section headings
            - ✅ Include relevant keywords
            - ✅ Use simple formatting
            - ✅ Save as .docx or .pdf
            - ✅ Include measurable achievements
            """)
        
        with col2:
            st.markdown("""
            **Don'ts:**
            - ❌ Avoid tables and columns
            - ❌ Don't use images or graphics
            - ❌ Avoid headers/footers
            - ❌ Don't use special characters
            - ❌ Avoid creative fonts
            """)
        
        # Download Report
        st.markdown("---")
        report = f"""
        ATS RESUME ANALYSIS REPORT
        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
        
        SCORE: {score}/100
        SKILLS FOUND: {len(skills)}
        MISSING SKILLS: {len(missing)}
        
        DETECTED SKILLS:
        {', '.join(sorted(skills))}
        
        RECOMMENDATIONS:
        {chr(10).join(f'- {w}' for w in warnings)}
        """
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"ats_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

else:
    # Landing section
    st.info("👆 Upload your resume to get started!")
    
    st.markdown("---")
    st.subheader("🎯 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Upload
        Upload your resume in PDF or DOCX format
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ Analyze
        Our AI scans your resume like an ATS system
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Optimize
        Get actionable insights to improve your score
        """)