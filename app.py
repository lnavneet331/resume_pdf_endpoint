import os
import re
import json
import logging
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
from docx import Document

# Setup logging to file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Save logs to a file
        logging.StreamHandler()          # Also log to console
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
PDF_FILENAME = os.path.join(os.path.dirname(__file__), "generated_resume.pdf")
DOCX_FILENAME = os.path.join(os.path.dirname(__file__), "generated_resume.docx")
DOCX_TEMPLATE = os.path.join(os.path.dirname(__file__), "template.docx")

@app.route('/')
def home():
    logger.info('Home route accessed.')
    return 'Welcome to the Resume Generator API!'

def draw_wrapped_text(c, text, x, y, max_width, line_height):
    """Helper function to wrap long text into lines"""
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
        c.drawString(50, y, f"Resume - {data.get('name', 'Data Science Intern')}")
        y -= 30

        # Contact Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Contact Information:")
        y -= 15
        c.setFont("Helvetica", 12)
        c.drawString(70, y, f"Phone: {data.get('phone', '')}")
        y -= 15
        c.drawString(70, y, f"Email: {data.get('email', '')}")
        y -= 15
        c.drawString(70, y, f"LinkedIn: {data.get('linkedin', '')}")
        y -= 15

        # Skills
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Skills:")
        y -= 15
        c.setFont("Helvetica", 12)
        for skill in data.get("skills", []):
            c.drawString(70, y, f"- {skill}")
            y -= 15

        # Experience
        for exp in data.get("experience", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{exp.get('designation', '')} at {exp.get('company', '')} ({exp.get('dates', '')})")
            y -= 15
            c.setFont("Helvetica", 12)
            y = draw_wrapped_text(c, f"{exp.get('city', '')}", 60, y, width - 100, 15)
            y = draw_wrapped_text(c, f"- {exp.get('1stbullet', '')}", 60, y, width - 100, 15)
            y = draw_wrapped_text(c, f"- {exp.get('2ndbullet', '')}", 60, y, width - 100, 15)

        # Projects
        for project in data.get("project", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{project.get('name', '')} ({project.get('dates', '')})")
            y -= 15
            c.setFont("Helvetica", 12)
            for bullet in ['1stbullet', '2ndbullet', '3rdbullet', '4thbullet']:
                if project.get(bullet):
                    y = draw_wrapped_text(c, f"- {project.get(bullet, '')}", 60, y, width - 100, 15)
            y = draw_wrapped_text(c, f"Link: {project.get('link', '')}", 60, y, width - 100, 15)

        # Education
        for edu in data.get("education", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{edu.get('branch', '')} - CGPA: {edu.get('cgpa', '')}")
            y -= 15

        # Responsibilities
        for resp in data.get("responsibilities", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{resp.get('name', '')}, {resp.get('organization', '')}")
            y -= 15
            c.setFont("Helvetica", 12)
            y = draw_wrapped_text(c, f"- {resp.get('bullet', '')}", 60, y, width - 100, 15)

        c.save()
        logger.info(f'PDF successfully saved at: {PDF_FILENAME}')
        return PDF_FILENAME

    except Exception as e:
        logger.error(f"Exception in generate_pdf: {e}")
        raise

def generate_docx(data):
    try:
        logger.info('Generating DOCX...')
        if not os.path.exists(DOCX_TEMPLATE):
            raise FileNotFoundError("DOCX template not found")

        doc = Document(DOCX_TEMPLATE)
        replacements = {
            '{{name}}': data.get('name', ''),
            '{{phone}}': data.get('phone', ''),
            '{{email}}': data.get('email', ''),
            '{{linkedin}}': data.get('linkedin', ''),
            '{{skills}}': ', '.join(data.get('skills', [])),
            '{{certification}}': data.get('certification', ''),
            '{{experience[0].designation}}': data.get('experience', [{}])[0].get('designation', ''),
            '{{experience[0].dates}}': data.get('experience', [{}])[0].get('dates', ''),
            '{{experience[0].company}}': data.get('experience', [{}])[0].get('company', ''),
            '{{experience[0].city}}': data.get('experience', [{}])[0].get('city', ''),
            '{{experience[0].1stbullet}}': data.get('experience', [{}])[0].get('1stbullet', ''),
            '{{experience[0].2ndbullet}}': data.get('experience', [{}])[0].get('2ndbullet', ''),
            '{{project[0].name}}': data.get('project', [{}])[0].get('name', ''),
            '{{project[0].dates}}': data.get('project', [{}])[0].get('dates', ''),
            '{{project[0].1stbullet}}': data.get('project', [{}])[0].get('1stbullet', ''),
            '{{project[0].2ndbullet}}': data.get('project', [{}])[0].get('2ndbullet', ''),
            '{{project[0].3rdbullet}}': data.get('project', [{}])[0].get('3rdbullet', ''),
            '{{project[0].4thbullet}}': data.get('project', [{}])[0].get('4thbullet', ''),
            '{{project[0].link}}': data.get('project', [{}])[0].get('link', ''),
            '{{project[1].name}}': data.get('project', [{}, {}])[1].get('name', ''),
            '{{project[1].dates}}': data.get('project', [{}, {}])[1].get('dates', ''),
            '{{project[1].1stbullet}}': data.get('project', [{}, {}])[1].get('1stbullet', ''),
            '{{project[1].2ndbullet}}': data.get('project', [{}, {}])[1].get('2ndbullet', ''),
            '{{project[1].3rdbullet}}': data.get('project', [{}, {}])[1].get('3rdbullet', ''),
            '{{project[1].4thbullet}}': data.get('project', [{}, {}])[1].get('4thbullet', ''),
            '{{project[1].link}}': data.get('project', [{}, {}])[1].get('link', ''),
            '{{education[0].branch}}': data.get('education', [{}])[0].get('branch', ''),
            '{{education[0].cgpa}}': data.get('education', [{}])[0].get('cgpa', ''),
            '{{responsibilities[0].name, responsibilities[0].organization}}': f"{data.get('responsibilities', [{}])[0].get('name', '')}, {data.get('responsibilities', [{}])[0].get('organization', '')}",
            '{{responsibilities[0].bullet}}': data.get('responsibilities', [{}])[0].get('bullet', ''),
            '{{responsibilities[1].name, responsibilities[1].organization}}': f"{data.get('responsibilities', [{}, {}])[1].get('name', '')}, {data.get('responsibilities', [{}, {}])[1].get('organization', '')}",
        }

        def replace_placeholders_in_runs(doc, replacements):
            for paragraph in doc.paragraphs:
                for placeholder, replacement in replacements.items():
                    for run in paragraph.runs:
                        if placeholder in run.text:
                            run.text = run.text.replace(placeholder, str(replacement))

        replace_placeholders_in_runs(doc, replacements)
        doc.save(DOCX_FILENAME)
        logger.info(f'DOCX successfully saved at: {DOCX_FILENAME}')
        return DOCX_FILENAME

    except Exception as e:
        logger.error(f"Exception in generate_docx: {e}")
        raise

@app.route('/generate_resume', methods=['POST'])
def create_resume():
    try:
        raw_data = request.data.decode('utf-8')
        logger.debug('Raw request data: %s', raw_data)

        raw_data = re.sub(r'^(?:json)?\s*', '', raw_data)
        raw_data = re.sub(r'\s*$', '', raw_data)
        logger.debug('Cleaned request data: %s', raw_data)

        data = json.loads(raw_data)
        if not data:
            logger.warning('No JSON data after cleaning')
            return jsonify({"error": "No data provided"}), 400

        # Generate both PDF and DOCX
        pdf_file = generate_pdf(data)
        docx_file = generate_docx(data)
        return jsonify({
            "message": "Resume generated successfully!",
            "pdf_url": request.host_url.rstrip('/') + '/preview_resume?type=pdf',
            "docx_url": request.host_url.rstrip('/') + '/preview_resume?type=docx'
        }), 200

    except Exception as e:
        logger.exception("Error in /generate_resume")
        return jsonify({"error": "Resume generation failed", "details": str(e)}), 500

@app.route('/preview_resume', methods=['GET'])
def preview_resume():
    file_type = request.args.get('type', 'pdf')
    if file_type == 'pdf' and os.path.exists(PDF_FILENAME):
        logger.info('Serving generated resume PDF')
        return send_file(PDF_FILENAME, mimetype='application/pdf', as_attachment=True, download_name='resume.pdf')
    elif file_type == 'docx' and os.path.exists(DOCX_FILENAME):
        logger.info('Serving generated resume DOCX')
        return send_file(DOCX_FILENAME, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', as_attachment=True, download_name='resume.docx')
    else:
        logger.warning(f'{file_type.upper()} not found for preview')
        return jsonify({"error": f"{file_type.upper()} not found"}), 404

@app.route('/logs', methods=['GET'])
def view_logs():
    try:
        log_path = "app.log"
        if not os.path.exists(log_path):
            return jsonify({"error": "Log file not found"}), 404

        with open(log_path, 'r') as log_file:
            lines = log_file.readlines()[-100:]
            return jsonify({"log": ''.join(lines)}), 200

    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({"error": "Could not retrieve logs"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
