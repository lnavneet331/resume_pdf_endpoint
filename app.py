import os
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Save PDF in the same folder as app.py
PDF_FILENAME = os.path.join(os.path.dirname(__file__), "generated_resume.pdf")


from flask import request, jsonify
from functools import wraps

API_KEY = 'smart-nav'  # Replace with your actual API key

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key and key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    return decorated


@app.route('/')
@require_api_key
def home():
    return 'Welcome to the Resume PDF Generator API!'
    
def generate_pdf(data):
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
    return PDF_FILENAME

@app.route('/generate_pdf', methods=['POST'])
def create_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        generate_pdf(data)
        preview_url = request.host_url.rstrip('/') + '/preview_resume'

        return jsonify({
            "message": "PDF generated successfully!",
            "preview_url": preview_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preview_resume', methods=['GET'])
def preview_resume():
    if os.path.exists(PDF_FILENAME):
        return send_file(PDF_FILENAME, mimetype='application/pdf')
    else:
        return jsonify({"error": "PDF not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
