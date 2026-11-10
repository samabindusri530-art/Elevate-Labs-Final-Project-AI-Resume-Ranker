from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def create_pdf_report(results, report_path):

    document = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e3a8a"),
        fontSize=20,
        spaceAfter=20
    )

    story = []

    story.append(Paragraph("AI RESUME RANKING REPORT", title_style))
    story.append(Paragraph(
        "Candidate comparison and skill analysis",
        styles["Normal"]
    ))
    story.append(Spacer(1, 20))

    table_data = [
        ["Rank", "Resume Name", "Similarity", "Skill Score", "Final Score"]
    ]

    for result in results:
        table_data.append([
            str(result["rank"]),
            Paragraph(result["filename"], styles["BodyText"]),
            str(result["similarity_score"]) + "%",
            str(result["skill_score"]) + "%",
            str(result["score"]) + "%"
        ])

    table = Table(
        table_data,
        colWidths=[35, 175, 85, 85, 85],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3157a4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#eef2ff")]),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(table)
    story.append(Spacer(1, 25))

    for result in results:
        story.append(Paragraph(
            f"<b>Rank {result['rank']}: "
            f"{result['filename']}</b>",
            styles["Heading3"]
        ))

        matched = ", ".join(result["matched_skills"]) or "None"
        missing = ", ".join(result["missing_skills"]) or "None"

        story.append(Paragraph(
            f"<b>Matched Skills:</b> {matched}",
            styles["BodyText"]
        ))

        story.append(Paragraph(
            f"<b>Missing Skills:</b> {missing}",
            styles["BodyText"]
        ))

        story.append(Spacer(1, 12))

    story.append(Spacer(1, 15))

    story.append(Paragraph(
        "<b>Note:</b> Scores are decision-support indicators only. "
        "They should not be used as automatic hiring decisions. "
        "A qualified human reviewer should independently assess "
        "each application.",
        styles["BodyText"]
    ))

    document.build(story)
