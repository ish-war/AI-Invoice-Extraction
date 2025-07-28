import re
from transformers import pipeline

# Load HuggingFace NER pipeline
ner_pipeline = pipeline("ner", grouped_entities=True, model="dslim/bert-base-NER")


def extract_entities(text):
    # Apply NER
    ner_results = ner_pipeline(text)

    # 1. Extract all Vendor Names (ORG entities)
    vendor_names = list(set([ent['word'] for ent in ner_results if ent['entity_group'] == 'ORG']))

    # 2. Extract all Invoice Numbers
    invoice_numbers = []
    invoice_patterns = [
        r"(?:Invoice|Inv|Bill)\s*(?:No\.?|Number)?\s*[:#\-]?\s*([A-Z0-9\-\/]+)",
        r"(?:Invoice|Inv|Bill)[^\w\d]?\s*#?\s*([A-Z0-9\-\/]+)"
    ]
    for pattern in invoice_patterns:
        invoice_numbers += re.findall(pattern, text, flags=re.IGNORECASE)
    invoice_numbers = list(set(invoice_numbers))  # Remove duplicates

    # 3. Extract all Invoice Dates
    date_pattern = r"(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})"
    invoice_dates = list(set(re.findall(date_pattern, text)))

    # 4. Extract all Total & Tax Amounts
    total_amounts = []
    tax_amounts = []

    amount_pattern = r"(Total Amount|Total|Amount Due)\s*[:\-]?\s*\₹?\$?\s*([0-9,]+\.\d{2})"
    tax_pattern = r"(GST|VAT|Tax)\s*[:\-]?\s*\₹?\$?\s*([0-9,]+\.\d{2})"

    total_matches = re.findall(amount_pattern, text, re.IGNORECASE)
    tax_matches = re.findall(tax_pattern, text, re.IGNORECASE)

    for _, amt in total_matches:
        try:
            total_amounts.append(float(amt.replace(",", "")))
        except:
            continue

    for _, amt in tax_matches:
        try:
            tax_amounts.append(float(amt.replace(",", "")))
        except:
            continue

    # 5. Extract Line Items (basic pattern)
    line_items = []
    for line in text.split('\n'):
        if re.search(r'[a-zA-Z]{3,}', line) and re.search(r'\d+\.\d{2}', line):
            try:
                parts = line.rsplit(' ', 1)
                description = parts[0].strip()
                amount = float(parts[1].replace(",", "").strip())
                line_items.append({"description": description, "amount": amount})
            except:
                continue

    return {
        "vendor_names": vendor_names,
        "invoice_numbers": invoice_numbers,
        "invoice_dates": invoice_dates,
        "total_amounts": total_amounts,
        "tax_amounts": tax_amounts,
        "line_items": line_items
    }


