import streamlit as st
import requests
import json
import re

# Streamlit app configuration
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.title("Tailor Your Resume")
st.markdown("Enter a job description and a URL to your resume PDF (Google Drive normal or direct download link) to generate tailored DOCX and PDF resumes.")

# Form for user inputs
with st.form(key="resume_form"):
    job_description = st.text_area("Job Description", placeholder="e.g., Seeking a Data Scientist with expertise in Python, SQL, and machine learning...", height=150)
    file_url = st.text_input("Resume File URL", placeholder="e.g., https://drive.google.com/file/d/your-file-id/view?usp=sharing or https://drive.google.com/uc?export=download&id=your-file-id")
    submit_button = st.form_submit_button("Tailor Resume")

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

# Function to call Make webhook for tailoring resume
def call_make_webhook(job_description, file_url):
    webhook_url = "https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva"
    headers = {"Content-Type": "application/json"}
    payload = {
        "job_description": job_description,
        "file_url": file_url
    }
    st.write("Sending payload to Make webhook:", payload)  # Debug: Show payload
    try:
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"error": f"Invalid JSON response: {response.text}"}
    except requests.RequestException as e:
        error_msg = f"Failed to connect to Make webhook. Details: {str(e)}"
        if 'response' in locals():
            error_msg += f"\nResponse: {response.text}"
        return {"error": error_msg}

# Function to call Flask endpoint for generating resumes
def call_flask_endpoint(tailored_resume_json):
    flask_url = "https://resume-pdf-endpoint.onrender.com/generate_resume"
    headers = {"Content-Type": "application/json"}
    st.write("Sending tailored JSON to Flask endpoint:", tailored_resume_json)  # Debug: Show JSON
    try:
        response = requests.post(flask_url, headers=headers, json=tailored_resume_json, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_msg = f"Failed to connect to Flask endpoint. Details: {str(e)}"
        if 'response' in locals():
            error_msg += f"\nResponse: {response.text}"
        return {"error": error_msg}

# Process form submission
if submit_button:
    if not job_description or not file_url:
        st.error("Please provide both a job description and a resume file URL.")
    elif not is_valid_url(file_url):
        st.error("Please provide a valid URL starting with http:// or https://")
    else:
        converted_url = convert_google_drive_url(file_url)
        if not ("drive.google.com" in converted_url):
            st.error("Please provide a Google Drive URL (normal or direct download link).")
        else:
            with st.spinner("Tailoring and generating your resume..."):
                # Step 1: Call Make webhook to tailor resume
                tailored_result = call_make_webhook(job_description, converted_url)
                
                if "error" in tailored_result:
                    st.error(tailored_result["error"])
                else:
                    # Step 2: Send tailored JSON to Flask endpoint
                    flask_result = call_flask_endpoint(tailored_result)
                    
                    if "error" in flask_result:
                        st.error(flask_result["error"])
                    else:
                        st.success("Resume generated successfully!")
                        st.subheader("Download Your Resume")
                        
                        # Display tailored JSON for reference
                        st.json(tailored_result)
                        
                        # Download buttons for DOCX and PDF
                        col1, col2 = st.columns(2)
                        with col1:
                            if flask_result.get("docx_url"):
                                st.markdown(
                                    f'<a href="{flask_result["docx_url"]}" download="resume.docx">'
                                    '<button style="padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">'
                                    'Download DOCX</button></a>',
                                    unsafe_allow_html=True
                                )
                        with col2:
                            if flask_result.get("pdf_url"):
                                st.markdown(
                                    f'<a href="{flask_result["pdf_url"]}" download="resume.pdf">'
                                    '<button style="padding: 10px; background-color: #008CBA; color: white; border: none; border-radius: 5px; cursor: pointer;">'
                                    'Download PDF</button></a>',
                                    unsafe_allow_html=True
                                )

# Instructions for setup
st.sidebar.header("Setup Instructions")
st.sidebar.markdown("""
1. Ensure the Make.com webhook at `https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva` is active and linked to the 'Resume Tailor' scenario.
2. Ensure the Flask API is running at `https://resume-pdf-endpoint.onrender.com`.
3. Install dependencies: `pip install streamlit requests python-docx reportlab`.
4. Ensure `template.docx` is available for the Flask API for DOCX generation.
5. Run the Streamlit app: `streamlit run main.py`.
6. Use a Google Drive normal link (e.g., `https://drive.google.com/file/d/your-file-id/view`) or direct download link.
7. Check Make.com execution logs or Flask API logs if errors persist.
""")
