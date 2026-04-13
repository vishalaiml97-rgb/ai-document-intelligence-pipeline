import os
import re
from pathlib import Path


def extract_receipt_fields(text: str) -> dict:
    """
    Extract fields from AURBORBLOOM LLC receipt text.
    Fields: vendor_name, receipt_number, date_paid, amount_paid, item_description
    """
    fields = {
        "vendor_name": None,
        "receipt_number": None,
        "date_paid": None,
        "amount_paid": None,
        "item_description": None,
        "document_type": "receipt"
    }

    # Vendor name - look for "Receipt from X" or "from X LLC"
    vendor_match = re.search(r"Receipt from ([A-Z][A-Z\s]+LLC)", text)
    if vendor_match:
        fields["vendor_name"] = vendor_match.group(1).strip()

    # Receipt number - look for #XXXX-XXXX pattern (with or without "Receipt" prefix)
    receipt_match = re.search(r"(?:Receipt\s*)?#([\d]{4}-[\d]{4})", text)
    if receipt_match:
        fields["receipt_number"] = receipt_match.group(1).strip()

    # Date paid - look for Month DD, YYYY pattern
    date_match = re.search(r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
                           r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
                           r"Dec(?:ember)?)\s+\d{1,2},\s+\d{4}", text)
    if date_match:
        fields["date_paid"] = date_match.group(0).strip()

    # Amount paid - look for $XXX.XX pattern
    amount_match = re.search(r"Amount paid\s+\$?([\d,]+\.\d{2})", text)
    if amount_match:
        fields["amount_paid"] = float(amount_match.group(1).replace(",", ""))
    else:
        # fallback - first dollar amount
        fallback = re.search(r"\$([\d,]+\.\d{2})", text)
        if fallback:
            fields["amount_paid"] = float(fallback.group(1).replace(",", ""))

    # Item description - look for "X x 1 $" pattern (product line)
    item_match = re.search(r"([A-Za-z][A-Za-z \.#&]+)\s+x\s+1\s+\$", text)
    if item_match:
        fields["item_description"] = item_match.group(1).strip().splitlines()[-1].strip()

    return fields


def extract_invoice_fields(text: str) -> dict:
    """
    Extract fields from a standard invoice PDF.
    Fields: vendor_name, invoice_number, invoice_date, due_date, total_amount
    """
    fields = {
        "vendor_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": None,
        "document_type": "invoice"
    }

    # Invoice number - INV-XXXX pattern
    inv_match = re.search(r"Invoice\s*Number\s+([A-Z]{2,5}-\d+)", text)
    if inv_match:
        fields["invoice_number"] = inv_match.group(1).strip()

    # Invoice date
    inv_date = re.search(r"Invoice\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})", text)
    if inv_date:
        fields["invoice_date"] = inv_date.group(1).strip()

    # Due date
    due_date = re.search(r"Due\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})", text)
    if due_date:
        fields["due_date"] = due_date.group(1).strip()

    # Vendor name - look for "From:" section, first line only
    vendor_match = re.search(r"From:\s*\n([^\n]+)", text)
    if vendor_match:
        fields["vendor_name"] = vendor_match.group(1).strip()

    # Total amount - look for "Total" followed by a dollar amount
    total_match = re.search(r"Total\s+\$?([\d,]+\.\d{2})", text)
    if total_match:
        fields["total_amount"] = float(total_match.group(1).replace(",", ""))

    return fields


def extract_fields_from_file(file_path: str) -> dict:
    """
    Read a clean text file and extract fields based on document type.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    file_name = os.path.basename(file_path)

    # Decide document type based on content
    if "Receipt" in text and "AMOUNT PAID" in text:
        fields = extract_receipt_fields(text)
    else:
        fields = extract_invoice_fields(text)

    fields["file_name"] = file_name
    return fields


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    clean_text_folder = os.path.join(base_dir, "clean_text")

    print(f"\nExtracting fields from: {clean_text_folder}\n")

    for file_name in os.listdir(clean_text_folder):
        if not file_name.endswith(".txt"):
            continue

        file_path = os.path.join(clean_text_folder, file_name)
        fields = extract_fields_from_file(file_path)

        print(f"--- {file_name} ---")
        for key, value in fields.items():
            print(f"  {key}: {value}")
        print()
