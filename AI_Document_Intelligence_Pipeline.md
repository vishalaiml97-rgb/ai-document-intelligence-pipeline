# AI Document Intelligence Pipeline
### A Production-Grade Local ETL System for Unstructured Document Processing

**Prepared by:** Vishal S
**Contact:** vishalaiml97@gmail.com
**Date:** March 2026

---

## TABLE OF CONTENTS

1. Executive Summary
2. Problem Statement
3. Solution Overview
4. System Architecture
5. Technology Stack — Detailed Breakdown
6. Component Deep Dive — Every Script Explained
7. Data Flow — Step by Step
8. Sample Inputs and Outputs
9. Database Design
10. Vector Database and Semantic Search
11. Data Quality Framework
12. Observability and Logging
13. Containerization
14. Future Roadmap
15. About

---

## 1. EXECUTIVE SUMMARY

The AI Document Intelligence Pipeline is a fully automated, production-grade local ETL
(Extract, Transform, Load) system built to solve a real-world data engineering challenge:
transforming unstructured documents — scanned invoices, photo receipts, and PDF files —
into validated, structured, model-ready data that can be stored, queried, and searched.

The pipeline handles the complete data lifecycle:

- **Ingestion:** Accepts any PDF or image file dropped into an input folder
- **Detection:** Automatically identifies the document type and selects the correct processing path
- **Extraction:** Pulls raw text using either direct PDF reading or OCR
- **Transformation:** Cleans, normalizes, and extracts structured fields
- **Validation:** Enforces strict data schemas using Pydantic before any data reaches storage
- **Deduplication:** Prevents duplicate records using MD5 file hashing and field-level comparison
- **Loading:** Saves results to JSON files, PostgreSQL relational database, and ChromaDB vector database
- **Observability:** Logs every event with timestamps for full pipeline auditability

This project directly mirrors the responsibilities of an AI Data/Platform Engineer role —
building ETL workflows for unstructured data, implementing data quality checks,
integrating vector databases for RAG systems, and ensuring pipeline reliability and observability.

---

## 2. PROBLEM STATEMENT

### The Challenge
Organizations dealing with large volumes of invoices, receipts, contracts, and scanned
documents face a persistent challenge: critical business data is locked inside unstructured files.

These documents arrive in multiple formats:
- Text-based PDFs (exported from accounting software)
- Scanned PDFs (physical documents scanned to digital)
- Images (photos taken on mobile devices — WhatsApp receipts, etc.)

Each format requires a different extraction approach. Manual processing is:
- **Slow** — a human reads and types out each document
- **Error-prone** — human transcription introduces mistakes
- **Not scalable** — hundreds of documents per day is unmanageable manually
- **Not auditable** — no record of when data was processed or by whom

### The Solution
An automated pipeline that ingests any document format, extracts structured data,
validates it, deduplicates it, and stores it in queryable databases — with zero human
intervention and full observability.

---

## 3. SOLUTION OVERVIEW

### What the Pipeline Does — Plain English

```
You drop a file into the input_docs/ folder.
The pipeline wakes up, reads it, figures out what type it is,
extracts all the text (using OCR if it's a scanned image),
cleans the text, finds the important fields like vendor name,
date, amount, and document number, checks if the data is valid,
checks if it has seen this file before, saves the result as JSON,
stores it in PostgreSQL so you can query it with SQL,
stores it in ChromaDB so you can search it by meaning,
and writes a log entry recording exactly what happened and when.
The whole process takes under 5 seconds per document.
```

### Pipeline in One Line
> Unstructured document (PDF/Image) → OCR/Text Extraction → Clean → Extract Fields
> → Validate (Pydantic) → Deduplicate (MD5) → JSON + PostgreSQL + ChromaDB + Logs

---

## 4. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
│                                                                   │
│   input_docs/                                                     │
│   ├── invoice_001.pdf          (text-based PDF)                  │
│   ├── receipt_whatsapp.jpeg    (phone photo)                     │
│   └── scanned_invoice.pdf      (scanned document)               │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DETECTION LAYER                              │
│                                                                   │
│   detect_files.py                                                 │
│   → Is this a text PDF? (pypdf can extract text?)               │
│   → Is this a scanned PDF? (no extractable text found)          │
│   → Is this an image? (.jpg / .jpeg / .png / .tiff)             │
└──────┬──────────────────┬──────────────────────────┬────────────┘
       │                  │                            │
       ▼                  ▼                            ▼
  TEXT PDF          SCANNED PDF                    IMAGE
  pypdf             pdf2image                  pytesseract
  (direct)          + pytesseract              (direct OCR)
  extract_pdf_      (convert pages             ocr_extract.py
  text.py           to images, then OCR)
       │                  │                            │
       └──────────────────┴──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RAW TEXT LAYER                                   │
