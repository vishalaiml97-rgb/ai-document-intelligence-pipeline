import os
import sys
import json
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(__file__))

from detect_files import detect_file_type
from extract_pdf_text import process_text_pdf
from ocr_extract import process_ocr_file
from clean_text import clean_text
from extract_fields import extract_fields_from_file
from to_json import process_to_json
from deduplicate import load_seen_hashes, save_seen_hashes, is_duplicate
from database import create_tables, save_to_database, fetch_all_receipts, fetch_all_invoices
from vector_store import store_document, search_similar

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="AI Document Intelligence Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_DIR = os.path.join(BASE_DIR, "input_docs")
RAW_DIR = os.path.join(BASE_DIR, "raw_text")
CLEAN_DIR = os.path.join(BASE_DIR, "clean_text")
JSON_DIR = os.path.join(BASE_DIR, "json_output")

# Mount static files (frontend)
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize DB tables on startup
@app.on_event("startup")
def startup():
    create_tables()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(STATIC_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or image), run the full pipeline,
    and return extracted fields as JSON.
    """
    # Save uploaded file to input_docs/
    file_name = file.filename
    file_path = os.path.join(INPUT_DIR, file_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Detect file type
    file_type = detect_file_type(file_path)
    if file_type == "unsupported":
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {Path(file_name).suffix}")

    # Deduplication check
    seen_hashes = load_seen_hashes()
    if is_duplicate(file_path, seen_hashes):
        save_seen_hashes(seen_hashes)
        return JSONResponse(content={
            "status": "duplicate",
            "message": f"{file_name} has already been processed.",
            "file_name": file_name,
            "file_type": file_type
        })
    save_seen_hashes(seen_hashes)

    # Extract text
    if file_type == "text_pdf":
        result = process_text_pdf(file_path, RAW_DIR)
    else:
        result = process_ocr_file(file_path, file_type, RAW_DIR)

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail="Text extraction failed.")

    # Clean text
    cleaned = clean_text(result["text"])
    clean_path = os.path.join(CLEAN_DIR, Path(file_name).stem + ".txt")
    os.makedirs(CLEAN_DIR, exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    # Extract fields
    fields = extract_fields_from_file(clean_path)

    # Validate and save JSON
    json_result = process_to_json(fields, JSON_DIR)
    if json_result["status"] != "success":
        raise HTTPException(status_code=422, detail=f"Validation failed: {json_result.get('error')}")

    # Save to PostgreSQL
    save_to_database(fields)

    # Save to ChromaDB
    store_document(Path(file_name).stem + ".txt", cleaned, fields)

    # Load and return saved JSON
    json_path = json_result["output_path"]
    with open(json_path, "r", encoding="utf-8") as f:
        output = json.load(f)

    return JSONResponse(content={
        "status": "success",
        "file_name": file_name,
        "file_type": file_type,
        "extracted_data": output
    })


@app.get("/search")
def semantic_search(query: str, n: int = 3):
    """
    Semantic search across all processed documents using ChromaDB.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    results = search_similar(query, n_results=n)

    if not results or not results["documents"]:
        return JSONResponse(content={"query": query, "results": []})

    output = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        output.append({
            "rank": i + 1,
            "file_name": meta.get("file_name", ""),
            "vendor_name": meta.get("vendor_name", ""),
            "amount": meta.get("amount_paid") or meta.get("total_amount", ""),
            "date": meta.get("date_paid") or meta.get("invoice_date", ""),
            "document_type": meta.get("document_type", ""),
            "preview": doc[:300]
        })

    return JSONResponse(content={"query": query, "results": output})


@app.get("/records")
def get_all_records():
    """
    Fetch all receipts and invoices from PostgreSQL.
    """
    receipts = [dict(r) for r in fetch_all_receipts()]
    invoices = [dict(r) for r in fetch_all_invoices()]

    # Convert datetime to string for JSON serialization
    for r in receipts:
        if "created_at" in r and r["created_at"]:
            r["created_at"] = str(r["created_at"])
    for i in invoices:
        if "created_at" in i and i["created_at"]:
            i["created_at"] = str(i["created_at"])

    return JSONResponse(content={
        "receipts": receipts,
        "invoices": invoices,
        "total": len(receipts) + len(invoices)
    })


