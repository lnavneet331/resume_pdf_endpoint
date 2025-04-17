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
    try:
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        # Try to parse JSON, but handle non-JSON responses
        try:
            return response.json()
        except ValueError:
            return {"error": "Could not process the response. Please try again."}
    except requests.RequestException as e:
        return {"error": "Connection issue. Please check your internet and try again."}

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
            st.error("Please use a Google Drive link to your resume.")
        else:
            # Your Make webhook URL
            WEBHOOK_URL = "https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva"
            
            # Display progress
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress stages
                status_text.write("Reading your resume...")
                progress_bar.progress(25)
                time.sleep(1)
                
                status_text.write("Analyzing job requirements...")
                progress_bar.progress(50)
                time.sleep(1)
                
                status_text.write("Tailoring your resume...")
                progress_bar.progress(75)
                time.sleep(1)
                
                # Make the actual API call
                result = call_make_webhook(job_description, converted_url, WEBHOOK_URL)
                
                status_text.write("Finalizing your tailored resume...")
                progress_bar.progress(100)
                time.sleep(1)
            
            # Clear the progress display
            progress_placeholder.empty()
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Your resume has been successfully tailored!")
                
                # Extract the download URL from the response
                download_url = result.get("download_url", "")
                
                if download_url:
                    # Create a direct download button using HTML
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 25px; margin-bottom: 30px;">
                        <a href="{download_url}" 
                           target="_blank"
                           style="background-color: #4CAF50; 
                                  color: white; 
                                  padding: 12px 24px; 
                                  text-align: center; 
                                  text-decoration: none; 
                                  display: inline-block; 
                                  font-size: 16px; 
                                  margin: 4px 2px; 
                                  border-radius: 8px;">
                            Download Your Resume
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add informational text about what to expect
                    st.info("Click the button above to download your tailored resume document.")
                else:
                    st.error("No download URL was provided in the response. Please try again.")

# Simple instructions in the sidebar
st.sidebar.header("How It Works")
st.sidebar.markdown("""
1. **Paste the job description** - Include the full text for best results
2. **Enter your resume URL** - Must be a public Google Drive link
3. **Click 'Tailor My Resume'** - Our AI will customize your resume for this specific job
4. **Download your resume** - Click the download button to get your tailored resume
""")

# Add a footer with minimal attribution
st.markdown("""
---
<div style="text-align: center; color: #888; font-size: 12px;">
Powered by AI Resume Tailoring Technology
</div>
""", unsafe_allow_html=True)