# groq.py

import os
import base64
import requests
import json
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
from pdf2image import convert_from_bytes


system_prompt = (
    "You are an intelligent and highly precise document parser. "
    "Your task is to extract relevant fields from invoice images with absolute accuracy. "
    "Always output a clean, well-structured JSON object without any extra text, explanation, or markdown formatting. "
    "Ensure the JSON follows proper structure, valid syntax, and includes keys like `invoice_number`, `vendor_name`, "
    "`invoice_date`, `total_amount`, `tax_amount`, and `line_items` (an array of objects with `description` and `amount`). "
    "Do not include backticks, markdown formatting, or any natural language description."
)

user_prompt = (
    "Extract the invoice details from this image and return only the JSON with the following fields:\n"
    "- invoice_number (string)\n"
    "- vendor_name (string)\n"
    "- invoice_date (string or ISO format)\n"
    "- total_amount (float)\n"
    "- tax_amount (float)\n"
    "- line_items (list of {description, amount})\n\n"
    "Only respond with the JSON structure."
)

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

def convert_pdf_to_image(file_bytes: bytes) -> Image.Image:
    images = convert_from_bytes(file_bytes, poppler_path=r"C:/Users/Ishwar/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin")  # ✅ Specify poppler path
    if not images:
        raise ValueError("No images found in PDF.")
    return images[0]  # First page only


# convert pdf to images
from pdf2image import convert_from_bytes

def encode_image_to_base64(file_bytes: bytes, file_ext: str) -> str:
    """
    Converts image (JPG/PNG/WEBP) or PDF (first page) to base64 string.
    """
    if file_ext.lower() == ".pdf":
        images = convert_from_bytes(file_bytes, poppler_path=r"C:/Users/Ishwar/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin")
        if not images:
            raise ValueError("PDF could not be converted to image.")
        image = images[0]
    else:
        try:
            image = Image.open(BytesIO(file_bytes))
            #   handle PNGs with transparency (RGBA)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
        except Exception:
            raise ValueError("File is not a valid image.")

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def extract_invoice_info_from_image(file_bytes, file_ext) -> dict:
    if not api_key:
        raise EnvironmentError(" GROQ_API_KEY not found in environment variables.")

    image_base64 = encode_image_to_base64(file_bytes, file_ext)

    prompt = """
    Extract the following fields from this invoice image and return ONLY in proper JSON format:
    - invoice_number
    - vendor_name
    - invoice_date
    - total_amount
    - tax_amount
    - line_items (description and amount for each)
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "temperature": 0.3
        }
    )

    result = response.json()
    result = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    output = parse_backtick_wrapped_json(result) 

    return output



import re

def parse_backtick_wrapped_json(content: str) -> dict:
    """
    Extract and parse a valid JSON object from a string that may contain triple backticks or markdown formatting.

    Args:
        content (str): Raw string containing JSON, possibly wrapped in markdown.

    Returns:
        dict: Parsed JSON object if found, otherwise empty dict.
    """
    try:
        # Extract JSON block from backticks like ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # fallback: try to use the full string as-is
            json_str = content.strip()

        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print(" JSON parsing error:", str(e))
        return {}



# Optional: keep this for testing independently
if __name__ == "__main__":
    try:
        path = input("📤 Enter invoice path (PDF/image): ").strip()
        if not os.path.exists(path):
            print(" File does not exist:", path)
            exit()

        if path.lower().endswith(".pdf"):
            path = convert_pdf_to_image(path)

        print("🖼️ Using image file:", path)

        output = extract_invoice_info_from_image(path)

        print("\n📄 Extracted Invoice JSON:\n", output)


    except Exception as e:
        print(" Error occurred:", str(e))