│                                                                   │
│   raw_text/                                                       │
│   ├── invoice_001.txt      (raw extracted text, may be messy)   │
│   ├── receipt_whatsapp.txt (raw OCR output)                     │
│   └── scanned_invoice.txt  (raw OCR output, page by page)       │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 TRANSFORMATION LAYER                             │
│                                                                   │
│   clean_text.py                                                   │
│   → Remove non-printable characters                             │
│   → Collapse multiple spaces                                    │
│   → Remove junk-only lines                                      │
│   → Normalize line breaks                                       │
│                                                                   │
│   extract_fields.py                                              │
│   → Regex patterns find: vendor name, document number,          │
│     date, amount, item description                              │
│   → Separate logic for receipts vs invoices                     │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VALIDATION LAYER                                │
│                                                                   │
│   Pydantic v2 Schema Validation                                  │
│   → ReceiptSchema: vendor, receipt_number, date, amount (float) │
│   → InvoiceSchema: vendor, invoice_number, dates, total (float) │
│   → Field validators: amount must be positive float             │
│   → Invalid records → logged + rejected, never reach DB         │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                DEDUPLICATION LAYER                               │
│                                                                   │
│   deduplicate.py                                                  │
│   → Layer 1: MD5 hash of file binary content                    │
│     (same content = same hash, regardless of filename)          │
│   → Layer 2: Field comparison (receipt_number + amount)         │
│   → Hashes stored in logs/seen_hashes.json                      │
│   → Duplicate? → SKIP + log                                     │
│   → New file? → CONTINUE                                        │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LOAD LAYER                                   │
│                                                                   │
│   to_json.py       → json_output/filename.json                  │
│   database.py      → PostgreSQL: receipts / invoices tables     │
│   vector_store.py  → ChromaDB: semantic embeddings              │
└─────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                OBSERVABILITY LAYER                               │
│                                                                   │
│   logs/pipeline.log                                              │
│   → Timestamped entry for every event                           │
│   → INFO: success, DB saved, vector stored                      │
│   → WARNING: duplicate skipped                                  │
│   → ERROR: extraction failed, validation failed                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. TECHNOLOGY STACK — DETAILED BREAKDOWN

### Python 3.13
**Role:** Core programming language for the entire pipeline
**Why chosen:**
- Richest ecosystem for document processing, OCR, data validation, and database connectivity
- Native support for file I/O, regex, logging, hashing, and JSON
- Widely used in data engineering and AI/ML infrastructure

**Key standard library modules used:**
- `os` and `pathlib` — file system operations, path manipulation
- `re` — regular expression pattern matching for field extraction
- `hashlib` — MD5 hashing for deduplication
- `json` — reading and writing structured JSON files
- `logging` — structured pipeline observability
- `datetime` — timestamp generation for logs

---

### Tesseract OCR v5.5 (System Tool)
**Role:** Core OCR engine — reads text from images
**What it does:**
- Google's open-source Optical Character Recognition engine
- Analyzes pixel data in images and converts it to readable text
- Supports 100+ languages
- Installed at system level: `C:\Program Files\Tesseract-OCR\`
**Why chosen:**
- Industry standard for open-source OCR
- Version 5 uses LSTM neural network for superior accuracy
- Free, no API cost, runs completely locally

---

### pytesseract 0.3.13
**Role:** Python wrapper for Tesseract OCR
**What it does:**
- Provides a Python API to call Tesseract from code
- `pytesseract.image_to_string(image)` — one line to extract text from any image
- Handles subprocess calls to Tesseract executable internally
**Dependency:** Requires Tesseract installed at system level

---

### pypdf 6.9.2
**Role:** Text extraction from text-based PDF files
**What it does:**
- Opens PDF files and reads embedded text layer directly
- Iterates through pages: `reader.pages[i].extract_text()`
- Returns plain text string per page
**Why not always use OCR:**
- Text PDFs have embedded text — extracting it directly is 10x faster and more accurate than OCR
- OCR is only needed when there is no embedded text (scanned documents)

---

### pdf2image 1.17.0
**Role:** Convert PDF pages to images for OCR processing
**What it does:**
- Uses Poppler's `pdftoppm` tool to render each PDF page as a PIL Image object
- `convert_from_path(file_path, dpi=300)` — returns list of page images
- DPI setting controls image quality and OCR accuracy
**Why needed:**
- Tesseract reads images, not PDFs. Scanned PDFs must be converted to images first.
**Dependency:** Requires Poppler installed at system level

---

### Poppler 24.08.0 (System Tool)
**Role:** PDF rendering engine required by pdf2image
**What it does:**
- Low-level PDF parsing and rendering library
- Installed at: `C:\poppler\Library\bin\`
- pdf2image calls `pdftoppm.exe` from Poppler to do the actual conversion
**Why needed:**
- pdf2image is just a Python wrapper — Poppler does the real work

---

### Pillow 12.1.1
**Role:** Python image processing library
**What it does:**
- Opens image files (JPG, PNG, TIFF, BMP) as PIL Image objects
- pytesseract accepts PIL Image objects as input
- Also used internally by pdf2image for page image handling

---

### Pydantic v2.12.5
**Role:** Data validation and schema enforcement
**What it does:**
- Define data models with typed fields (str, float, date, Optional)
- Validate every extracted record before saving
- Custom field validators enforce business rules
- ValidationError raised immediately for bad data — never reaches storage

**Two schemas defined:**
```
ReceiptSchema:
  - file_name: str (required)
  - vendor_name: Optional[str]
  - receipt_number: Optional[str]
  - date_paid: Optional[str]
  - amount_paid: Optional[float] → must be positive
  - item_description: Optional[str]

