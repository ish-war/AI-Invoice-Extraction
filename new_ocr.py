import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import re

# Optional: If on Windows, set Tesseract path like this
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_file_type(file_ext, file_bytes):
    """
    Detects if the uploaded file is a readable PDF (with embedded text),
    a scanned/unreadable PDF, or an image.
    """
    if file_ext == ".pdf":
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                return "readable_pdf"
            else:
                return "scanned_pdf"
        except Exception:
            return "scanned_pdf"
    elif file_ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
        return "image"
    else:
        return "unsupported"


def extract_text_from_readable_pdf_bytes(file_bytes):
    """
    Extracts text from a readable PDF using PyMuPDF.
    """
    # Optional fallback extraction
    extracted_fields = ""
    full_text = extract_text_sectionwise_from_pdf_bytes(file_bytes)

    return full_text.strip() + "\n\n" + "Extracted Fields:\n" + str(extracted_fields)

import fitz  # PyMuPDF


def extract_text_sectionwise_from_pdf_bytes(file_bytes):
    """
    Extracts section-wise text from readable PDF using PyMuPDF's block-level layout.
    Combines the blocks into free-flowing natural reading order (top-down, left-right).
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""

    for page in doc:
        # Each block is: (x0, y0, x1, y1, text, block_no, block_type, block_flags)
        blocks = page.get_text("blocks")
        # Sort blocks top-to-bottom (y0), then left-to-right (x0)
        blocks = sorted(blocks, key=lambda b: (round(b[1]), round(b[0])))

        for block in blocks:
            block_text = block[4].strip()
            if block_text:  # skip empty blocks
                full_text += block_text + "\n\n"

    doc.close()
    return full_text.strip()



def extract_text_from_unreadable_pdf_bytes(file_bytes):
    """
    Extracts text from a scanned PDF using OCR (via Tesseract).
    """
    images = convert_from_bytes(file_bytes, poppler_path=r"C:/Users/Ishwar/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin")  # ✅ Specify poppler path

    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang='eng', config='--psm 6')
    return text.strip()


def extract_text_from_image_file(pil_image):
    """
    Extracts text from an image using OCR (via Tesseract).
    """
    return pytesseract.image_to_string(pil_image, lang='eng').strip()


def extract_field_from_pdf_text(text):
    """
    Extracts key fields like Invoice Number, Order ID, and Date using regex.
    """
    fields = {}

    # Invoice Number
    match_invoice = re.search(r"Invoice\s*No\.?:\s*([A-Z0-9\-]+)", text)
    if match_invoice:
        fields['invoice_number'] = match_invoice.group(1)

    # Order ID
    match_order = re.search(r"Order\s*Id\s*[:\-]?\s*([A-Z0-9]+)", text, re.IGNORECASE)
    if match_order:
        fields['order_id'] = match_order.group(1)

    # Invoice Date
    match_date = re.search(r"Date\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", text)
    if match_date:
        fields['invoice_date'] = match_date.group(1)

    return fields
