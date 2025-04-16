from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

def generate_pdf(data):
    filename = "/tmp/generated_resume.pdf"  # Render allows write access to /tmp
    c = canvas.Canvas(filename, pagesize=letter)
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
    return filename

@app.route('/generate_pdf', methods=['POST'])
def create_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        pdf_path = generate_pdf(data)

        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='generated_resume.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
