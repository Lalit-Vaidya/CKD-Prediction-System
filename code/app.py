import os
from flask import Flask, render_template, request, send_file
import mysql.connector
from datetime import date
import pytesseract
import cv2
import re
from app2 import generate_ckd_report

# -------- TESSERACT PATH --------
# Path where Tesseract OCR is installed (required for text extraction)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------- APP INIT --------
# Initialize Flask application
app = Flask(__name__)

# -------- BASE PATH --------
# Get current file directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------- FOLDERS --------
# Create folders for storing uploaded images and generated reports
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Configure upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- DATABASE --------
# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="ckduser",
    password="Lalit@123",
    database="ckd_db"
)
cursor = db.cursor()

# -------- HELPER FUNCTION --------
# Extract numeric value from string (used for OCR outputs)
def get_number(value):
    if value is None or value == "":
        return 0
    num = re.findall(r"\d+\.?\d*", str(value))
    return float(num[0]) if num else 0

# -------- OCR FUNCTION --------
# Extract lab values from uploaded image using OCR
def extract_lab_values(image_path):
    img = cv2.imread(image_path)

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold to improve OCR accuracy
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # Extract text from image
    text = pytesseract.image_to_string(gray)
    print("\nOCR TEXT:\n", text)

    # Function to extract text using regex
    def find_value(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""

    # Extract only first numeric value from line
    def extract_value_only(keyword):
        for line in text.split("\n"):
            if keyword.lower() in line.lower():
                numbers = re.findall(r"\d+\.?\d*", line)
                if numbers:
                    return numbers[0]
        return ""

    # Special handling for RBC (text-based)
    def extract_rbc():
        for line in text.split("\n"):
            if "rbc" in line.lower():
                if "abnormal" in line.lower():
                    return "Abnormal"
                else:
                    return "Normal"
        return ""

    # Store extracted values
    values = {
        "name": find_value(r"Patient Name[:\-]?\s*([A-Za-z ]+)"),
        "age": find_value(r"Age[:\-]?\s*(\d+)"),
        "place": find_value(r"Place\s*[:\-]?\s*([A-Za-z ]+)"),

        "bp": extract_value_only("Blood Pressure"),
        "sg": extract_value_only("Specific Gravity"),
        "albumin": extract_value_only("Albumin"),
        "sugar": extract_value_only("Sugar"),
        "glucose": extract_value_only("Glucose"),
        "urea": extract_value_only("Urea"),
        "creatinine": extract_value_only("Creatinine"),
        "hemoglobin": extract_value_only("Hemoglobin"),
        "sodium": extract_value_only("Sodium"),
        "potassium": extract_value_only("Potassium"),
        "pcv": extract_value_only("Packed Cell Volume"),
        "wbc": extract_value_only("WBC"),
        "rbc": extract_rbc()
    }

    print("\nExtracted Values:", values)
    return values

# -------- CKD STAGE --------
# Determine CKD stage based on creatinine value
def get_ckd_stage(creatinine):
    if creatinine <= 1.2:
        return "Stage 1"
    elif creatinine <= 1.8:
        return "Stage 2"
    elif creatinine <= 3.0:
        return "Stage 3"
    elif creatinine <= 5.0:
        return "Stage 4"
    else:
        return "Stage 5"

# -------- STAGE DETAILS --------
# Provide description and preventive measures for each stage
def get_stage_details(stage):
    details = {
        "Stage 1": {
            "desc": "Early kidney damage with normal kidney function.",
            "precautions": [
                "Control blood pressure",
                "Maintain blood sugar",
                "Drink enough water",
                "Reduce salt intake",
                "Regular health checkups"
            ]
        },
        "Stage 2": {
            "desc": "Mild kidney damage with slight loss of function.",
            "precautions": [
                "Low salt diet",
                "Avoid painkillers",
                "Stay hydrated",
                "Monitor kidney health",
                "Control diabetes"
            ]
        },
        "Stage 3": {
            "desc": "Moderate kidney damage with waste buildup.",
            "precautions": [
                "Limit protein intake",
                "Control BP and sugar",
                "Avoid smoking",
                "Kidney-friendly diet",
                "Doctor consultation"
            ]
        },
        "Stage 4": {
            "desc": "Severe kidney damage with high risk.",
            "precautions": [
                "Strict diet",
                "Fluid control",
                "Regular tests",
                "Prepare for dialysis",
                "Avoid potassium foods"
            ]
        },
        "Stage 5": {
            "desc": "Kidney failure requiring treatment.",
            "precautions": [
                "Start dialysis",
                "Consider transplant",
                "Strict diet",
                "Take medicines",
                "Continuous monitoring"
            ]
        }
    }
    return details[stage]

# -------- HOME PAGE --------
# Load homepage with empty values
@app.route('/')
def index():
    empty_values = {key: "" for key in [
        "name","age","place","bp","sg","albumin","sugar","glucose","urea",
        "creatinine","hemoglobin","sodium","potassium","pcv","wbc","rbc"
    ]}
    return render_template('index.html', values=empty_values)

# -------- FILE UPLOAD --------
# Upload lab report and extract values using OCR
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['lab_report']
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    values = extract_lab_values(filepath)
    return render_template("index.html", values=values)

# -------- PREDICTION --------
# Predict CKD stage and generate report
@app.route('/predict', methods=['POST'])
def predict():

    # Get form data
    name = request.form.get('name') or "N/A"
    age = request.form.get('age') or "N/A"
    place = request.form.get('place') or "N/A"

    bp = request.form.get('bp') or "-"
    sg = request.form.get('sg') or "-"
    albumin = request.form.get('albumin') or "-"
    sugar = request.form.get('sugar') or "-"
    glucose = request.form.get('glucose') or "-"
    urea = request.form.get('urea') or "-"
    creatinine = request.form.get('creatinine') or "-"
    hemoglobin = request.form.get('hemoglobin') or "-"

    sodium = request.form.get('sodium') or "-"
    potassium = request.form.get('potassium') or "-"
    pcv = request.form.get('pcv') or "-"
    wbc = request.form.get('wbc') or "-"
    rbc = request.form.get('rbc') or "-"

    # Convert creatinine to numeric
    creatinine_val = get_number(creatinine)

    # Get stage and details
    stage = get_ckd_stage(creatinine_val)
    details = get_stage_details(stage)

    # Determine risk level
    if creatinine_val > 5:
        risk = "HIGH RISK - STAGE 5 CKD"
    elif creatinine_val > 3:
        risk = "MEDIUM RISK - STAGE 4 CKD"
    elif creatinine_val > 2:
        risk = "MEDIUM RISK - STAGE 3 CKD"
    elif creatinine_val > 1.2:
        risk = "LOW RISK - STAGE 2 CKD"
    else:
        risk = "LOW RISK - STAGE 1 CKD"

    # -------- DATABASE INSERT --------
    sql = """INSERT INTO patients 
    (name, age, bp, albumin, sugar, glucose, urea, creatinine, hemoglobin, prediction, risk_level, test_date)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    values_db = (
        name, age,
        get_number(bp), get_number(albumin), get_number(sugar),
        get_number(glucose), get_number(urea), creatinine_val,
        get_number(hemoglobin),
        stage, risk, date.today()
    )

    cursor.execute(sql, values_db)
    db.commit()

    # -------- GENERATE PDF REPORT --------
    file_name = generate_ckd_report(
        name=name, age=age, place=place,
        bp=bp, sg=sg, albumin=albumin, sugar=sugar,
        glucose=glucose, urea=urea, creatinine=creatinine,
        sodium=sodium, potassium=potassium,
        hemoglobin=hemoglobin, pcv=pcv, wbc=wbc, rbc=rbc,
        risk=risk, stage=stage, details=details
    )

    return send_file(file_name, as_attachment=True)

# -------- RUN APP --------
if __name__ == '__main__':
    app.run(debug=True)