import streamlit as st
import requests
import json
import base64
import re

# Streamlit app configuration
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.title("Tailor Your Resume with AI")
st.markdown("Enter a job description and a URL to your resume PDF (Google Drive normal or direct download link) to get a tailored resume (JSON format) powered by Make.com AI Agent.")

# Form for user inputs
with st.form(key="resume_form"):
    job_description = st.text_area("Job Description", placeholder="e.g., Seeking a Data Scientist with expertise in Python, SQL, and machine learning...", height=150)
    file_url = st.text_input("Resume File URL", placeholder="e.g., https://drive.google.com/file/d/your-file-id/view?usp=sharing or https://drive.google.com/uc?export=download&id=your-file-id")
    submit_button = st.form_submit_button("Tailor Resume")

# Function to convert Google Drive normal link to direct download link
def convert_google_drive_url(url):
    # Pattern for normal Google Drive link: https://drive.google.com/file/d/FILE_ID/view or /edit
    normal_pattern = r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/?(view|edit)?(\?.*)?$"
    # Pattern for direct download link: https://drive.google.com/uc?export=download&id=FILE_ID
    direct_pattern = r"https://drive\.google\.com/uc\?export=download&id=([a-zA-Z0-9_-]+)"
    
    # Check if it's a normal Google Drive link
    normal_match = re.match(normal_pattern, url)
    if normal_match:
        file_id = normal_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # Check if it's already a direct download link
    direct_match = re.match(direct_pattern, url)
    if direct_match:
        return url
    
    # If neither, return the original URL (will be validated later)
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
    st.write("Sending payload:", payload)  # Debug: Show payload
    try:
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        # Try to parse JSON, but handle non-JSON responses
        try:
            return response.json()
        except ValueError:
            return {"error": f"Invalid JSON response: {response.text}"}
    except requests.RequestException as e:
        error_msg = f"Failed to connect to Make webhook. Details: {str(e)}"
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
        # Convert Google Drive URL if necessary
        converted_url = convert_google_drive_url(file_url)
        # Check if the URL is a Google Drive link (normal or direct)
        if not ("drive.google.com" in converted_url):
            st.error("Please provide a Google Drive URL (normal or direct download link).")
        else:
            # Your Make webhook URL
            WEBHOOK_URL = "https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva"  # Replace if you have a new URL
            
            with st.spinner("Tailoring your resume..."):
                result = call_make_webhook(job_description, converted_url, WEBHOOK_URL)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Resume tailored successfully!")
                st.subheader("Tailored Resume (JSON)")
                st.json(result)
                
                # Download button for the tailored resume JSON
                result_str = json.dumps(result, indent=2)
                result_bytes = result_str.encode("utf-8")
                b64 = base64.b64encode(result_bytes).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="tailored_resume.json">Download Tailored Resume JSON</a>'
                st.markdown(href, unsafe_allow_html=True)

# Instructions for setup
st.sidebar.header("Setup Instructions")
st.sidebar.markdown("""
1. Ensure the Make.com webhook at `https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva` is active and linked to the 'Resume Tailor' scenario.
2. Update `WEBHOOK_URL` with the new webhook URL if recreated.
3. Install dependencies: `pip install streamlit requests`.
4. Run the app: `streamlit run app.py`.
5. Use a Google Drive normal link (e.g., https://drive.google.com/file/d/your-file-id/view) or direct download link (e.g., https://drive.google.com/uc?export=download&id=your-file-id).
6. Check Make.com execution logs if errors persist.
""")
