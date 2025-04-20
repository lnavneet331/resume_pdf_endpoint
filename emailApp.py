import streamlit as st
import requests
import re

st.set_page_config(layout="wide")
st.title("Resume Matcher")

# Input fields
job_description = st.text_area("Paste the Job Description")
resume_link = st.text_input("Enter the Resume Link (publicly accessible)")

def extract_sections(text):
    """
    Extracts verdict, reasoning, and response blocks.
    """
    # Extract Verdict
    verdict_match = re.search(r"\*\*Verdict:\*\*\s*(.+)", text)
    verdict = verdict_match.group(1).strip() if verdict_match else "Not found"

    # Extract Reasoning
    reasoning_match = re.search(r"\*\*Reasoning:\*\*\s*(.+?)(?=Response A:)", text, re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else "Not found"

    # Extract Responses A and B
    pattern = r"Response\s([A-Z]):\s*\n\nsubject:\s(.+?)\n\ncontent:\n\n(.+?)(?=(\n\nResponse [A-Z]:|$))"
    matches = re.findall(pattern, text, re.DOTALL)

    responses = []
    for match in matches:
        _, subject, content, _ = match
        responses.append({
            "subject": subject.strip(),
            "content": content.strip()
        })

    return verdict, reasoning, responses

# Submit button
if st.button("Submit"):
    if not job_description or not resume_link:
        st.warning("Please enter both job description and resume link.")
    else:
        payload = {
            "job_description": job_description,
            "resume_link": resume_link
        }

        try:
            response = requests.post(
                "https://hook.eu2.make.com/0l6wfbrd2jtogw04bf4iz2cy9w4f57oo",
                json=payload
            )
            response.raise_for_status()

            if response.text:
                # Extract sections
                verdict, reasoning, responses = extract_sections(response.text)

                # Show verdict and reasoning
                st.success("🧠 AI Verdict & Reasoning")
                st.markdown(f"**Verdict:** {verdict}")
                st.markdown(f"**Reasoning:** {reasoning}")

                # Show responses A & B
                if len(responses) >= 2:
                    st.divider()
                    col1, col2 = st.columns(2)
                    for i, col in enumerate([col1, col2]):
                        r = responses[i]
                        with col:
                            st.subheader(f"Response {'A' if i == 0 else 'B'}")

                            st.markdown("**Subject:**")
                            st.code(r["subject"], language="text")
                            if st.button(f"📋 Copy Subject {'A' if i == 0 else 'B'}", key=f"copy_subject_{i}"):
                                st.session_state[f"copied_subject_{i}"] = r["subject"]
                                st.toast("Copied!", icon="✅")

                            st.markdown("**Content:**")
                            st.text_area(f"Content {'A' if i == 0 else 'B'}", r["content"], height=250, key=f"content_display_{i}")
                            if st.button(f"📋 Copy Content {'A' if i == 0 else 'B'}", key=f"copy_content_{i}"):
                                st.session_state[f"copied_content_{i}"] = r["content"]
                                st.toast("Copied!", icon="✅")
                else:
                    st.warning("Could not parse both responses. Showing raw output:")
                    st.text_area("Raw Response", response.text, height=400)

                # Show full webhook response in an expander
                with st.expander("📦 Full Raw Webhook Response"):
                    st.text_area("Raw Response", response.text, height=300)

            else:
                st.warning("Received an empty response from the webhook.")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