InvoiceSchema:
  - file_name: str (required)
  - vendor_name: Optional[str]
  - invoice_number: Optional[str]
  - invoice_date: Optional[str]
  - due_date: Optional[str]
  - total_amount: Optional[float] → must be positive
```

**Why Pydantic matters:**
In production pipelines, silent data errors are dangerous. Without validation,
a corrupted OCR reading like "hello" for an amount field would be inserted into
the database as-is, breaking downstream analytics. Pydantic catches this immediately.

---

### PostgreSQL 17.9
**Role:** Relational database for structured data storage
**What it does:**
- Stores all validated records in structured tables
- Supports SQL queries for reporting and analytics
- ON CONFLICT handling prevents duplicate inserts at the database level
- Runs locally on port 5432

**Tables created:**
```sql
receipts (
    id              SERIAL PRIMARY KEY,
    file_name       TEXT,
    vendor_name     TEXT,
    receipt_number  TEXT UNIQUE,
    date_paid       TEXT,
    amount_paid     FLOAT,
    item_description TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
)

invoices (
    id              SERIAL PRIMARY KEY,
    file_name       TEXT,
    vendor_name     TEXT,
    invoice_number  TEXT UNIQUE,
    invoice_date    TEXT,
    due_date        TEXT,
    total_amount    FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
)
```

---

### psycopg2-binary 2.9.11
**Role:** Python-PostgreSQL database connector
**What it does:**
- Provides Python API for PostgreSQL connections
- Executes SQL queries: INSERT, SELECT, CREATE TABLE
- `RealDictCursor` returns rows as Python dictionaries
- Connection pooling and transaction management

---

### ChromaDB 1.5.5
**Role:** Vector database for semantic search and RAG support
**What it does:**
- Stores document text as high-dimensional vector embeddings
- Each document is converted into a 384-dimension vector
- Similar documents have similar vectors (close in vector space)
- `collection.query(query_texts=["..."], n_results=3)` — semantic search
- Persistent storage in `chroma_db/` folder

**Embedding model used:**
- `all-MiniLM-L6-v2` — sentence transformer model
- Converts text to 384-dimensional embeddings
- Optimized for semantic similarity tasks
- Downloaded automatically on first run (~80MB)

**Why ChromaDB for RAG:**
- RAG (Retrieval Augmented Generation) requires finding relevant documents
  given a user query, then passing those documents to an LLM
- ChromaDB is the retrieval layer — it finds the most semantically relevant
  documents for any query
- This pipeline is the data ingestion component of a RAG system

---

### hashlib (Python Standard Library)
**Role:** MD5 file hashing for deduplication
**What it does:**
- Reads file as binary
- Computes MD5 hash — unique fingerprint of file content
- Same file content always produces the same hash
- Hashes stored in `logs/seen_hashes.json` across runs

---

### Docker
**Role:** Containerization for portable deployment
**What it does:**
- Packages Python, Tesseract, Poppler, and all pip packages into one image
- Based on `python:3.11-slim` for minimal image size
- `apt-get install tesseract-ocr poppler-utils` at build time
- `pip install -r requirements.txt` installs all Python dependencies
- `CMD ["python", "scripts/run_pipeline.py"]` runs pipeline on container start

---

## 6. COMPONENT DEEP DIVE — EVERY SCRIPT EXPLAINED

---

### detect_files.py

**Purpose:** Scan input folder and classify each file by type

**Logic:**
```
For each file in input_docs/:
    Get file extension (.pdf, .jpg, .png, etc.)

    If extension is .pdf:
        Open with pypdf
        Try to extract text from first page
        If text found and not empty → "text_pdf"
        If text empty → "scanned_pdf"

    If extension is .jpg / .jpeg / .png / .tiff / .bmp:
        → "image"

    Otherwise:
        → "unsupported" (skip this file)

