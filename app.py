# app.py
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Page configuration
st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .output-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def analyze_resume(resume_text, job_description):
    """Analyze resume using Gemini AI"""
    prompt = f"""
    As an expert ATS and resume consultant, analyze this resume and job description:

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}

    Please provide:
    1. A relevance score (0-100%)
    2. Key matching skills and experiences
    3. Missing key requirements
    4. A tailored version of the resume optimized for this role
    5. Specific suggestions for improvement

    Format the response in clear sections with markdown headings.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return None

def generate_ats_keywords(job_description):
    """Generate ATS keywords from job description"""
    prompt = f"""
    As an ATS expert, analyze this job description and provide:
    1. Key technical skills required
    2. Key soft skills required
    3. Required qualifications
    4. Important keywords for ATS optimization

    JOB DESCRIPTION:
    {job_description}

    Format the response in markdown with clear sections.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating keywords: {str(e)}")
        return None

def improve_resume_section(section_text):
    """Improve specific resume section"""
    prompt = f"""
    As a professional resume writer, improve this resume section:

    {section_text}

    Provide:
    1. An improved version with stronger action verbs
    2. Better quantification of achievements
    3. Enhanced formatting suggestions
    4. Keywords optimization

    Format the response in markdown.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error improving section: {str(e)}")
        return None

def main():
    st.title("🤖 AI Resume Tailor")
    st.markdown("### Optimize your resume with AI-powered analysis and recommendations")

    # Sidebar
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        1. Upload your resume (PDF)
        2. Paste the job description
        3. Choose analysis options
        4. Get AI-powered recommendations
        """)

        st.header("Features")
        st.markdown("""
        - ATS Optimization
        - Keyword Analysis
        - Section Improvements
        - Tailored Content
        - Format Suggestions
        """)

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Resume")
        uploaded_file = st.file_uploader("Choose your resume (PDF)", type=['pdf'])

        st.subheader("📝 Job Description")
        job_description = st.text_area("Paste the job description here", height=200)

        if uploaded_file and job_description:
            analyze_button = st.button("🔍 Analyze Resume")
            keywords_button = st.button("🎯 Generate ATS Keywords")

    with col2:
        if uploaded_file and job_description:
            if analyze_button:
                with st.spinner('Analyzing your resume...'):
                    # Extract text from PDF
                    resume_text = extract_text_from_pdf(uploaded_file)
                    if resume_text:
                        # Get AI analysis
                        analysis = analyze_resume(resume_text, job_description)
                        if analysis:
                            st.markdown("### 📊 Analysis Results")
                            st.markdown(analysis)

                            # Add download button for the analysis
                            st.download_button(
                                label="📥 Download Analysis",
                                data=analysis,
                                file_name="resume_analysis.md",
                                mime="text/markdown"
                            )

            if keywords_button:
                with st.spinner('Generating ATS keywords...'):
                    keywords = generate_ats_keywords(job_description)
                    if keywords:
                        st.markdown("### 🎯 ATS Keywords")
                        st.markdown(keywords)

                        # Add download button for keywords
                        st.download_button(
                            label="📥 Download Keywords",
                            data=keywords,
                            file_name="ats_keywords.md",
                            mime="text/markdown"
                        )

    # Section Improver
    if uploaded_file:
        st.markdown("---")
        st.subheader("✨ Section Improver")
        section_text = st.text_area("Paste a specific section to improve", height=150)
        if section_text:
            if st.button("Improve Section"):
                with st.spinner('Improving section...'):
                    improved = improve_resume_section(section_text)
                    if improved:
                        st.markdown("### 📝 Improved Section")
                        st.markdown(improved)

                        # Add download button for improved section
                        st.download_button(
                            label="📥 Download Improved Section",
                            data=improved,
                            file_name="improved_section.md",
                            mime="text/markdown"
                        )

if __name__ == "__main__":
    main()
