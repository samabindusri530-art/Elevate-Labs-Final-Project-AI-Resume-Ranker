
import os
import csv
import uuid
import pymupdf as fitz

from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename

from ranker import rank_resumes
from pdf_report import create_pdf_report

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allow multiple PDF files up to 100 MB in total
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

results_data = []


# EXTRACT PDF TEXT
def extract_text(pdf_path):

    text = ""

    try:
        with fitz.open(pdf_path) as document:

            for page in document:
                text += page.get_text() + "\n"

    except Exception as error:
        print("PDF ERROR:", error)

    return text.strip()


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# RESUME UPLOAD
@app.route("/upload", methods=["GET", "POST"])
def upload():

    global results_data

    if request.method == "POST":

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        files = request.files.getlist("resumes")

        print("\n========== UPLOAD DEBUG ==========")
        print("Files received:", len(files))

        if not job_description:
            return render_template(
                "upload.html",
                error="Please enter a job description."
            )

        resumes = []

        for index, file in enumerate(files, start=1):

            if not file or not file.filename:
                continue

            print(f"\nProcessing resume {index}: {file.filename}")

            if not file.filename.lower().endswith(".pdf"):
                print("Skipped: Not a PDF")
                continue

            filename = secure_filename(file.filename)

            # Unique name prevents files from overwriting each other
            unique_filename = (
                uuid.uuid4().hex[:8] + "_" + filename
            )

            file_path = os.path.join(
                UPLOAD_FOLDER,
                unique_filename
            )

            try:
                file.save(file_path)

                resume_text = extract_text(file_path)

                if resume_text:

                    resumes.append({
                        "filename": filename,
                        "text": resume_text
                    })

                    print("Successfully processed:", filename)

                else:
                    print("No readable text:", filename)

            except Exception as error:
                print("Processing error:", filename, error)

        print("\nTotal readable resumes:", len(resumes))

        if not resumes:

            return render_template(
                "upload.html",
                error="No readable PDF resumes found. Please upload valid PDFs."
            )

        # Process every resume together
        results_data = rank_resumes(
            resumes,
            job_description
        )

        print("\nTOTAL CANDIDATES RANKED:", len(results_data))

        for candidate in results_data:

            print(
                "Rank:", candidate["rank"],
                "| Name:", candidate["filename"],
                "| Score:", candidate["score"]
            )

        print("==================================\n")

        return redirect(url_for("dashboard"))

    return render_template("upload.html")


# HR DASHBOARD
@app.route("/dashboard")
def dashboard():

    total = len(results_data)

    highest = max(
        [r["score"] for r in results_data],
        default=0
    )

    average = (
        sum(r["score"] for r in results_data) / total
        if total else 0
    )

    matched = sum(
        1 for r in results_data
        if r["matched_skills"]
    )

    return render_template(
        "dashboard.html",
        total_resumes=total,
        highest_score=round(highest, 2),
        average_score=round(average, 2),
        matched_candidates=matched
    )


# CANDIDATE RANKINGS
@app.route("/rankings")
def rankings():

    return render_template(
        "rankings.html",
        results=results_data
    )


# SKILL MATCHING
@app.route("/skills")
def skills():

    return render_template(
        "skills.html",
        results=results_data
    )


# CANDIDATE MANAGEMENT
@app.route("/candidates")
def candidates():

    return render_template(
        "candidates.html",
        results=results_data
    )


# CANDIDATE TRACKING
@app.route("/tracking")
def tracking():

    return render_template("tracking.html")


# REPORTS
@app.route("/reports")
def reports():

    return render_template("reports.html")


# CSV DOWNLOAD
@app.route("/download")
def download_report():

    if not results_data:
        return "Upload resumes first.", 400

    report_path = os.path.join(
        REPORT_FOLDER,
        "resume_ranking_report.csv"
    )

    fields = [
        "rank",
        "filename",
        "similarity_score",
        "skill_score",
        "matched_skills",
        "missing_skills",
        "score"
    ]

    with open(
        report_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for result in results_data:

            row = result.copy()

            row["matched_skills"] = ", ".join(
                result["matched_skills"]
            )

            row["missing_skills"] = ", ".join(
                result["missing_skills"]
            )

            writer.writerow(row)

    return send_file(
        report_path,
        as_attachment=True
    )


# PDF DOWNLOAD
@app.route("/download-pdf")
def download_pdf():

    if not results_data:
        return "Upload resumes first.", 400

    report_path = os.path.join(
        REPORT_FOLDER,
        "resume_ranking_report.pdf"
    )

    create_pdf_report(
        results_data,
        report_path
    )

    return send_file(
        report_path,
        as_attachment=True,
        mimetype="application/pdf"
    )


if __name__ == "__main__":

    app.run(debug=True)