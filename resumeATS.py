import streamlit as st
import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
# done h ji 
# Function to get Perplexity AI output
def get_perplexity_output(pdf_text, prompt):
    """
    Function to interact with Perplexity AI API using the sonar-pro model
    """
    api_key = st.secrets["settings"]["PERPLEXITY_API_KEY"]
    # api_key = os.getenv("PERPLEXITY_API_KEY")
    # if not api_key:
    #     return "Error: PERPLEXITY_API_KEY not set in environment variables"
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are ResumeChecker, an expert in resume analysis and ATS optimization."},
            {"role": "user", "content": f"{prompt}\n\nResume text: {pdf_text}"}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to read PDF
def read_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        return pdf_text
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit UI
st.set_page_config(page_title="ResumeATS Pro - Powered by Perplexity AI", layout="wide")

# Custom CSS for Apple-inspired design
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f7;
        color: #1d1d1f;
    }
    .stButton>button {
        background-color: #0071e3;
        color: white;
        border-radius: 20px;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .perplexity-badge {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="perplexity-badge">⚡ Powered by Perplexity AI</div>', unsafe_allow_html=True)
st.title("ResumeATS Pro")
st.subheader("Optimize Your Resume for ATS and Land Your Dream Job")

# File upload
upload_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# Job description input
job_description = st.text_area("Enter the job description (optional)")

# Analysis options
analysis_option = st.radio("Choose analysis type:", 
                           ["Quick Scan", "Detailed Analysis", "ATS Optimization"])

if st.button("Analyze Resume"):
    if upload_file is not None:
        with st.spinner("Analyzing your resume with Perplexity AI..."):
            pdf_text = read_pdf(upload_file)
            
            if analysis_option == "Quick Scan":
                prompt = f"""
                Provide a quick scan of the following resume:
                
                1. Identify the most suitable profession for this resume.
                2. List 3 key strengths of the resume.
                3. Suggest 2 quick improvements.
                4. Give an overall ATS score out of 100.
                
                Job description (if provided): {job_description}
                """
            elif analysis_option == "Detailed Analysis":
                prompt = f"""
                Provide a detailed analysis of the following resume:
                
                1. Identify the most suitable profession for this resume.
                2. List 5 strengths of the resume.
                3. Suggest 3-5 areas for improvement with specific recommendations.
                4. Rate the following aspects out of 10: Impact, Brevity, Style, Structure, Skills.
                5. Provide a brief review of each major section (e.g., Summary, Experience, Education).
                6. Give an overall ATS score out of 100 with a breakdown of the scoring.
                
                Job description (if provided): {job_description}
                """
            else:  # ATS Optimization
                prompt = f"""
                Analyze the following resume and provide ATS optimization suggestions:
                
                1. Identify keywords from the job description that should be included in the resume.
                2. Suggest reformatting or restructuring to improve ATS readability.
                3. Recommend changes to improve keyword density without keyword stuffing.
                4. Provide 3-5 bullet points on how to tailor this resume for the specific job description.
                5. Give an ATS compatibility score out of 100 and explain how to improve it.
                
                Job description: {job_description}
                """
            
            response = get_perplexity_output(pdf_text, prompt)
            
            st.subheader("Analysis Results")
            st.write(response)
            
            # Store the analysis in session state for follow-up questions
            st.session_state['pdf_text'] = pdf_text
            st.session_state['analysis'] = response
        
        # Option to chat about the resume
        st.subheader("Have questions about your resume?")
        user_question = st.text_input("Ask me anything about your resume or the analysis:")
        if user_question and 'pdf_text' in st.session_state:
            with st.spinner("Generating response..."):
                chat_prompt = f"""
                Based on the resume and analysis provided, answer the following question:
                {user_question}
                
                Previous analysis: {st.session_state['analysis']}
                """
                chat_response = get_perplexity_output(st.session_state['pdf_text'], chat_prompt)
                st.write(chat_response)
    else:
        st.error("Please upload a resume to analyze.")

# Additional resources
st.sidebar.title("Resources")
st.sidebar.markdown("""
- [Resume Writing Tips](https://cdn-careerservices.fas.harvard.edu/wp-content/uploads/sites/161/2023/08/College-resume-and-cover-letter-4.pdf)
- [ATS Optimization Guide](https://career.io/career-advice/create-an-optimized-ats-resume)
- [Interview Preparation](https://hbr.org/2021/11/10-common-job-interview-questions-and-how-to-answer-them)
""")

# Feedback form
st.sidebar.title("Feedback")
st.sidebar.text_area("Help us improve! Leave your feedback:")
st.sidebar.button("Submit Feedback")