@app.post("/process-multiple")
async def process_multiple(files: list[UploadFile] = File(...)):
    """
    Upload multiple documents at once and process each one.
    Returns a list of results.
    """
    results = []
    seen_hashes = load_seen_hashes()

    for file in files:
        file_name = file.filename
        file_path = os.path.join(INPUT_DIR, file_name)

        # Save file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Detect type
        file_type = detect_file_type(file_path)
        if file_type == "unsupported":
            results.append({"file_name": file_name, "status": "failed", "error": "Unsupported file type"})
            continue

        # Deduplication
        if is_duplicate(file_path, seen_hashes):
            results.append({"file_name": file_name, "status": "duplicate", "file_type": file_type})
            continue

        try:
            # Extract text
            if file_type == "text_pdf":
                result = process_text_pdf(file_path, RAW_DIR)
            else:
                result = process_ocr_file(file_path, file_type, RAW_DIR)

            if result["status"] != "success":
                results.append({"file_name": file_name, "status": "failed", "error": "Text extraction failed"})
                continue

            # Clean
            cleaned = clean_text(result["text"])
            clean_path = os.path.join(CLEAN_DIR, Path(file_name).stem + ".txt")
            os.makedirs(CLEAN_DIR, exist_ok=True)
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            # Extract fields
            fields = extract_fields_from_file(clean_path)

            # Validate + JSON
            json_result = process_to_json(fields, JSON_DIR)
            if json_result["status"] != "success":
                results.append({"file_name": file_name, "status": "failed", "error": "Validation failed"})
                continue

            # Save to DB + Vector
            save_to_database(fields)
            store_document(Path(file_name).stem + ".txt", cleaned, fields)

            # Load JSON output
            with open(json_result["output_path"], "r", encoding="utf-8") as f:
                output = json.load(f)

            results.append({
                "file_name": file_name,
                "status": "success",
                "file_type": file_type,
                "extracted_data": output
            })

        except Exception as e:
            results.append({"file_name": file_name, "status": "failed", "error": str(e)})

    save_seen_hashes(seen_hashes)

    summary = {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "duplicate": sum(1 for r in results if r["status"] == "duplicate"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
    }

    return JSONResponse(content={"summary": summary, "results": results})


@app.post("/run-pipeline")
def run_full_pipeline():
    """
    Run the full pipeline on all files currently in input_docs/.
    """
    from detect_files import scan_input_folder
    from deduplicate import check_duplicate_fields

    seen_hashes = load_seen_hashes()
    seen_records = []
    results = []

    files = scan_input_folder(INPUT_DIR)

    for file_info in files:
        file_path = file_info["file_path"]
        file_name = file_info["file_name"]
        file_type = file_info["file_type"]

        if file_type == "unsupported":
            results.append({"file_name": file_name, "status": "skipped", "reason": "unsupported type"})
            continue

        if is_duplicate(file_path, seen_hashes):
            results.append({"file_name": file_name, "status": "duplicate"})
            continue

        try:
            if file_type == "text_pdf":
                result = process_text_pdf(file_path, RAW_DIR)
            else:
                result = process_ocr_file(file_path, file_type, RAW_DIR)

            if result["status"] != "success":
                results.append({"file_name": file_name, "status": "failed", "reason": "extraction failed"})
                continue

            cleaned = clean_text(result["text"])
            clean_path = os.path.join(CLEAN_DIR, Path(file_name).stem + ".txt")
            os.makedirs(CLEAN_DIR, exist_ok=True)
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            fields = extract_fields_from_file(clean_path)

            if check_duplicate_fields(fields, seen_records):
                results.append({"file_name": file_name, "status": "duplicate", "reason": "duplicate fields"})
                continue

            json_result = process_to_json(fields, JSON_DIR)
            if json_result["status"] != "success":
                results.append({"file_name": file_name, "status": "failed", "reason": "validation failed"})
                continue

            save_to_database(fields)
            store_document(Path(file_name).stem + ".txt", cleaned, fields)
            seen_records.append(fields)

            with open(json_result["output_path"], "r", encoding="utf-8") as f:
                output = json.load(f)

            results.append({
                "file_name": file_name,
                "status": "success",
                "file_type": file_type,
                "extracted_data": output
            })

        except Exception as e:
            results.append({"file_name": file_name, "status": "failed", "reason": str(e)})

    save_seen_hashes(seen_hashes)

    summary = {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "duplicate": sum(1 for r in results if r["status"] == "duplicate"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
    }

    return JSONResponse(content={"summary": summary, "results": results})


@app.get("/health")
def health():
    return {"status": "running", "message": "AI Document Intelligence Pipeline is live."}
