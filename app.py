import os
import re
import json
import logging
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
from docx import Document

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
BASE_DIR = os.path.dirname(__file__)
PDF_FILENAME = os.path.join(BASE_DIR, "generated_resume.pdf")
DOCX_FILENAME = os.path.join(BASE_DIR, "generated_resume.docx")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.docx")


def draw_wrapped_text(c, text, x, y, max_width, line_height):
    lines = wrap(text, width=95)
    for line in lines:
        if y <= 50:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 12)
        c.drawString(x, y, line)
        y -= line_height
    return y


def generate_pdf(data):
    try:
        logger.info('Generating PDF...')
        c = canvas.Canvas(PDF_FILENAME, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Resume - Data Science Intern")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Skills:")
        y -= 15
        c.setFont("Helvetica", 12)
        for skill in data.get("skills", []):
            c.drawString(70, y, f"- {skill}")
            y -= 15

        for internship in data.get("internship", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{internship.get('title', '')} at {internship.get('company', '')} ({internship.get('dates', '')})")
            y -= 15
            c.setFont("Helvetica", 12)
            y = draw_wrapped_text(c, internship.get("description", ""), 60, y, width - 100, 15)

        for key in ["project_1", "project_2"]:
            project = data.get(key)
            if project:
                y -= 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"{project.get('project_name', '')} ({project.get('dates', '')})")
                y -= 15
                c.setFont("Helvetica", 12)
                y = draw_wrapped_text(c, project.get("description", ""), 60, y, width - 100, 15)

        c.save()
        logger.info(f'PDF saved at {PDF_FILENAME}')
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise


def generate_docx(data):
    try:
        logger.info("Generating DOCX...")
        doc = Document(TEMPLATE_PATH)

        replacements = {
            '{{name}}': data['name'],
            '{{phone}}': data['phone'],
            '{{email}}': data['email'],
            '{{linkedin}}': data['linkedin'],
            '{{skills}}': ', '.join(data['skills']),
            '{{certification}}': data['certification'],
            '{{experience[0].designation}}': data['experience'][0]['designation'],
            '{{experience[0].dates}}': data['experience'][0]['dates'],
            '{{experience[0].company}}': data['experience'][0]['company'],
            '{{experience[0].city}}': data['experience'][0]['city'],
            '{{experience[0].1stbullet}}': data['experience'][0]['1stbullet'],
            '{{experience[0].2ndbullet}}': data['experience'][0]['2ndbullet'],
            '{{project[0].name}}': data['project'][0]['name'],
            '{{project[0].dates}}': data['project'][0]['dates'],
            '{{project[0].1stbullet}}': data['project'][0]['1stbullet'],
            '{{project[0].2ndbullet}}': data['project'][0]['2ndbullet'],
            '{{project[0].3dbullet}}': data['project'][0]['3dbullet'],
            '{{project[0].4thbullet}}': data['project'][0]['4thbullet'],
            '{{project[0].link}}': data['project'][0]['link'],
            '{{project[1].name}}': data['project'][1]['name'],
            '{{project[1].dates}}': data['project'][1]['dates'],
            '{{project[1].1stbullet}}': data['project'][1]['1stbullet'],
            '{{project[1].2ndbullet}}': data['project'][1]['2ndbullet'],
            '{{project[1].3dbullet}}': data['project'][1]['3dbullet'],
            '{{project[1].4thbullet}}': data['project'][1]['4thbullet'],
            '{{project[1].link}}': data['project'][1]['link'],
            '{{education[0].branch}}': data['education'][0]['branch'],
            '{{education[0].cgpa}}': data['education'][0]['cgpa'],
            '{{responsibilities[0].name, responsibilities[0].organization}}': f"{data['responsibilities'][0]['name']}, {data['responsibilities'][0]['organization']}",
            '{{responsibilities[0].bullet}}': data['responsibilities'][0]['bullet'],
            '{{responsibilities[1].name, responsibilities[1].organization}}': f"{data['responsibilities'][1]['name']}, {data['responsibilities'][1]['organization']}",
        }

        for paragraph in doc.paragraphs:
            for placeholder, replacement in replacements.items():
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, replacement)

        doc.save(DOCX_FILENAME)
        logger.info(f'DOCX saved at {DOCX_FILENAME}')
    except Exception as e:
        logger.error(f"Error generating DOCX: {e}")
        raise


@app.route('/')
def home():
    return 'Welcome to the Resume Generator API!'


@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    try:
        raw_data = request.data.decode('utf-8')
        raw_data = re.sub(r'^```(?:json)?\s*', '', raw_data)
        raw_data = re.sub(r'\s*```$', '', raw_data)
        data = json.loads(raw_data)

        if not data:
            return jsonify({"error": "No data provided"}), 400

        generate_pdf(data)
        generate_docx(data)

        base_url = request.host_url.rstrip('/')
        return jsonify({
            "message": "Resume generated successfully!",
            "pdf_url": f"{base_url}/download_pdf",
            "docx_url": f"{base_url}/download_docx"
        }), 200

    except Exception as e:
        logger.exception("Resume generation failed")
        return jsonify({"error": "Resume generation failed", "details": str(e)}), 500


@app.route('/download_pdf')
def download_pdf():
    if os.path.exists(PDF_FILENAME):
        return send_file(PDF_FILENAME, as_attachment=True)
    return jsonify({"error": "PDF not found"}), 404


@app.route('/download_docx')
def download_docx():
    if os.path.exists(DOCX_FILENAME):
        return send_file(DOCX_FILENAME, as_attachment=True)
    return jsonify({"error": "DOCX not found"}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
