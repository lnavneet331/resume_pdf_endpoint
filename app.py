import os
import re
import json
import logging
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap

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


@app.route('/')
def home():
    logger.info('Home route accessed.')
    return 'Welcome to the Resume PDF Generator API!'


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
        c.drawString(50, y, "Resume - Data Science Intern")
        y -= 30

        # Skills
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Skills:")
        y -= 15
        c.setFont("Helvetica", 12)
        for skill in data.get("skills", []):
            c.drawString(70, y, f"- {skill}")
            y -= 15

        # Internships
        for internship in data.get("internship", []):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{internship.get('title', '')} at {internship.get('company', '')} ({internship.get('dates', '')})")
            y -= 15
            c.setFont("Helvetica", 12)
            y = draw_wrapped_text(c, internship.get("description", ""), 60, y, width - 100, 15)

        # Projects
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
        logger.info(f'PDF successfully saved at: {PDF_FILENAME}')
        return PDF_FILENAME

    except Exception as e:
        logger.error(f"Exception in generate_pdf: {e}")
        raise


@app.route('/generate_pdf', methods=['POST'])
def create_pdf():
    try:
        # Read raw request body
        raw_data = request.data.decode('utf-8')
        logger.debug('Raw request data: %s', raw_data)

        # Strip markdown code fences if present
        raw_data = re.sub(r'^```(?:json)?\s*', '', raw_data)
        raw_data = re.sub(r'\s*```$', '', raw_data)
        logger.debug('Cleaned request data: %s', raw_data)

        # Parse JSON
        data = json.loads(raw_data)
        if not data:
            logger.warning('No JSON data after cleaning')
            return jsonify({"error": "No data provided"}), 400

        # Generate PDF from cleaned JSON
        generate_pdf(data)
        preview_url = request.host_url.rstrip('/') + '/preview_resume'
        return jsonify({
            "message": "PDF generated successfully!",
            "preview_url": preview_url
        }), 200

    except Exception as e:
        logger.exception("Error in /generate_pdf")
        return jsonify({"error": "PDF generation failed", "details": str(e)}), 500


@app.route('/preview_resume', methods=['GET'])
def preview_resume():
    if os.path.exists(PDF_FILENAME):
        logger.info('Serving generated resume PDF')
        return send_file(PDF_FILENAME, mimetype='application/pdf')
    else:
        logger.warning('PDF not found for preview')
        return jsonify({"error": "PDF not found"}), 404


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
