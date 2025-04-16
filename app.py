from flask import Flask, request, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

app = Flask(__name__)

def generate_pdf(data):
    # Create a PDF file
    filename = "generated_resume.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Resume - Data Science Intern")
    
    # Add skills
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Skills:")
    y_position = height - 145
    for skill in data["skills"]:
        c.drawString(100, y_position, f"- {skill}")
        y_position -= 15

    # Add Internship Experience
    c.drawString(100, y_position - 10, "Internship Experience:")
    y_position -= 25
    for internship in data["internship"]:
        c.drawString(100, y_position, f"Company: {internship['company']}")
        y_position -= 15
        c.drawString(100, y_position, f"Title: {internship['title']}")
        y_position -= 15
        c.drawString(100, y_position, f"Dates: {internship['dates']}")
        y_position -= 15
        c.drawString(100, y_position, f"Description: {internship['description']}")
        y_position -= 30

    # Add Project Experience
    c.drawString(100, y_position - 10, "Project Experience:")
    y_position -= 25
    for project in [data["project_1"], data["project_2"]]:
        c.drawString(100, y_position, f"Project: {project['name']}")
        y_position -= 15
        c.drawString(100, y_position, f"Dates: {project['dates']}")
        y_position -= 15
        c.drawString(100, y_position, f"Description: {project['description']}")
        y_position -= 30

    # Save the PDF
    c.save()
    return filename

@app.route('/generate_pdf', methods=['POST'])
def create_pdf():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Generate PDF
        filename = generate_pdf(data)
        return jsonify({"message": f"PDF generated successfully!", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if PORT not set
    app.run(host='0.0.0.0', port=port)
