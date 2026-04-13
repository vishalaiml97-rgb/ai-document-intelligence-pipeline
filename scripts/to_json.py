import os
import json
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class ReceiptSchema(BaseModel):
    file_name: str
    document_type: str
    vendor_name: Optional[str] = None
    receipt_number: Optional[str] = None
    date_paid: Optional[str] = None
    amount_paid: Optional[float] = None
    item_description: Optional[str] = None

    @field_validator("amount_paid")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("amount_paid must be a positive number")
        return v

    @field_validator("receipt_number")
    @classmethod
    def receipt_number_format(cls, v):
        if v is not None and not v.replace("-", "").isdigit():
            raise ValueError("receipt_number must be in XXXX-XXXX format")
        return v


class InvoiceSchema(BaseModel):
    file_name: str
    document_type: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    total_amount: Optional[float] = None

    @field_validator("total_amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("total_amount must be a positive number")
        return v


# ── Validate & Save ───────────────────────────────────────────────────────────

def validate_fields(fields: dict) -> tuple:
    """
    Validate extracted fields using Pydantic schema.
    Returns (validated_dict, error_message)
    """
    try:
        if fields.get("document_type") == "receipt":
            validated = ReceiptSchema(**fields)
        else:
            validated = InvoiceSchema(**fields)
        return validated.model_dump(), None
    except ValidationError as e:
        return None, str(e)


def save_to_json(validated_data: dict, json_output_folder: str) -> str:
    """
    Save validated data dict to a JSON file.
    Returns the output file path.
    """
    os.makedirs(json_output_folder, exist_ok=True)

    # Use file_name stem as output filename
    base_name = os.path.splitext(validated_data["file_name"])[0]
    output_path = os.path.join(json_output_folder, base_name + ".json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validated_data, f, indent=4)

    return output_path


def process_to_json(fields: dict, json_output_folder: str) -> dict:
    """
    Validate fields and save to JSON.
    Returns result dict with status and output path.
    """
    file_name = fields.get("file_name", "unknown")

    validated_data, error = validate_fields(fields)

    if error:
        print(f"  VALIDATION FAILED: {file_name}")
        print(f"  Error: {error}")
        return {"file_name": file_name, "status": "failed", "error": error, "output_path": None}

    output_path = save_to_json(validated_data, json_output_folder)
    print(f"  SAVED: {output_path}")

    return {"file_name": file_name, "status": "success", "output_path": output_path}


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from extract_fields import extract_fields_from_file

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    clean_text_folder = os.path.join(base_dir, "clean_text")
    json_output_folder = os.path.join(base_dir, "json_output")

    print(f"\nConverting extracted fields to JSON...\n")

    for file_name in os.listdir(clean_text_folder):
        if not file_name.endswith(".txt"):
            continue

        file_path = os.path.join(clean_text_folder, file_name)
        fields = extract_fields_from_file(file_path)

        print(f"--- {file_name} ---")
        result = process_to_json(fields, json_output_folder)
        print(f"  Status: {result['status']}")
        print()

    # Show saved JSON files
    print("\nJSON files saved:")
    for f in os.listdir(json_output_folder):
        print(f"  {f}")
