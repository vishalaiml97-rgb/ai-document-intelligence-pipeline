import os
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# Point to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file (JPG, PNG, etc.) using OCR.
    """
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"  ERROR during OCR on image {file_path}: {e}")
        return ""


def extract_text_from_scanned_pdf(file_path: str) -> str:
    """
    Extract text from a scanned PDF by converting pages to images first,
    then running OCR on each page image.
    """
    try:
        pages = convert_from_path(file_path, dpi=300)
        full_text = ""
        for i, page_image in enumerate(pages):
            print(f"    Running OCR on page {i + 1}...")
            page_text = pytesseract.image_to_string(page_image)
            full_text += f"\n--- Page {i + 1} ---\n"
            full_text += page_text
        return full_text.strip()
    except Exception as e:
        print(f"  ERROR during OCR on scanned PDF {file_path}: {e}")
        return ""


def save_raw_text(file_name: str, text: str, raw_text_folder: str) -> str:
    """
    Save extracted OCR text to the raw_text folder.
    """
    os.makedirs(raw_text_folder, exist_ok=True)
    output_file = os.path.join(raw_text_folder, Path(file_name).stem + ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    return output_file


def process_ocr_file(file_path: str, file_type: str, raw_text_folder: str) -> dict:
    """
    Process an image or scanned PDF file using OCR.
    file_type: 'image' or 'scanned_pdf'
    """
    file_name = os.path.basename(file_path)
    print(f"  Running OCR on: {file_name}")

    if file_type == "image":
        text = extract_text_from_image(file_path)
    elif file_type == "scanned_pdf":
        text = extract_text_from_scanned_pdf(file_path)
    else:
        return {"file_name": file_name, "status": "failed", "output_path": None, "text": ""}

    if not text:
        print(f"  WARNING: No text extracted from {file_name}")
        return {"file_name": file_name, "status": "failed", "output_path": None, "text": ""}

    output_path = save_raw_text(file_name, text, raw_text_folder)
    print(f"  Saved to: {output_path}")

    return {"file_name": file_name, "status": "success", "output_path": output_path, "text": text}


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_folder = os.path.join(base_dir, "input_docs")
    raw_text_folder = os.path.join(base_dir, "raw_text")

    image_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]

    print(f"\nProcessing images and scanned PDFs from: {input_folder}\n")

    for file_name in os.listdir(input_folder):
        ext = Path(file_name).suffix.lower()
        file_path = os.path.join(input_folder, file_name)

        if ext in image_extensions:
            result = process_ocr_file(file_path, "image", raw_text_folder)
        else:
            continue

        if result["status"] == "success":
            print(f"\n  Preview (first 300 chars):")
            print(f"  {result['text'][:300]}")
        print()
