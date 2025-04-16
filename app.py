import os
import logging
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Save PDF in the same folder as app.py
PDF_FILENAME = os.path.join(os.path.dirname(__file__), "generated_resume.pdf")

@app.route('/')
def home():
    logger.info('Home route accessed.')
    return 'Welcome to the Resume PDF Generator API!'

def generate_pdf(data):
    logger.info('Generating PDF for data: %s', data)
    
    c = canvas.Canvas(PDF_FILENAME, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Resume - Data Science Intern")

    c.setFont("Helvetica", 12)
    y = height - 130
    c.drawString(100, y, "Skills:")
    for skill in data.get("skills", []):
        y -= 15
        c.drawString(120, y, f"- {skill}")

    for section in ["internship"]:
        y -= 30
        for item in data.get(section, []):
            c.drawString(100, y, f"{item['title']} at {item['company']} ({item['dates']})")
            y -= 15
            c.drawString(110, y, item['description'])
            y -= 30

    for key in ["project_1", "project_2"]:
        project = data.get(key)
        if project:
            y -= 15
            c.drawString(100, y, f"Project: {project['name']} ({project['dates']})")
            y -= 15
            c.drawString(110, y, project['description'])
            y -= 30

    c.save()
    logger.info(f'PDF generated and saved as {PDF_FILENAME}')
    return PDF_FILENAME

@app.route('/generate_pdf', methods=['POST'])
def create_pdf():
    try:
        data = request.get_json()
        if not data:
            logger.warning('No data provided in request.')
            return jsonify({"error": "No data provided"}), 400

        logger.info('Received data: %s', data)
        generate_pdf(data)
        preview_url = request.host_url.rstrip('/') + '/preview_resume'

        logger.info('PDF generated successfully, preview URL: %s', preview_url)
        return jsonify({
            "message": "PDF generated successfully!",
            "preview_url": preview_url
        }), 200

    except Exception as e:
        logger.error('Error generating PDF: %s', str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/preview_resume', methods=['GET'])
def preview_resume():
    if os.path.exists(PDF_FILENAME):
        logger.info(f'Previewing PDF: {PDF_FILENAME}')
        return send_file(PDF_FILENAME, mimetype='application/pdf')
    else:
        logger.warning('PDF file not found: %s', PDF_FILENAME)
        return jsonify({"error": "PDF not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
