import os
import re
from pathlib import Path


def clean_text(text: str) -> str:
    """
    Clean and normalize raw extracted text.
    - Remove extra whitespace
    - Remove repeated blank lines
    - Remove junk symbols
    - Fix spacing issues
    """
    # Replace tabs with a space
    text = text.replace("\t", " ")

    # Remove non-printable/junk characters but keep common punctuation
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)

    # Remove multiple spaces → single space
    text = re.sub(r" {2,}", " ", text)

    # Remove lines that are just symbols or whitespace (junk lines)
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip empty or junk-only lines (lines with only symbols, no alphanumeric)
        if stripped and re.search(r"[a-zA-Z0-9]", stripped):
            cleaned_lines.append(stripped)
        elif not stripped:
            # Keep one blank line for readability
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")

    # Remove leading/trailing blank lines
    while cleaned_lines and cleaned_lines[0] == "":
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def process_clean_text(raw_text_folder: str, clean_text_folder: str) -> list:
    """
    Read all .txt files from raw_text folder, clean them,
    and save to clean_text folder.
    """
    os.makedirs(clean_text_folder, exist_ok=True)
    results = []

    txt_files = [f for f in os.listdir(raw_text_folder) if f.endswith(".txt")]

    if not txt_files:
        print("  No text files found in raw_text folder.")
        return results

    for file_name in txt_files:
        input_path = os.path.join(raw_text_folder, file_name)
        output_path = os.path.join(clean_text_folder, file_name)

        print(f"  Cleaning: {file_name}")

        with open(input_path, "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = clean_text(raw)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"  Saved to: {output_path}")
        results.append({"file_name": file_name, "output_path": output_path, "text": cleaned})

    return results


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_text_folder = os.path.join(base_dir, "raw_text")
    clean_text_folder = os.path.join(base_dir, "clean_text")

    print(f"\nCleaning text files from: {raw_text_folder}\n")

    results = process_clean_text(raw_text_folder, clean_text_folder)

    print(f"\nTotal files cleaned: {len(results)}")

    # Show preview of each cleaned file
    for r in results:
        print(f"\n--- Preview: {r['file_name']} ---")
        print(r["text"][:400])