Return list of {file_path, file_name, file_type}
```

**Why file type detection matters:**
Running OCR on a text PDF wastes time and reduces accuracy.
Running pypdf on an image returns nothing.
Smart routing is essential for pipeline efficiency.

---

### extract_pdf_text.py

**Purpose:** Extract text directly from text-based PDFs

**Logic:**
```
Open PDF file with PdfReader
For each page in reader.pages:
    Extract text: page.extract_text()
    If text is not empty:
        Add page marker: "--- Page N ---"
        Append text to output string
Write combined text to raw_text/filename.txt
```

**Key detail:**
Page markers (`--- Page 1 ---`) are added to preserve document structure.
This helps field extraction know which part of the document it is reading.

---

### ocr_extract.py

**Purpose:** Extract text from scanned PDFs and images using OCR

**For scanned PDFs:**
```
Convert PDF pages to PIL images using pdf2image (DPI=300)
For each page image:
    Run pytesseract.image_to_string(image)
    Add page marker
    Append to output string
Write to raw_text/filename.txt
```

**For image files (JPG, PNG):**
```
Open image with PIL Image.open()
Run pytesseract.image_to_string(image)
Write to raw_text/filename.txt
```

**DPI=300 explanation:**
Higher DPI = higher resolution images = better OCR accuracy.
300 DPI is the industry standard for document OCR.
Lower DPI (72, 96) causes Tesseract to misread characters.

**Tesseract path hardcoded:**
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
This ensures the pipeline finds Tesseract regardless of PATH configuration.

---

### clean_text.py

**Purpose:** Normalize raw extracted text for consistent field extraction

**Cleaning operations in order:**

1. **Replace tabs with spaces**
   `text.replace("\t", " ")`
   Tabs from PDF tables become spaces

2. **Remove non-printable characters**
   `re.sub(r"[^\x20-\x7E\n]", " ", text)`
   Keeps only standard ASCII printable characters (space through ~)
   Removes: weird Unicode, control characters, OCR artifacts

3. **Collapse multiple spaces**
   `re.sub(r" {2,}", " ", text)`
   "Invoice   Number" becomes "Invoice Number"

4. **Filter junk lines**
   Lines with no alphanumeric characters are removed
   A line of just "---@@---" provides no value

5. **Limit consecutive blank lines**
   Maximum one blank line between sections
   Prevents excessive whitespace in output

**Why cleaning is critical:**
Regex field extraction relies on consistent patterns.
`"Invoice  Number:  INV-3337"` (double spaces) may not match
a regex written for `"Invoice Number: INV-3337"` (single spaces).
Cleaning standardizes the input so patterns work reliably.

---

### extract_fields.py

**Purpose:** Find and extract specific data fields from cleaned text

**Document type detection:**
```python
if "Receipt" in text and "AMOUNT PAID" in text:
    → extract_receipt_fields(text)
else:
    → extract_invoice_fields(text)
```

**Receipt field extraction:**

| Field | Regex Pattern | Example Match |
|---|---|---|
| vendor_name | `Receipt from ([A-Z][A-Z\s]+LLC)` | AURBORBLOOM LLC |
| receipt_number | `(?:Receipt\s*)?#([\d]{4}-[\d]{4})` | 1055-6311 |
| date_paid | `(Jan\|Feb\|Mar...)\s+\d{1,2},\s+\d{4}` | Mar 17, 2026 |
| amount_paid | `Amount paid\s+\$?([\d,]+\.\d{2})` | 150.00 |
| item_description | `([A-Za-z...]+)\s+x\s+1\s+\$` | C# & .NET Basics |

**Invoice field extraction:**

| Field | Regex Pattern | Example Match |
|---|---|---|
| invoice_number | `Invoice\s*Number\s+([A-Z]{2,5}-\d+)` | INV-3337 |
| invoice_date | `Invoice\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4})` | January 25, 2016 |
| due_date | `Due\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4})` | January 31, 2016 |
| vendor_name | `From:\s*\n([^\n]+)` | DEMO - Sliced Invoices |
| total_amount | `Total\s+\$?([\d,]+\.\d{2})` | 250.00 |

**Why rule-based regex over LLM:**
- Deterministic: same input always gives same output
- No API cost, no latency, no rate limits
- Fully auditable: you can inspect exactly which pattern matched
- Fast: regex runs in microseconds
- LLMs can be added as a fallback for complex edge cases later

---

### to_json.py

**Purpose:** Validate extracted fields and save as structured JSON

**Validation flow:**
```
Pass fields dict to Pydantic schema
→ If document_type == "receipt" → ReceiptSchema(**fields)
→ If document_type == "invoice" → InvoiceSchema(**fields)

If validation passes:
    → model.model_dump() returns clean dict
    → Write to json_output/filename.json with indent=4

If validation fails:
    → ValidationError caught
    → Error message logged
    → File marked as failed
    → No JSON saved
```

