import os
from pathlib import Path

# Supported file types
PDF_EXTENSION = ".pdf"
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]


def is_text_pdf(file_path: str) -> bool:
    """Check if a PDF has extractable text (not scanned)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                return True
        return False
    except Exception:
        return False


def detect_file_type(file_path: str) -> str:
    """
    Detect the type of a document file.

    Returns:
        'text_pdf'   - PDF with extractable text
        'scanned_pdf' - PDF that is scanned (needs OCR)
        'image'       - JPG, PNG or other image file
        'unsupported' - File type not supported
    """
    ext = Path(file_path).suffix.lower()

    if ext == PDF_EXTENSION:
        if is_text_pdf(file_path):
            return "text_pdf"
        else:
            return "scanned_pdf"
    elif ext in IMAGE_EXTENSIONS:
        return "image"
    else:
        return "unsupported"


def scan_input_folder(input_folder: str) -> list:
    """
    Scan the input folder and return a list of files with their detected types.

    Returns:
        List of dicts: [{"file_path": "...", "file_name": "...", "file_type": "..."}]
    """
    results = []

    if not os.path.exists(input_folder):
        print(f"Input folder not found: {input_folder}")
        return results

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        if not os.path.isfile(file_path):
            continue

        file_type = detect_file_type(file_path)

        results.append({
            "file_path": file_path,
            "file_name": file_name,
            "file_type": file_type
        })

        print(f"  {file_name} --> {file_type}")

    return results


if __name__ == "__main__":
    input_folder = os.path.join(os.path.dirname(__file__), "..", "input_docs")
    input_folder = os.path.abspath(input_folder)

    print(f"\nScanning folder: {input_folder}\n")
    files = scan_input_folder(input_folder)

    print(f"\nTotal files found: {len(files)}")
    for f in files:
        print(f"  [{f['file_type']}] {f['file_name']}")
