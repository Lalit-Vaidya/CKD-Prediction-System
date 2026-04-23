import os
import random
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors


# -------- BASE PATH --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


# -------- BORDER --------
def draw_border(canvas, doc):
    width, height = letter
    margin = 20
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(2)
    canvas.rect(margin, margin, width - 2 * margin, height - 2 * margin)


def generate_ckd_report(
    name=None, age=None, place=None,
    bp=None, sg=None, albumin=None, sugar=None, glucose=None, urea=None, creatinine=None,
    sodium=None, potassium=None, hemoglobin=None, pcv=None, wbc=None, rbc=None,
    risk=None, stage=None, details=None
):

    # -------- SAFE FILE NAME --------
    safe_name = str(name).replace(" ", "_")
    file_name = os.path.join(REPORT_DIR, f"CKD_{safe_name}.pdf")

    report_id = "CKD" + str(random.randint(1000, 9999))
    patient_id = "PID" + str(random.randint(1000, 9999))

    pdf = SimpleDocTemplate(file_name, pagesize=letter)

    styles = getSampleStyleSheet()

    # -------- CUSTOM STYLES --------
    if 'MyTitle' not in styles:
        styles.add(ParagraphStyle(name='MyTitle', alignment=TA_CENTER, fontSize=20, textColor=colors.darkblue))

    if 'MySubTitle' not in styles:
        styles.add(ParagraphStyle(name='MySubTitle', alignment=TA_CENTER, fontSize=10))

    if 'MyRight' not in styles:
        styles.add(ParagraphStyle(name='MyRight', alignment=TA_RIGHT, fontSize=10, leading=14))

    if 'MySection' not in styles:
        styles.add(ParagraphStyle(name='MySection', fontSize=13, textColor=colors.darkblue, spaceAfter=6))

    if 'MyText' not in styles:
        styles.add(ParagraphStyle(name='MyText', fontSize=11))

    if 'MyGreen' not in styles:
        styles.add(ParagraphStyle(name='MyGreen', fontSize=12, textColor=colors.green))

    if 'MyRed' not in styles:
        styles.add(ParagraphStyle(name='MyRed', fontSize=12, textColor=colors.red))

    content = []

    # -------- HEADER --------
    content.append(Spacer(1, 10))
    content.append(Paragraph("CITY CARE HOSPITAL & DIAGNOSTIC CENTER", styles['MyTitle']))
    content.append(Spacer(1, 4))
    content.append(Paragraph("Ichalkaranji, Maharashtra | 9876543210", styles['MySubTitle']))
    content.append(Spacer(1, 6))

    doctor_info = """
    <b>Dr. Amit Patil</b><br/>
    MD (Nephrology)<br/>
    Kidney Specialist
    """
    content.append(Paragraph(doctor_info, styles['MyRight']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Chronic Kidney Disease Medical Report", styles['MySection']))
    content.append(Spacer(1, 10))

    # -------- PATIENT TABLE --------
    patient_table = Table([
        ["Patient ID", patient_id, "Report ID", report_id],
        ["Name", name, "Visit Date", str(date.today())],
        ["Age", age, "Place", place]
    ], colWidths=[100, 150, 100, 150])

    patient_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    content.append(patient_table)
    content.append(Spacer(1, 15))

    # -------- LAB TABLE --------
    content.append(Paragraph("Laboratory Test Results", styles['MySection']))

    lab_data = [
        ["Test", "Result", "Normal Range"],
        ["Blood Pressure", bp, "80–120 mmHg"],
        ["Specific Gravity", sg, "1.005–1.025"],
        ["Albumin", albumin, "3.5–5.0 g/dL"],
        ["Sugar", sugar, "0–5 mg/dL"],
        ["Glucose", glucose, "70–140 mg/dL"],
        ["Urea", urea, "15–40 mg/dL"],
        ["Creatinine", creatinine, "0.6–1.2 mg/dL"],
        ["Sodium", sodium, "135–145 mmol/L"],
        ["Potassium", potassium, "3.5–5.0 mmol/L"],
        ["Hemoglobin", hemoglobin, "12–16 g/dL"],
        ["PCV", pcv, "36–46 %"],
        ["WBC", wbc, "4000–11000"],
        ["RBC", rbc, "Normal"]
    ]

    lab_table = Table(lab_data, colWidths=[180, 120, 150])

    lab_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    content.append(lab_table)
    content.append(Spacer(1, 15))

    # -------- RISK --------
    stage_num = int(stage.split()[-1])
    risk_style = styles['MyGreen'] if stage_num <= 2 else styles['MyRed']

    content.append(Paragraph(f"<b>Risk Level:</b> {risk}", risk_style))
    content.append(Paragraph(f"<b>CKD Stage:</b> {stage}", styles['MyText']))
    content.append(Spacer(1, 10))

    # -------- DESCRIPTION --------
    content.append(Paragraph("<b>Description:</b>", styles['MySection']))
    content.append(Paragraph(details['desc'], styles['MyText']))
    content.append(Spacer(1, 10))

    # -------- PREVENTIVE --------
    content.append(Paragraph("Preventive Measures", styles['MySection']))
    content.append(Spacer(1, 6))

    for p in details['precautions']:
        content.append(Paragraph("• " + p, styles['MyText']))
        content.append(Spacer(1, 4))

    content.append(Spacer(1, 25))

    # Signature
    content.append(Paragraph("Dr. Amit Patil", styles['MyRight']))
    content.append(Paragraph("Signature: ____________________", styles['MyRight']))

    # -------- BUILD --------
    pdf.build(content, onFirstPage=draw_border, onLaterPages=draw_border)

    return file_name