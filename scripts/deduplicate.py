import os
import hashlib
import json


SEEN_HASHES_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "seen_hashes.json")


def load_seen_hashes() -> dict:
    """Load previously seen file hashes from disk."""
    os.makedirs(os.path.dirname(SEEN_HASHES_FILE), exist_ok=True)
    if os.path.exists(SEEN_HASHES_FILE):
        with open(SEEN_HASHES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_seen_hashes(seen: dict):
    """Save updated hashes to disk."""
    with open(SEEN_HASHES_FILE, "w") as f:
        json.dump(seen, f, indent=4)


def hash_file(file_path: str) -> str:
    """Generate MD5 hash of file contents."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def is_duplicate(file_path: str, seen_hashes: dict) -> bool:
    """Check if a file has been processed before based on its hash."""
    file_hash = hash_file(file_path)
    file_name = os.path.basename(file_path)

    if file_hash in seen_hashes:
        print(f"  DUPLICATE: {file_name} matches {seen_hashes[file_hash]}")
        return True

    # Not a duplicate — register it
    seen_hashes[file_hash] = file_name
    return False


def check_duplicate_fields(fields: dict, seen_records: list) -> bool:
    """
    Secondary check: compare key fields to catch renamed duplicate files.
    For receipts: receipt_number + amount_paid
    For invoices: invoice_number + total_amount
    """
    doc_type = fields.get("document_type")

    for record in seen_records:
        if doc_type == "receipt":
            if (record.get("receipt_number") == fields.get("receipt_number") and
                    record.get("receipt_number") is not None and
                    record.get("amount_paid") == fields.get("amount_paid")):
                print(f"  DUPLICATE FIELDS: receipt_number={fields.get('receipt_number')} already processed")
                return True
        elif doc_type == "invoice":
            if (record.get("invoice_number") == fields.get("invoice_number") and
                    record.get("invoice_number") is not None and
                    record.get("total_amount") == fields.get("total_amount")):
                print(f"  DUPLICATE FIELDS: invoice_number={fields.get('invoice_number')} already processed")
                return True

    return False


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_folder = os.path.join(base_dir, "input_docs")

    print("\nChecking for duplicate files...\n")

    seen_hashes = load_seen_hashes()
    initial_count = len(seen_hashes)

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if not os.path.isfile(file_path):
            continue

        dup = is_duplicate(file_path, seen_hashes)
        if not dup:
            print(f"  NEW: {file_name}")

    save_seen_hashes(seen_hashes)
    new_count = len(seen_hashes) - initial_count
    print(f"\nNew files registered: {new_count}")
    print(f"Total seen: {len(seen_hashes)}")
