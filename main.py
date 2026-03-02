import streamlit as st
from latex import build_pdf

st.set_page_config(page_title="LaTeX to PDF", page_icon="📄")
st.title("📄 LaTeX to PDF Converter")

latex_input = st.text_area(
    "Enter LaTeX Code:",
    height=400,
    placeholder=r"""\documentclass{article}
\begin{document}
Hello World!
\end{document}"""
)

if st.button("Submit", type="primary"):
    if latex_input.strip():
        try:
            with st.spinner("Generating PDF..."):
                pdf = build_pdf(latex_input)
                pdf_bytes = bytes(pdf)

            st.success("✅ PDF ready!")
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="document.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("❌ Failed to generate PDF")
            st.code(str(e))
    else:
        st.warning("Please enter LaTeX code first.")