**JSON output format (receipt):**
```json
{
    "file_name": "receipt_001.txt",
    "document_type": "receipt",
    "vendor_name": "AURBORBLOOM LLC",
    "receipt_number": "1148-2760",
    "date_paid": "Feb 27, 2026",
    "amount_paid": 130.0,
    "item_description": "Full Stack Software Testing"
}
```

---

### deduplicate.py

**Purpose:** Prevent processing the same document twice

**Layer 1 — File Hash Deduplication:**
```python
def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()
```
- Reads file as bytes (binary mode)
- MD5 produces a 32-character hex string fingerprint
- Same file content → same hash, always
- Stored in `logs/seen_hashes.json` after first processing
- On second run: hash found → skip file → log as duplicate

**Layer 2 — Field-Level Deduplication:**
```python
# For receipts: compare receipt_number + amount_paid
# For invoices: compare invoice_number + total_amount
```
- Catches cases where the same document was renamed and dropped again
- Compares extracted fields against all previously processed records in current run

**Persistence:**
```json
{
    "a1b2c3d4e5f6...": "receipt_001.jpeg",
    "f6e5d4c3b2a1...": "invoice_001.pdf"
}
```
Hash file persists across pipeline runs so duplicates are detected
even if the pipeline is restarted.

---

### database.py

**Purpose:** Save validated records to PostgreSQL

**Connection:**
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pipeline_db",
    "user": "postgres",
    "password": "postgres123"
}
psycopg2.connect(**DB_CONFIG)
```

**Table creation:**
- `CREATE TABLE IF NOT EXISTS` — idempotent, safe to run multiple times
- `receipt_number TEXT UNIQUE` — database-level duplicate prevention
- `created_at TIMESTAMP DEFAULT NOW()` — automatic record timestamps

**Insert with conflict handling:**
```sql
INSERT INTO receipts (file_name, vendor_name, receipt_number, ...)
VALUES (%s, %s, %s, ...)
ON CONFLICT (receipt_number) DO NOTHING
RETURNING id;
```
- `ON CONFLICT DO NOTHING` — if receipt_number already exists, skip silently
- `RETURNING id` — if insert succeeded, returns the new row ID
- If result is None → duplicate was skipped at DB level

**Useful analytical queries:**
```sql
-- Total spend per vendor
SELECT vendor_name, SUM(amount_paid) as total
FROM receipts GROUP BY vendor_name;

-- All receipts this month
SELECT * FROM receipts
WHERE date_paid LIKE '%2026%';

-- Receipts above $100
SELECT * FROM receipts WHERE amount_paid > 100;
```

---

### vector_store.py

**Purpose:** Store documents as vector embeddings in ChromaDB for semantic search

**ChromaDB setup:**
```python
client = chromadb.PersistentClient(path="chroma_db/")
collection = client.get_or_create_collection(
    name="documents",
    embedding_function=DefaultEmbeddingFunction()
)
```
- `PersistentClient` — saves vectors to disk, survives restarts
- `DefaultEmbeddingFunction` — uses `all-MiniLM-L6-v2` model
- Collection is created on first run, reused on subsequent runs

**Document storage:**
```python
collection.upsert(
    ids=[doc_id],           # unique identifier
    documents=[text],       # full cleaned text to embed
    metadatas=[metadata]    # extracted fields as metadata
)
```
- `upsert` — insert if new, update if exists (idempotent)
- The embedding model converts the text to a 384-dimension vector
- Metadata stored alongside vector for retrieval

**Semantic search:**
```python
results = collection.query(
    query_texts=["software training payment"],
    n_results=3
)
```
- Query text is converted to a vector
- ChromaDB finds the N closest document vectors
- Returns documents, metadata, and distance scores

**How semantic search works:**
```
"software training payment"
         ↓ embed
[0.23, -0.45, 0.12, ...] (384 numbers)
         ↓ compare with stored vectors
"C# .NET Basics receipt"    → distance: 0.15 (very similar)
"Full Stack Testing receipt" → distance: 0.18 (very similar)
"Pizza restaurant receipt"   → distance: 0.87 (very different)
```

---

### run_pipeline.py

**Purpose:** Master orchestrator — runs all steps in sequence for every file

**Pipeline steps per file:**
```
1. detect_file_type()
2. if unsupported → skip
3. is_duplicate(file_hash) → if yes, skip
4. if text_pdf → process_text_pdf()
   if image/scanned → process_ocr_file()
