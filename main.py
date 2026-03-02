import streamlit as st
import subprocess
import tempfile
import os

def latex_to_pdf(latex_content: str) -> bytes:
    """Convert LaTeX string to PDF bytes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file = os.path.join(temp_dir, "document.tex")
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
            capture_output=True,
            text=True,
            cwd=temp_dir
        )

        pdf_path = os.path.join(temp_dir, "document.pdf")

        if result.returncode != 0 or not os.path.exists(pdf_path):
            raise Exception(result.stdout + "\n" + result.stderr)

        with open(pdf_path, 'rb') as f:
            return f.read()


# ─── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="LaTeX to PDF", page_icon="📄")
st.title("📄 LaTeX to PDF Converter")

# Text input
latex_input = st.text_area(
    "Enter LaTeX Code:",
    height=400,
    placeholder=r"""\documentclass{article}
\begin{document}
Hello World!
\end{document}"""
)

# Submit button
if st.button("Submit", type="primary"):
    if latex_input.strip():
        try:
            with st.spinner("Generating PDF..."):
                pdf_bytes = latex_to_pdf(latex_input)
            
            st.success("✅ PDF ready!")
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="document.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("❌ Failed to generate PDF")
            st.code(str(e))
    else:
        st.warning("Please enter LaTeX code first")
