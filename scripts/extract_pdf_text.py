import os
from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a text-based PDF file.
    Returns the full extracted text as a string.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i + 1} ---\n"
                text += page_text
        return text.strip()
    except Exception as e:
        print(f"  ERROR reading PDF {file_path}: {e}")
        return ""


def save_raw_text(file_name: str, text: str, raw_text_folder: str) -> str:
    """
    Save extracted text to the raw_text folder.
    Returns the path of the saved file.
    """
    os.makedirs(raw_text_folder, exist_ok=True)
    output_file = os.path.join(raw_text_folder, Path(file_name).stem + ".txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    return output_file


def process_text_pdf(file_path: str, raw_text_folder: str) -> dict:
    """
    Full process: extract text from PDF and save to raw_text folder.
    Returns a result dict with status and output path.
    """
    file_name = os.path.basename(file_path)
    print(f"  Extracting text from: {file_name}")

    text = extract_text_from_pdf(file_path)

    if not text:
        print(f"  WARNING: No text extracted from {file_name}")
        return {"file_name": file_name, "status": "failed", "output_path": None, "text": ""}

    output_path = save_raw_text(file_name, text, raw_text_folder)
    print(f"  Saved raw text to: {output_path}")

    return {"file_name": file_name, "status": "success", "output_path": output_path, "text": text}


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_folder = os.path.join(base_dir, "input_docs")
    raw_text_folder = os.path.join(base_dir, "raw_text")

    print(f"\nProcessing text PDFs from: {input_folder}\n")

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".pdf"):
            file_path = os.path.join(input_folder, file_name)
            result = process_text_pdf(file_path, raw_text_folder)

            if result["status"] == "success":
                print(f"\n  Preview (first 300 chars):")
                print(f"  {result['text'][:300]}")
            print()