5. clean_text()
6. extract_fields_from_file()
7. check_duplicate_fields() → if yes, skip
8. process_to_json() → Pydantic validation
9. save_to_database() → PostgreSQL
10. store_document() → ChromaDB
11. log result
```

**Error isolation:**
Each step is wrapped in try/except. If one file fails at any step,
the error is logged and the pipeline moves to the next file.
One bad document never stops the entire pipeline.

**Stats tracking:**
```python
stats = {
    "total": 4,
    "success": 3,
    "failed": 0,
    "duplicate": 1,
    "skipped": 0
}
```
Final summary printed and logged at end of every run.

---

## 7. DATA FLOW — STEP BY STEP

### Example: WhatsApp Receipt Photo

```
File: "WhatsApp Image 2026-03-23 at 10.11.06 PM.jpeg"

STEP 1 — Detection
detect_files.py reads extension: .jpeg
→ file_type = "image"

STEP 2 — OCR Extraction
ocr_extract.py opens image with PIL
pytesseract.image_to_string() runs Tesseract
→ Raw text extracted:
"Receipt from AURBORBLOOM LLC
Receipt #1148-2760
AMOUNT PAID DATE PAID PAYMENT METHOD
$130.00 Feb 27, 2026, 11:58:31 AM - 7524
SUMMARY
Full Stack Software Testing x 1 $130.00
Amount paid $130.00"

Saved to: raw_text/WhatsApp Image 2026-03-23 at 10.11.06 PM.txt

STEP 3 — Text Cleaning
clean_text.py normalizes the text:
→ Removes OCR artifacts
→ Fixes spacing
→ Saves to: clean_text/WhatsApp Image 2026-03-23 at 10.11.06 PM.txt

STEP 4 — Field Extraction
extract_fields.py detects "Receipt" + "AMOUNT PAID" → receipt type
→ vendor_name: "AURBORBLOOM LLC"   (regex: "Receipt from ([A-Z]+LLC)")
→ receipt_number: "1148-2760"       (regex: "#(\d{4}-\d{4})")
→ date_paid: "Feb 27, 2026"         (regex: month + day + year)
→ amount_paid: 130.0                 (regex: "Amount paid \$(\d+\.\d{2})")
→ item_description: "Full Stack Software Testing"

STEP 5 — Pydantic Validation
ReceiptSchema(**fields) called
→ vendor_name: str ✓
→ receipt_number: str ✓
→ date_paid: str ✓
→ amount_paid: 130.0 (float, positive) ✓
→ VALIDATION PASSED

STEP 6 — Deduplication
hash_file("WhatsApp Image...jpeg") → "a1b2c3..."
Check seen_hashes.json → not found
→ NEW FILE, continue
→ Save hash to seen_hashes.json

STEP 7 — JSON Save
json_output/WhatsApp Image 2026-03-23 at 10.11.06 PM.json written:
{
    "file_name": "...",
    "document_type": "receipt",
    "vendor_name": "AURBORBLOOM LLC",
    "receipt_number": "1148-2760",
    "date_paid": "Feb 27, 2026",
    "amount_paid": 130.0,
    "item_description": "Full Stack Software Testing"
}

STEP 8 — PostgreSQL Insert
INSERT INTO receipts (...) VALUES (...)
→ DB INSERT: receipt saved (id=3)

STEP 9 — ChromaDB Store
collection.upsert(id="WhatsApp_Image...", documents=[cleaned_text])
→ all-MiniLM-L6-v2 converts text to 384-dim vector
→ CHROMA STORED: WhatsApp_Image_2026-03-23_at_10.11.06_PM

