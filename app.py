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
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("Google API key is missing. Please check your .env file.")

# Page configuration
st.set_page_config(
    page_title="AI Resume & Cover Letter Generator",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'job_description' not in st.session_state:
    st.session_state['job_description'] = None

if 'resume_text' not in st.session_state:
    st.session_state['resume_text'] = None

if 'analysis_complete' not in st.session_state:
    st.session_state['analysis_complete'] = False

# Functions
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

# Main function
def main():
    st.title("🤖 AI Resume & Cover Letter Generator")
    st.markdown("### Optimize your application materials with AI-powered analysis")

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
        """)

    tab1, tab2 = st.tabs(["Resume Analysis", "Cover Letter Generator"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📤 Upload Resume")
            uploaded_file = st.file_uploader("Choose your resume (PDF)", type=['pdf'])

            st.subheader("📝 Job Description")
            input_method = st.radio("Choose input method:", ["Paste Job Description", "Enter Job URL"])

            if input_method == "Enter Job URL":
                job_url = st.text_input("Enter job posting URL:")
                if job_url and st.button("Fetch Job Description"):
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

            if uploaded_file and st.session_state.job_description:
                if st.button("🔍 Analyze Resume"):
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

        with tab2:
            st.subheader("✍️ Cover Letter Generator")
            if st.session_state.analysis_complete:
                company_name = st.text_input("Company Name:")
                role_title = st.text_input("Role Title:")
                if company_name and role_title and st.button("Generate Cover Letter"):
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

if __name__ == "__main__":
    main()
