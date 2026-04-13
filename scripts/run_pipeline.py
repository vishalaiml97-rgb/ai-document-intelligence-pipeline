import os
import sys
import logging
from datetime import datetime

# Add scripts folder to path
sys.path.insert(0, os.path.dirname(__file__))

from detect_files import scan_input_folder
from extract_pdf_text import process_text_pdf
from ocr_extract import process_ocr_file
from clean_text import clean_text
from extract_fields import extract_fields_from_file
from to_json import process_to_json
from deduplicate import load_seen_hashes, save_seen_hashes, is_duplicate, check_duplicate_fields
from database import create_tables, save_to_database
from vector_store import store_document


# ── Setup Logging ─────────────────────────────────────────────────────────────

def setup_logging(logs_folder: str) -> logging.Logger:
    os.makedirs(logs_folder, exist_ok=True)
    log_file = os.path.join(logs_folder, "pipeline.log")

    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(base_dir: str):
    input_folder       = os.path.join(base_dir, "input_docs")
    raw_text_folder    = os.path.join(base_dir, "raw_text")
    clean_text_folder  = os.path.join(base_dir, "clean_text")
    json_output_folder = os.path.join(base_dir, "json_output")
    logs_folder        = os.path.join(base_dir, "logs")

    logger = setup_logging(logs_folder)
    logger.info("=" * 60)
    logger.info("PIPELINE STARTED")
    logger.info("=" * 60)

    # Initialize database tables
    create_tables()

    # Load deduplication hashes
    seen_hashes = load_seen_hashes()
    seen_records = []

    # Stats
    stats = {"total": 0, "success": 0, "failed": 0, "duplicate": 0, "skipped": 0}

    # Step 1: Scan input folder
    logger.info(f"Scanning input folder: {input_folder}")
    files = scan_input_folder(input_folder)
    stats["total"] = len(files)
    logger.info(f"Found {len(files)} files")

    for file_info in files:
        file_path  = file_info["file_path"]
        file_name  = file_info["file_name"]
        file_type  = file_info["file_type"]

        logger.info(f"--- Processing: {file_name} [{file_type}] ---")

        # Step 2: Skip unsupported files
        if file_type == "unsupported":
            logger.warning(f"SKIPPED (unsupported type): {file_name}")
            stats["skipped"] += 1
            continue

        # Step 3: Deduplication check
        if is_duplicate(file_path, seen_hashes):
            logger.warning(f"SKIPPED (duplicate file): {file_name}")
            stats["duplicate"] += 1
            continue

        # Step 4: Extract text
        try:
            if file_type == "text_pdf":
                result = process_text_pdf(file_path, raw_text_folder)
            else:
                result = process_ocr_file(file_path, file_type, raw_text_folder)

            if result["status"] != "success":
                logger.error(f"FAILED (text extraction): {file_name}")
                stats["failed"] += 1
                continue

            raw_text = result["text"]
        except Exception as e:
            logger.error(f"FAILED (text extraction error): {file_name} - {e}")
            stats["failed"] += 1
            continue

        # Step 5: Clean text
        try:
            from pathlib import Path
            cleaned = clean_text(raw_text)
            clean_path = os.path.join(clean_text_folder, Path(file_name).stem + ".txt")
            os.makedirs(clean_text_folder, exist_ok=True)
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            logger.info(f"Text cleaned: {clean_path}")
        except Exception as e:
            logger.error(f"FAILED (text cleaning): {file_name} - {e}")
            stats["failed"] += 1
            continue

        # Step 6: Extract fields
        try:
            fields = extract_fields_from_file(clean_path)
            logger.info(f"Fields extracted: {list(fields.keys())}")
        except Exception as e:
            logger.error(f"FAILED (field extraction): {file_name} - {e}")
            stats["failed"] += 1
            continue

        # Step 7: Field-level deduplication
        if check_duplicate_fields(fields, seen_records):
            logger.warning(f"SKIPPED (duplicate fields): {file_name}")
            stats["duplicate"] += 1
            continue

        # Step 8: Validate and save JSON
        json_result = process_to_json(fields, json_output_folder)

        if json_result["status"] == "success":
            logger.info(f"SUCCESS: {file_name} → {json_result['output_path']}")
            seen_records.append(fields)
            stats["success"] += 1

            # Step 9: Save to PostgreSQL
            save_to_database(fields)
            logger.info(f"DB saved: {file_name}")

            # Step 10: Store in ChromaDB vector store
            store_document(Path(file_name).stem + ".txt", cleaned, fields)
            logger.info(f"Vector stored: {file_name}")
        else:
            logger.error(f"FAILED (validation): {file_name} - {json_result.get('error')}")
            stats["failed"] += 1

    # Save updated hashes
    save_seen_hashes(seen_hashes)

    # Final summary
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Total files   : {stats['total']}")
    logger.info(f"  Successful    : {stats['success']}")
    logger.info(f"  Failed        : {stats['failed']}")
    logger.info(f"  Duplicates    : {stats['duplicate']}")
    logger.info(f"  Skipped       : {stats['skipped']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_pipeline(base_dir)
