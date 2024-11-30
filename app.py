# app.py
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Page configuration
st.set_page_config(
    page_title="AI Resume & Cover Letter Generator",
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
    .success-box {
        background-color: #d1f2eb;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def scrape_job_description(url):
    """Scrape job description from common job sites"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Identify the job site
        domain = urlparse(url).netloc

        if 'linkedin.com' in domain:
            job_desc = soup.find('div', {'class': 'description__text'})
        elif 'indeed.com' in domain:
            job_desc = soup.find('div', {'id': 'jobDescriptionText'})
        elif 'glassdoor.com' in domain:
            job_desc = soup.find('div', {'class': 'jobDescriptionContent'})
        else:
            # Generic extraction
            job_desc = soup.find(['div', 'section'], {'class': re.compile('(job|position|description)', re.I)})

        if job_desc:
            return job_desc.get_text(strip=True)
        else:
            return None

    except Exception as e:
        st.error(f"Error scraping job description: {str(e)}")
        return None

def generate_cover_letter(resume_text, job_description, company_name, role_title):
    """Generate a cover letter using Gemini AI"""
    prompt = f"""
    As an expert cover letter writer, create a compelling cover letter based on:

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}

    COMPANY: {company_name}
    ROLE: {role_title}

    Please write a professional cover letter that:
    1. Matches the candidate's experience with job requirements
    2. Shows enthusiasm for the role and company
    3. Highlights relevant achievements
    4. Maintains a professional yet engaging tone
    5. Follows standard cover letter format

    Format the response as a properly structured cover letter with appropriate spacing and paragraphs.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating cover letter: {str(e)}")
        return None

# [Previous functions remain the same: extract_text_from_pdf, analyze_resume, generate_ats_keywords, improve_resume_section]

def main():
    st.title("🤖 AI Resume & Cover Letter Generator")
    st.markdown("### Optimize your application materials with AI-powered analysis")

    # Sidebar
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        1. Upload your resume (PDF)
        2. Enter job details (URL or paste)
        3. Get resume analysis
        4. Generate cover letter
        """)

        st.header("Features")
        st.markdown("""
        - ATS Optimization
        - Job Description Scraping
        - Resume Analysis
        - Cover Letter Generation
        - Format Suggestions
        """)

    # Main content
    tab1, tab2 = st.tabs(["Resume Analysis", "Cover Letter Generator"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📤 Upload Resume")
            uploaded_file = st.file_uploader("Choose your resume (PDF)", type=['pdf'])

            st.subheader("📝 Job Description")
            input_method = st.radio("Choose input method:", 
                                  ["Paste Job Description", "Enter Job URL"])

            if input_method == "Enter Job URL":
                job_url = st.text_input("Enter job posting URL:")
                if job_url:
                    if st.button("Fetch Job Description"):
                        with st.spinner('Fetching job description...'):
                            job_description = scrape_job_description(job_url)
                            if job_description:
                                st.session_state.job_description = job_description
                                st.success("Job description fetched successfully!")
                            else:
                                st.error("Could not fetch job description. Please paste it manually.")
            else:
                job_description = st.text_area("Paste the job description here", height=200)
                if job_description:
                    st.session_state.job_description = job_description

            if uploaded_file and 'job_description' in st.session_state:
                analyze_button = st.button("🔍 Analyze Resume")
                keywords_button = st.button("🎯 Generate ATS Keywords")

        with col2:
            if uploaded_file and 'job_description' in st.session_state:
                if analyze_button:
                    with st.spinner('Analyzing your resume...'):
                        resume_text = extract_text_from_pdf(uploaded_file)
                        if resume_text:
                            st.session_state.resume_text = resume_text
                            analysis = analyze_resume(resume_text, st.session_state.job_description)
                            if analysis:
                                st.markdown("### 📊 Analysis Results")
                                st.markdown(analysis)
                                st.session_state.analysis_complete = True

                                st.download_button(
                                    label="📥 Download Analysis",
                                    data=analysis,
                                    file_name="resume_analysis.md",
                                    mime="text/markdown"
                                )

                if keywords_button:
                    with st.spinner('Generating ATS keywords...'):
                        keywords = generate_ats_keywords(st.session_state.job_description)
                        if keywords:
                            st.markdown("### 🎯 ATS Keywords")
                            st.markdown(keywords)

                            st.download_button(
                                label="📥 Download Keywords",
                                data=keywords,
                                file_name="ats_keywords.md",
                                mime="text/markdown"
                            )

    with tab2:
        st.subheader("✍️ Cover Letter Generator")
        if 'analysis_complete' in st.session_state and st.session_state.analysis_complete:
            company_name = st.text_input("Company Name:")
            role_title = st.text_input("Role Title:")

            if company_name and role_title:
                if st.button("Generate Cover Letter"):
                    with st.spinner('Generating cover letter...'):
                        cover_letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.job_description,
                            company_name,
                            role_title
                        )
                        if cover_letter:
                            st.markdown("### 📝 Generated Cover Letter")
                            st.markdown(cover_letter)

                            st.download_button(
                                label="📥 Download Cover Letter",
                                data=cover_letter,
                                file_name="cover_letter.md",
                                mime="text/markdown"
                            )
        else:
            st.info("Please complete the resume analysis first to generate a cover letter.")

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

                        st.download_button(
                            label="📥 Download Improved Section",
                            data=improved,
                            file_name="improved_section.md",
                            mime="text/markdown"
                        )

if __name__ == "__main__":
    main()
