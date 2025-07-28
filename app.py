from flask import Flask, render_template, request, session, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import os
import json
import io
import pandas as pd

#  OCR and entity extraction modules

from extract_entities import extract_entities
from groq import extract_invoice_info_from_image
from new_ocr import (
    detect_file_type,
    extract_text_from_readable_pdf_bytes,
    extract_text_from_unreadable_pdf_bytes,
    extract_text_from_image_file
)

# CONFIG
UPLOAD_FOLDER = "uploads"
POPPLER_PATH = r"C:/Users/Ishwar/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin"

# Ensure upload dir exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Init Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'

# Convert PDF to PIL image
def convert_pdf_to_image(pdf_path):
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    return pages[0]

# Extract text using pytesseract OCR
def extract_text_from_image(pil_image):
    import pytesseract
    return pytesseract.image_to_string(pil_image)

@app.route("/", methods=["GET", "POST"])
def index():
    error_message = ""
    raw_text = ""
    extracted_data = None

    if request.method == "POST":
        file = request.files.get("file")
        method = request.form.get("method")

        if not file or file.filename == "":
            error_message = " No file selected"
        elif not method:
            error_message = " No extraction method selected"
        else:
            try:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                file_bytes = file.read()
                file.seek(0)

                if method == "normal":
                    file_type = detect_file_type(file_ext, file_bytes)

                    if file_type == "readable_pdf":
                        raw_text = extract_text_from_readable_pdf_bytes(file_bytes)
                    elif file_type == "scanned_pdf":
                        raw_text = extract_text_from_unreadable_pdf_bytes(file_bytes)
                    elif file_type == "image":
                        pil_image = Image.open(file).convert("RGB")
                        raw_text = extract_text_from_image_file(pil_image)
                    else:
                        error_message = " Unsupported or unrecognized file type"

                    extracted_data = extract_entities(raw_text)

                elif method == "groq":
                    extracted_data = extract_invoice_info_from_image(file_bytes, file_ext)
                else:
                    error_message = " Invalid extraction method selected"

            except Exception as e:
                error_message = f" Error: {str(e)}"

    # Store in session for download
    if extracted_data:
        session['extracted_data'] = extracted_data

    return render_template("index.html", error_message=error_message, raw_text=raw_text, extracted_data=extracted_data)


# download output as csv or excel 
@app.route("/download_csv")
def download_csv():
    data = session.get("extracted_data")
    if not data:
        return "No data available to download.", 400

    if isinstance(data, dict) and "line_items" in data:
        df = pd.DataFrame(data["line_items"])
    else:
        df = pd.DataFrame([data])

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="invoice_data.csv")

@app.route("/download_excel")
def download_excel():
    data = session.get("extracted_data")
    if not data:
        return "No data available to download.", 400

    if isinstance(data, dict) and "line_items" in data:
        df = pd.DataFrame(data["line_items"])
    else:
        df = pd.DataFrame([data])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="InvoiceData")
    output.seek(0)

    return send_file(output,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True,
                     download_name="invoice_data.xlsx")

if __name__ == "__main__":
    app.run(debug=True)