STEP 10 — Log
2026-03-26 21:12:10 [INFO] SUCCESS: WhatsApp Image...jpeg → json_output/...json
2026-03-26 21:12:10 [INFO] DB saved: WhatsApp Image...jpeg
2026-03-26 21:12:10 [INFO] Vector stored: WhatsApp Image...jpeg
```

---

## 8. SAMPLE INPUTS AND OUTPUTS

### Input File Types Tested

| File | Type | Extraction Method |
|---|---|---|
| wordpress-pdf-invoice-plugin-sample.pdf | Text PDF | pypdf direct extraction |
| WhatsApp Image 2026-03-23 at 10.10.02 PM (1).jpeg | Phone photo | Tesseract OCR |
| WhatsApp Image 2026-03-23 at 10.10.02 PM.jpeg | Phone photo | Tesseract OCR |
| WhatsApp Image 2026-03-23 at 10.11.06 PM.jpeg | Phone photo | Tesseract OCR |

### Sample JSON Outputs

**Receipt:**
```json
{
    "file_name": "WhatsApp Image 2026-03-23 at 10.11.06 PM.txt",
    "document_type": "receipt",
    "vendor_name": "AURBORBLOOM LLC",
    "receipt_number": "1148-2760",
    "date_paid": "Feb 27, 2026",
    "amount_paid": 130.0,
    "item_description": "Full Stack Software Testing"
}
```

**Invoice:**
```json
{
    "file_name": "wordpress-pdf-invoice-plugin-sample.txt",
    "document_type": "invoice",
    "vendor_name": "DEMO - Sliced Invoices",
    "invoice_number": "INV-3337",
    "invoice_date": "January 25, 2016",
    "due_date": "January 31, 2016",
    "total_amount": 1.0
}
```

---

## 9. DATABASE DESIGN

### Schema

```sql
CREATE TABLE receipts (
    id               SERIAL PRIMARY KEY,
    file_name        TEXT NOT NULL,
    vendor_name      TEXT,
    receipt_number   TEXT UNIQUE,      -- prevents duplicate receipts
    date_paid        TEXT,
    amount_paid      FLOAT,
    item_description TEXT,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invoices (
    id              SERIAL PRIMARY KEY,
    file_name       TEXT NOT NULL,
    vendor_name     TEXT,
    invoice_number  TEXT UNIQUE,       -- prevents duplicate invoices
    invoice_date    TEXT,
    due_date        TEXT,
    total_amount    FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Analytical Queries

```sql
-- Total spend per vendor
SELECT vendor_name, SUM(amount_paid) AS total_spent,
       COUNT(*) AS num_receipts
FROM receipts
GROUP BY vendor_name
ORDER BY total_spent DESC;

-- All receipts above $100
SELECT vendor_name, receipt_number, amount_paid, date_paid
FROM receipts
WHERE amount_paid > 100
ORDER BY amount_paid DESC;

-- Invoices with due dates
SELECT vendor_name, invoice_number, invoice_date, due_date, total_amount
FROM invoices
ORDER BY invoice_date;
```

---

## 10. VECTOR DATABASE AND SEMANTIC SEARCH

### How Embeddings Work

When a document is stored in ChromaDB:

```
"Full Stack Software Testing receipt from AURBORBLOOM LLC, $130"
                        ↓
            all-MiniLM-L6-v2 model
                        ↓
    [0.23, -0.45, 0.12, 0.87, -0.33, ...] (384 numbers)
                        ↓
            Stored in ChromaDB
```

When a query is made:

```
Query: "coding course payment"
                        ↓
            all-MiniLM-L6-v2 model
                        ↓
    [0.21, -0.42, 0.15, 0.85, -0.31, ...] (384 numbers)
                        ↓
    Compare with stored vectors (cosine similarity)
                        ↓
    "Full Stack Software Testing" → similarity: 0.92 ✓ (very close)
    "C# .NET Basics"             → similarity: 0.88 ✓ (close)
    "Sliced Invoices invoice"    → similarity: 0.31   (far apart)
```

### Semantic Search Results

```
Query: "software training payment"
→ Match 1: AURBORBLOOM LLC | Full Stack Software Testing | $130.00
→ Match 2: AURBORBLOOM LLC | C# & .NET Basics | $150.00

Query: "invoice from sliced invoices"
→ Match 1: DEMO - Sliced Invoices | INV-3337 | $1.00
→ Match 2: AURBORBLOOM LLC | C# & .NET Basics | $150.00

Query: "full stack course receipt"
→ Match 1: AURBORBLOOM LLC | Full Stack Software Testing | $130.00
→ Match 2: AURBORBLOOM LLC | C# & .NET Basics | $150.00
```

### RAG Integration Potential

This pipeline is the data ingestion layer of a RAG system:

```
User Question: "How much did I spend on software courses?"
                        ↓
        ChromaDB semantic search finds relevant receipts
                        ↓
        Retrieved documents passed to LLM as context
                        ↓
        LLM answers: "You spent $280 on software courses —
        $150 for C# .NET Basics and $130 for Full Stack Testing"
```

---

## 11. DATA QUALITY FRAMEWORK

### Three Layers of Data Quality

**Layer 1 — Text Quality (clean_text.py)**
- Remove OCR artifacts before field extraction
- Normalize whitespace for consistent regex matching
- Filter lines with no meaningful content

**Layer 2 — Schema Validation (Pydantic)**
- Type checking: amount must be float, not string
- Business rule validation: amount must be positive
- Required field checking
- Rejection of invalid records before storage

**Layer 3 — Deduplication (deduplicate.py)**
- File-level: MD5 hash prevents exact duplicate files
- Field-level: key field comparison prevents renamed duplicates
- Database-level: UNIQUE constraints prevent duplicate DB records

### What Happens to Bad Data

```
Scenario: OCR misreads amount as "15O.OO" (letter O instead of zero)

→ extract_fields.py regex: r"Amount paid\s+\$?([\d,]+\.\d{2})"
  → "15O.OO" does not match (non-digit characters) → amount_paid = None

→ Pydantic ReceiptSchema validation:
  → amount_paid = None → passes (Optional field)
  → record saved with null amount

→ Logged: [WARNING] amount_paid not found in receipt_001.jpeg

→ Database: amount_paid column is NULL for this record
  → Visible in queries, can be reviewed and corrected manually
```

---

## 12. OBSERVABILITY AND LOGGING

### Log Structure

Every log entry follows the format:
```
YYYY-MM-DD HH:MM:SS [LEVEL] Message
```

### Log Levels Used

| Level | When Used | Example |
|---|---|---|
| INFO | Normal events | `SUCCESS: invoice.pdf → json_output/invoice.json` |
| INFO | Database operations | `DB saved: invoice.pdf` |
| INFO | Vector operations | `Vector stored: invoice.pdf` |
| WARNING | Skipped events | `SKIPPED (duplicate file): invoice_copy.pdf` |
| ERROR | Failures | `FAILED (validation): receipt.jpg - amount must be positive` |

### Sample Pipeline Log

```
2026-03-26 21:12:04 [INFO] ============================================================
2026-03-26 21:12:04 [INFO] PIPELINE STARTED
2026-03-26 21:12:04 [INFO] ============================================================
2026-03-26 21:12:04 [INFO] Scanning input folder: .../input_docs
2026-03-26 21:12:04 [INFO] Found 4 files
2026-03-26 21:12:04 [INFO] --- Processing: receipt_001.jpeg [image] ---
2026-03-26 21:12:07 [INFO] Text cleaned: .../clean_text/receipt_001.txt
2026-03-26 21:12:07 [INFO] Fields extracted: [vendor, receipt_number, date, amount, item]
2026-03-26 21:12:07 [INFO] SUCCESS: receipt_001.jpeg → json_output/receipt_001.json
2026-03-26 21:12:07 [INFO] DB saved: receipt_001.jpeg
2026-03-26 21:12:07 [INFO] Vector stored: receipt_001.jpeg
2026-03-26 21:12:08 [WARNING] SKIPPED (duplicate file): receipt_001_copy.jpeg
2026-03-26 21:12:11 [INFO] ============================================================
2026-03-26 21:12:11 [INFO] PIPELINE COMPLETE
2026-03-26 21:12:11 [INFO]   Total files   : 4
2026-03-26 21:12:11 [INFO]   Successful    : 3
2026-03-26 21:12:11 [INFO]   Failed        : 0
2026-03-26 21:12:11 [INFO]   Duplicates    : 1
2026-03-26 21:12:11 [INFO]   Skipped       : 0
2026-03-26 21:12:11 [INFO] ============================================================
```

---

## 13. CONTAINERIZATION

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies: Tesseract OCR + Poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p input_docs raw_text clean_text json_output logs chroma_db

CMD ["python", "scripts/run_pipeline.py"]
```

### Why Docker Matters

Without Docker:
- Tesseract must be installed manually on every machine
- Poppler must be added to PATH manually
- Python version conflicts between machines
- "Works on my machine" problem

With Docker:
- One `docker build` installs everything
- Runs identically on Windows, Mac, Linux, or any cloud server
- Ready for Kubernetes deployment
- CI/CD pipeline integration

### Build and Run Commands

```bash
# Build image
docker build -t document-pipeline .

# Run pipeline (mount input folder)
docker run -v $(pwd)/input_docs:/app/input_docs \
           -v $(pwd)/json_output:/app/json_output \
           document-pipeline
```

---


---

## 14. FUTURE ROADMAP

### Short Term
- **FastAPI REST endpoint** — accept file uploads via HTTP POST, return JSON
- **Airflow DAG** — scheduled pipeline execution with retry logic
- **LLM fallback extraction** — for documents where regex fails

### Medium Term
- **AWS S3 integration** — read input files from S3 bucket
- **AWS RDS** — replace local PostgreSQL with managed cloud database
- **Pinecone / Weaviate** — replace local ChromaDB with managed vector DB
- **Apache Spark** — distributed processing for high document volumes

### Long Term
- **Delta Lake / Apache Iceberg** — data lakehouse for versioned datasets
- **MLflow / DVC** — dataset versioning and lineage tracking
- **Kubernetes** — container orchestration for production scaling
- **pgvector** — PostgreSQL-native vector extension

---

## 15. ABOUT

**Vishal S**
AI Data & Platform Engineer
vishalaiml97@gmail.com

Specializing in building data pipelines for AI/ML systems —
ETL workflows, unstructured data processing, OCR pipelines,
vector databases, schema validation, and production-grade
data infrastructure.

---

*Built with: Python 3.13 | Tesseract OCR v5.5 | pypdf | pdf2image |
pytesseract | Pillow | Pydantic v2 | PostgreSQL 17 | ChromaDB |
psycopg2 | hashlib | Docker*
