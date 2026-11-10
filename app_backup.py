import os
import fitz
import csv
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from ranker import rank_resumes

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

results_data = []


def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as document:
        for page in document:
            text += page.get_text()
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    global results_data

    if request.method == "POST":
        job_description = request.form.get("job_description", "").strip()
        files = request.files.getlist("resumes")

        if not job_description or not files:
            return render_template(
                "index.html",
                error="Enter a job description and upload PDF resumes."
            )

        resumes = []

        for file in files:
            if file and file.filename.lower().endswith(".pdf"):
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)

                text = extract_text(path)

                if text.strip():
                    resumes.append({
                        "filename": filename,
                        "text": text
                    })

        if not resumes:
            return render_template(
                "index.html",
                error="No readable PDF resumes found."
            )

        results_data = rank_resumes(resumes, job_description)

        return render_template("results.html", results=results_data)

    return render_template("index.html")


@app.route("/download")
def download_report():
    if not results_data:
        return "No ranking results available. Upload resumes first.", 400

    report_path = os.path.join(REPORT_FOLDER, "resume_ranking_report.csv")

    with open(report_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["rank", "filename", "score"]
        )
        writer.writeheader()
        writer.writerows(results_data)

    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
