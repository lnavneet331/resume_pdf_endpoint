import streamlit as st
import requests
import json
import base64

# Streamlit app configuration
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.title("Tailor Your Resume with AI")
st.markdown("Enter a job description and a URL to your resume PDF to get a tailored resume (JSON format) powered by Make.com AI Agent.")

# Form for user inputs
with st.form(key="resume_form"):
    job_description = st.text_area("Job Description", placeholder="e.g., Seeking a Data Scientist with expertise in Python, SQL, and machine learning...", height=150)
    file_url = st.text_input("Resume File URL", placeholder="e.g., https://drive.google.com/uc?export=download&id=your-file-id")
    submit_button = st.form_submit_button("Tailor Resume")

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
        return response.json()
    except requests.RequestException as e:
        error_msg = f"Failed to connect to Make webhook. Details: {str(e)}"
        if 'response' in locals():
            error_msg += f"\nResponse: {response.text}"
        return {"error": error_msg}

# Process form submission
if submit_button:
    if not job_description or not file_url:
        st.error("Please provide both a job description and a resume file URL.")
    elif not file_url.startswith(("https://", "http://")):
        st.error("Please provide a valid URL starting with http:// or https://")
    else:
        # Your Make webhook URL
        WEBHOOK_URL = "https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva"
        
        with st.spinner("Tailoring your resume..."):
            result = call_make_webhook(job_description, file_url, WEBHOOK_URL)
        
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
1. Ensure the Make.com webhook at `https://hook.eu2.make.com/62o1ojangdlx7mlddd2ayq2r6wbk5rva` expects `job_description` and `file_url`.
2. Install dependencies: `pip install streamlit requests`.
3. Run the app: `streamlit run app.py`.
4. Use a direct download URL for the resume PDF (e.g., Google Drive direct link).
5. Check Make.com execution logs if errors persist.
""")
