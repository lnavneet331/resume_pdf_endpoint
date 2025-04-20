import streamlit as st
import requests
import json
import re
import time

# Streamlit app configuration
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.title("Resume Tailor AI")
st.markdown("Get your resume tailored specifically for your target job in just a few seconds.")

# Form for user inputs
with st.form(key="resume_form"):
    job_description = st.text_area(
        "Job Description",
        placeholder="Paste the complete job description here...",
        height=150
    )
    file_url = st.text_input(
        "Resume URL",
        placeholder="Enter Google Drive link to your resume (make sure it's set to public)"
    )
    submit_button = st.form_submit_button("Tailor My Resume")

# Function to convert Google Drive normal link to direct download link
def convert_google_drive_url(url):
    normal_pattern = r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/?(view|edit)?(\?.*)?$"
    direct_pattern = r"https://drive\.google\.com/uc\?export=download&id=([a-zA-Z0-9_-]+)"
    
    normal_match = re.match(normal_pattern, url)
    if normal_match:
        file_id = normal_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    direct_match = re.match(direct_pattern, url)
    if direct_match:
        return url
    
    return url

# Function to validate URL
def is_valid_url(url):
    return url.startswith(("https://", "http://"))

# Function to call Make webhook
def call_make_webhook(job_description, file_url, webhook_url):
    headers = {"Content-Type": "application/json"}
    payload = {
        "job_description": job_description,
        "file_url": file_url
    }
    try:
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"error": "Connection issue. Please check your internet and try again."}
    except ValueError:
        return {"error": "Invalid response. Please try again later."}

# Function to fetch resume file content
def fetch_resume_file(download_url):
    try:
        response = requests.get(download_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        return None

# Process form submission
if submit_button:
    if not job_description or not file_url:
        st.error("Please provide both a job description and a resume file URL.")
    elif not is_valid_url(file_url):
        st.error("Please provide a valid URL starting with http:// or https://")
    else:
        converted_url = convert_google_drive_url(file_url)
        if not ("drive.google.com" in converted_url):
            st.error("Please use a Google Drive link to your resume.")
        else:
            WEBHOOK_URL = "https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva"

            progress_placeholder = st.empty()
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.write("Reading your resume...")
                progress_bar.progress(25)
                time.sleep(1)

                status_text.write("Analyzing job requirements...")
                progress_bar.progress(50)
                time.sleep(1)

                status_text.write("Tailoring your resume...")
                progress_bar.progress(75)
                time.sleep(1)

                result = call_make_webhook(job_description, converted_url, WEBHOOK_URL)

                status_text.write("Finalizing your tailored resume...")
                progress_bar.progress(100)
                time.sleep(1)

            progress_placeholder.empty()

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Your resume has been successfully tailored!")

                # Assume resume is always at this URL
                download_url = "http://3.111.41.213:5000/download_resume"

                # Fetch the resume file content
                resume_file = fetch_resume_file(download_url)

                if resume_file:
                    st.download_button(
                    label="Download Your Tailored Resume",
                    data=resume_file,
                    file_name="Tailored_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
                else:
                    st.error("Failed to fetch the resume file. Please try again later.")

# Sidebar instructions
st.sidebar.header("How It Works")
st.sidebar.markdown("""
1. **Paste the job description** - Include the full text for best results  
2. **Enter your resume URL** - Must be a public Google Drive link  
3. **Click 'Tailor My Resume'** - Our AI will customize your resume for this specific job  
4. **Download your resume** - A button will appear to download your tailored resume  
""")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #888; font-size: 12px;">
Powered by AI Resume Tailoring Technology
</div>
""", unsafe_allow_html=True)
