# 🧾 InvoSight – AI-Powered Invoice Data Extractor

**InvoSight** is a lightweight and intelligent web application that extracts structured data from invoices in PDF or image formats. It supports OCR-based extraction using both standard Tesseract OCR and Groq's powerful vision-language model (LLaMA). Outputs are presented in JSON format and downloadable as CSV or Excel.

---

## 🔍 Features

- ✅ Upload invoice files (PDF, PNG, JPG, WEBP)
- ✅ Choose between **Normal OCR (Tesseract)** or **Groq OCR (LLaMA VLM)**
- ✅ Handles both structured and unstructured invoices
- ✅ Auto-detects PDF type (readable vs scanned)
- ✅ Displays extracted JSON output
- ✅ Download result as **CSV** or **Excel (.xlsx)**
- ✅ Responsive & clean UI built with Bootstrap

---

## 🎯 Objective

Build an AI system that automatically reads scanned or digital invoices (PDFs/images) from various vendors with different layouts and extracts structured expense information for further processing, analytics, or storage.

---

## 📂 Supported Formats

- Scanned PDF invoice documents

- PNG, JPG, JPEG, WEBP receipt with tabular billing

- WEBP format digital invoice

- Multi-vendor unstructured PDFs

---

## 🚀 How It Works

Below is the workflow of how the system processes input files:
<img width="3840" height="3493" alt="ai-invoice-workflow" src="https://github.com/user-attachments/assets/2b4ac385-4d6b-45fc-b693-9044f44c9fbc" />


---

## ⚙️ Setup & Installation

### 🛠️ Prerequisites

- Python 3.8+
- [Poppler](https://github.com/oschwartz10612/poppler-windows) (for PDF to image conversion)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) (ensure it's in your system path)

### 📦 Installation

```bash
git clone https://github.com/your-username/invosight.git
cd invosight
pip install -r requirements.txt

```

### Make sure to update .env with your Groq API key:

GROQ_API_KEY = "your_groq_key_here"

### On Windows, ensure your system PATH or script points to: 

poppler_path = "path/to/poppler/bin"
pytesseract.pytesseract.tesseract_cmd = "path/to/tesseract.exe"

### Run the App

python app.py

http://127.0.0.1:5000/

### Screenshots 

<img width="1630" height="1462" alt="new-invoice1" src="https://github.com/user-attachments/assets/1377149d-21c9-4014-b7c9-9a5cabbbca94" />

<img width="1616" height="1442" alt="new-invoice2" src="https://github.com/user-attachments/assets/7c08a913-a8ff-4fb3-a360-e3286b112ecd" />


### Acknowledgements

- [Groq](https://groq.com/) 
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler PDF](https://poppler.freedesktop.org/)
- [Flask](https://flask.palletsprojects.com/)

### Contributions 

⭐️ Star this repo if you like it, and feel free to fork or contribute!

### License

This project is licensed under the MIT License.

MIT License , Copyright (c) 2025
