import os
import requests
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

def generate_pdf(data):
    filename = "/tmp/generated_resume.pdf"
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

        # Upload to file.io
        with open(pdf_path, 'rb') as f:
            response = requests.post("https://file.io", files={'file': f})
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return jsonify({
                    "message": "PDF generated and uploaded successfully!",
                    "download_url": result["link"]
                }), 200
            else:
                return jsonify({"error": "Failed to upload to file.io", "details": result}), 500
        else:
            return jsonify({"error": "File upload failed", "status_code": response.status_code}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
