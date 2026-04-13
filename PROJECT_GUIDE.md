# Local Document Processing Pipeline
## Complete Project Guide — Interview Preparation & Demo

---

## TABLE OF CONTENTS

1. Project Overview
2. Architecture Diagram
3. Complete Skill Breakdown
4. Script-by-Script Explanation
5. How to Demo (Step-by-Step)
6. Interview Questions & Answers
7. JD Keyword Mapping

---

## 1. PROJECT OVERVIEW

### What You Built
A local ETL (Extract, Transform, Load) pipeline that:
- Reads PDF and image files from an input folder
- Extracts text using either direct PDF reading or OCR
- Cleans and normalizes the extracted text
- Pulls important fields (vendor, amount, date, receipt/invoice number)
- Validates data using schema validation
- Deduplicates to avoid processing the same file twice
- Saves output as structured JSON
- Stores records in PostgreSQL (relational database)
- Stores document vectors in ChromaDB (vector database) for semantic search
- Logs every step with timestamps

### One-Line Summary for Interview
> "I built a local document processing pipeline that ingests raw PDFs and scanned images,
> extracts structured data using OCR and regex, validates it with Pydantic, deduplicates
> using file hashing, and stores results in both PostgreSQL and ChromaDB for querying and
> semantic search."

---

## 2. ARCHITECTURE DIAGRAM

```
INPUT
  input_docs/
  (PDF, JPEG, PNG)
       |
       v
  detect_files.py
  (What type is this file?)
       |
       |--- text PDF ---------> extract_pdf_text.py (pypdf)
       |--- scanned PDF ------> ocr_extract.py (pdf2image + pytesseract)
       |--- image (JPG/PNG) --> ocr_extract.py (pytesseract)
       |
       v
  raw_text/filename.txt
  (raw extracted text)
       |
       v
  clean_text.py
  (remove junk, fix spaces, normalize)
       |
       v
  clean_text/filename.txt
  (clean normalized text)
       |
       v
  extract_fields.py
  (regex patterns find: vendor, amount, date, number)
       |
       v
  Pydantic Validation
  (is the data valid? correct types?)
       |
       |--- INVALID --> log error, skip file
       |--- VALID   --> continue
       |
       v
  deduplicate.py
  (MD5 hash check — seen before?)
       |
       |--- DUPLICATE --> skip, log
       |--- NEW       --> continue
       |
       v
  to_json.py
  (save structured JSON)
       |
       v
  json_output/filename.json
       |
       |---------> database.py ---------> PostgreSQL (pipeline_db)
       |---------> vector_store.py -----> ChromaDB (semantic search)
       |
       v
  logs/pipeline.log
  (full audit trail)
```

---

## 3. COMPLETE SKILL BREAKDOWN

---

### SKILL 1: Python (Core Language)
**Where used:** Every single script in the project

**What it does:**
- All business logic is written in Python
- File I/O, string manipulation, regex, logging
- Connects all tools together

**How to explain in interview:**
> "Python was the natural choice because it has the richest ecosystem for
> document processing, OCR, data validation, and database connectivity.
> I used Python 3.13 with a virtual environment to keep dependencies isolated."

**Key Python concepts used:**
- `os` and `pathlib` for file system operations
- `re` module for regex pattern matching
- `logging` module for structured logs
- `json` module for reading/writing JSON
- `hashlib` for MD5 file hashing
- f-strings, list comprehensions, exception handling

---

### SKILL 2: OCR — Tesseract + pytesseract
**Where used:** `scripts/ocr_extract.py`

**What it does:**
- Tesseract OCR is a Google open-source engine that reads text from images
- pytesseract is the Python wrapper that calls Tesseract from code
- Converts pixel-based text (in scanned PDFs and photos) into actual string data
- Used on all 3 WhatsApp receipt images in this project

**How to explain in interview:**
> "Not all PDFs have extractable text — scanned documents and photos are just
> images of text. I used Tesseract OCR, called through pytesseract in Python,
> to recognize and extract text from those image files. For scanned PDFs,
> I first converted pages to images using pdf2image, then ran OCR on each page."

**Demo talking point:**
Show the raw JPEG receipt → show the extracted text → they'll be impressed OCR
pulled out structured data from a phone photo.

---

### SKILL 3: PDF Text Extraction — pypdf
**Where used:** `scripts/extract_pdf_text.py`

**What it does:**
- Reads text directly from text-based PDF files
- Text-based PDFs (like exported Word documents) have embedded text
- pypdf reads that text without needing OCR
- Much faster and more accurate than OCR for text PDFs

**How to explain in interview:**
> "I used pypdf to extract text from text-based PDFs directly. Before running OCR,
> the pipeline checks if the PDF has extractable text. If yes, we use pypdf — it's
> faster and more accurate. If the PDF is scanned and has no embedded text, we
> fall back to OCR."

---

### SKILL 4: pdf2image + Poppler
**Where used:** `scripts/ocr_extract.py`

**What it does:**
- pdf2image converts each page of a PDF into a PNG/JPEG image
- Poppler is the underlying rendering engine pdf2image depends on
- Required because Tesseract can only read images, not PDF files directly
- Each page becomes a separate image, OCR runs on each page

**How to explain in interview:**
> "Tesseract reads images, not PDFs. So for scanned PDFs, I used pdf2image
> to convert each page into an image first, then ran OCR. pdf2image depends
> on Poppler, a PDF rendering library, which I installed separately on the system."

---

### SKILL 5: Data Cleaning — Regex + String Processing
**Where used:** `scripts/clean_text.py`

**What it does:**
- Raw OCR output is messy: double spaces, broken lines, junk symbols
- Regex patterns remove non-printable characters
- Multiple spaces collapsed to single spaces
- Junk-only lines (no alphanumeric content) removed
- Normalized output saved to clean_text/ folder

**How to explain in interview:**
> "Raw OCR output always has noise — extra whitespace, broken characters, symbols.
> I wrote a cleaning step that normalizes the text before field extraction.
> This is critical because regex patterns for field extraction need clean,
> consistent input to work reliably."

**Key regex patterns used:**
```python
re.sub(r"[^\x20-\x7E\n]", " ", text)   # remove non-printable chars
re.sub(r" {2,}", " ", text)              # collapse multiple spaces
re.search(r"[a-zA-Z0-9]", stripped)     # keep only lines with real content
```

---

### SKILL 6: Field Extraction — Rule-Based Regex
**Where used:** `scripts/extract_fields.py`

**What it does:**
- Finds specific data fields inside cleaned text using pattern matching
- No AI/LLM — purely rule-based regex
- Separate functions for receipts vs invoices
- Extracts: vendor name, receipt/invoice number, date, amount, item description

**How to explain in interview:**
> "For field extraction I used rule-based regex, not an LLM. For structured
> documents like invoices and receipts, the fields always appear in predictable
> patterns. Regex is faster, cheaper, fully explainable, and doesn't require
> an API call. I can always add LLM extraction later for edge cases."

**Key regex patterns:**
```python
# Receipt number
re.search(r"(?:Receipt\s*)?#([\d]{4}-[\d]{4})", text)

# Date (Month DD, YYYY)
re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},\s+\d{4}", text)

# Amount paid
re.search(r"Amount paid\s+\$?([\d,]+\.\d{2})", text)

# Invoice number
re.search(r"Invoice\s*Number\s+([A-Z]{2,5}-\d+)", text)
```

---

### SKILL 7: Schema Validation — Pydantic
**Where used:** `scripts/to_json.py`

**What it does:**
- Defines strict schemas for Receipt and Invoice data
- Validates every extracted record before saving
- Catches type errors: string where float expected, negative amounts, etc.
- Invalid records are logged and rejected — never reach the database

**How to explain in interview:**
> "Pydantic gives me schema validation at the Python level. Before any data
> touches the database, it must pass validation. For example, amount_paid must
> be a positive float — if OCR extracted 'hello' instead of a number, Pydantic
> catches it immediately and logs the error. This prevents silent data corruption,
> which is a real problem in production pipelines."

**Pydantic schemas:**
```python
class ReceiptSchema(BaseModel):
    file_name: str
    vendor_name: Optional[str]
    receipt_number: Optional[str]
    date_paid: Optional[str]
    amount_paid: Optional[float]

    @field_validator("amount_paid")
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("amount must be positive")
        return v
```

---

### SKILL 8: Deduplication — MD5 File Hashing
**Where used:** `scripts/deduplicate.py`

**What it does:**
- Every input file gets an MD5 hash computed from its binary content
- Hash is stored in logs/seen_hashes.json after first processing
- On next run, if hash already exists → file is skipped as duplicate
- Secondary check: compare key fields (receipt_number + amount) to catch renamed duplicates
- Prevents duplicate records in PostgreSQL and ChromaDB

**How to explain in interview:**
> "In real data pipelines, the same file gets dropped into the input folder
> multiple times — by mistake, by retry logic, or by multiple users.
> I implemented two layers of deduplication: first an MD5 file hash check
> to catch exact duplicates, and second a field-level comparison to catch
> renamed duplicates. This is essential for data quality in any production ETL."

**How hashing works:**
```python
def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()
# Same file content = same hash, regardless of filename
```

---

### SKILL 9: JSON Output
**Where used:** `scripts/to_json.py`

**What it does:**
- Saves validated extracted fields as structured JSON files
- One JSON file per processed document
- Stored in json_output/ folder
- Serves as intermediate format between extraction and database storage

**Sample output:**
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

---

### SKILL 10: PostgreSQL — Relational Database
**Where used:** `scripts/database.py`

**What it does:**
- Creates two tables: receipts and invoices
- Inserts validated records after each successful pipeline run
- Uses ON CONFLICT DO NOTHING to prevent duplicate DB entries
- Supports SQL queries for reporting and analysis

**How to explain in interview:**
> "I used PostgreSQL to persist extracted data in a relational database.
> This allows querying across all processed documents — for example,
> show all receipts from a specific vendor, or find all invoices above
> a certain amount. I used psycopg2 as the Python connector and implemented
> ON CONFLICT handling to prevent duplicate inserts at the database level
> as a second safety layer after the pipeline deduplication."

**Useful demo queries:**
```sql
-- All receipts
SELECT * FROM receipts;

-- Receipts over $100
SELECT vendor_name, amount_paid, date_paid
FROM receipts WHERE amount_paid > 100;

-- Total spent per vendor
SELECT vendor_name, SUM(amount_paid) as total
FROM receipts GROUP BY vendor_name;
```

---

### SKILL 11: ChromaDB — Vector Database
**Where used:** `scripts/vector_store.py`

**What it does:**
- Stores cleaned document text as vector embeddings
- Uses sentence-transformers (all-MiniLM-L6-v2) to generate embeddings
- Allows semantic similarity search — find documents by meaning, not keywords
- Persistent storage in chroma_db/ folder
- Can find similar documents even if exact words don't match

**How to explain in interview:**
> "ChromaDB is a vector database that stores documents as mathematical
> representations of their meaning — called embeddings. This lets me search
> by concept rather than exact keyword. For example, searching 'software
> training payment' finds receipts for '.NET Basics' and 'Full Stack Testing'
> because they're semantically similar even though the exact phrase doesn't
> appear. This is the foundation of RAG (Retrieval Augmented Generation)
> systems, which is a key use case in modern AI data platforms."

**Why vector databases matter:**
- Traditional DB: WHERE description = 'software course' (exact match only)
- Vector DB: find documents semantically similar to 'software course'
  → finds 'C# .NET Basics', 'Full Stack Testing', 'coding bootcamp', etc.

---

### SKILL 12: Logging — Python logging module
**Where used:** `scripts/run_pipeline.py`

**What it does:**
- Structured logging to both console and file (logs/pipeline.log)
- Timestamps on every log entry
- INFO level for normal events, WARNING for skips, ERROR for failures
- Complete audit trail of every pipeline run

**How to explain in interview:**
> "Production pipelines need observability. I used Python's logging module
> to write structured logs to both the console and a log file. Every file
> processed gets a timestamped entry — success, failure, duplicate, or skip.
> If something goes wrong in production, the log file tells you exactly
> what failed and why."

**Sample log output:**
```
2026-03-25 21:12:04 [INFO] PIPELINE STARTED
2026-03-25 21:12:07 [INFO] SUCCESS: invoice.pdf → json_output/invoice.json
2026-03-25 21:12:07 [INFO] DB saved: invoice.pdf
2026-03-25 21:12:07 [INFO] Vector stored: invoice.pdf
2026-03-25 21:12:08 [WARNING] SKIPPED (duplicate file): invoice_copy.pdf
2026-03-25 21:12:08 [INFO] PIPELINE COMPLETE — 4 total, 3 success, 1 duplicate
```

---

### SKILL 13: Docker — Containerization
**Where used:** `Dockerfile`

**What it does:**
- Packages the entire application with all dependencies into a container
- Includes Python, Tesseract, Poppler, and all pip packages
- Container runs identically on any machine — no "works on my machine" problem
- Based on python:3.11-slim for a lightweight image

**How to explain in interview:**
> "I wrote a Dockerfile to containerize the pipeline. The container installs
> Tesseract and Poppler at the OS level, then installs all Python packages
> from requirements.txt. This means anyone can run the pipeline with just
> docker build and docker run — no manual setup required. In production,
> this container could run on any cloud provider or Kubernetes cluster."

**Docker commands:**
```bash
# Build the image
docker build -t document-pipeline .

# Run the pipeline
docker run -v $(pwd)/input_docs:/app/input_docs document-pipeline
```

---

### SKILL 14: Virtual Environment — venv
**Where used:** Project setup

**What it does:**
- Isolated Python environment for this project
- Prevents package conflicts with other Python projects on the same machine
- requirements.txt records exact package versions for reproducibility

**How to explain in interview:**
> "I used a virtual environment to isolate project dependencies. This is
> standard practice — it ensures reproducibility and prevents version
> conflicts. The requirements.txt file pins exact versions so anyone
> can recreate the exact same environment."

---

### SKILL 15: ETL Pipeline Design — run_pipeline.py
**Where used:** `scripts/run_pipeline.py`

**What it does:**
- Orchestrates all pipeline steps in the correct order
- Single entry point: run one script, processes everything
- Handles errors gracefully — one file failing doesn't stop the pipeline
- Tracks stats: total, success, failed, duplicate, skipped
- Calls: detect → extract → clean → fields → validate → deduplicate → JSON → DB → vector

**How to explain in interview:**
> "run_pipeline.py is the orchestrator — it ties all components together
> in a proper ETL pattern. Extract: read files and get text. Transform:
> clean, extract fields, validate. Load: save to JSON, PostgreSQL, and
> ChromaDB. Each step is isolated so failures are contained. This is the
> same pattern used in production pipelines, just without a cloud scheduler
> like Airflow on top."

---

## 4. SCRIPT-BY-SCRIPT EXPLANATION

| Script | Purpose | Key Library |
|---|---|---|
| detect_files.py | Identify file type (text PDF / scanned PDF / image) | pypdf, pathlib |
| extract_pdf_text.py | Extract text from text-based PDFs | pypdf |
| ocr_extract.py | Extract text from images and scanned PDFs | pytesseract, pdf2image, Pillow |
| clean_text.py | Normalize and clean raw extracted text | re (regex) |
| extract_fields.py | Find specific fields using pattern matching | re (regex) |
| to_json.py | Validate data and save as JSON | pydantic, json |
| deduplicate.py | Detect and skip duplicate files | hashlib |
| database.py | Save records to PostgreSQL | psycopg2 |
| vector_store.py | Store and search documents in ChromaDB | chromadb |
| run_pipeline.py | Master script — runs all steps in order | logging, all above |

---

## 5. HOW TO DEMO (STEP BY STEP)

### Before the Demo
1. Activate venv: `venv\Scripts\activate`
2. Make sure PostgreSQL is running
3. Clear previous outputs for a fresh demo:
```powershell
del logs\seen_hashes.json
del json_output\*.json
```

---

### Demo Script (10 minutes)

**STEP 1 — Introduce the project (1 min)**

Say:
> "I built a local document processing ETL pipeline. It takes raw documents —
> PDFs and scanned images — and converts them into structured data stored in
> PostgreSQL and ChromaDB. Let me show you end to end."

Open the project folder in VS Code. Show the folder structure.

---

**STEP 2 — Show the input files (30 sec)**

Open input_docs/ folder. Say:
> "These are the raw inputs — three WhatsApp photos of payment receipts and
> one text-based PDF invoice. The pipeline handles both automatically."

---

**STEP 3 — Run the pipeline live (3 mins)**

```powershell
python scripts/run_pipeline.py
```

Walk through the output line by line:
- "Here it scans the folder and detects file types"
- "Here it runs OCR on the JPEG images using Tesseract"
- "Here it extracts text from the PDF using pypdf"
- "Here it cleans the text and extracts fields"
- "Here Pydantic validates the data schema"
- "Here it saves JSON output"
- "Here it saves to PostgreSQL"
- "Here it stores vectors in ChromaDB"

---

**STEP 4 — Show JSON output (1 min)**

```powershell
cat "json_output/WhatsApp Image 2026-03-23 at 10.11.06 PM.json"
```

Say:
> "This is the structured output — vendor name, receipt number, date, amount —
> all automatically extracted from a phone photo of a receipt."

---

**STEP 5 — Show PostgreSQL (2 mins)**

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT vendor_name, receipt_number, amount_paid, date_paid FROM receipts;"
```

Then show a real query:
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT vendor_name, SUM(amount_paid) as total_spent FROM receipts GROUP BY vendor_name;"
```

Say:
> "All data is in PostgreSQL. I can run any SQL query — total spend per vendor,
> receipts in a date range, anything."

---

**STEP 6 — Show ChromaDB semantic search (2 mins)**

```powershell
python scripts/vector_store.py
```

Say:
> "ChromaDB stores documents as vector embeddings. I can search by meaning —
> watch: I search 'software training payment' and it finds the right receipts
> even though those exact words don't appear together in the document.
> This is semantic search, the foundation of RAG systems."

---

**STEP 7 — Show deduplication (30 sec)**

Run pipeline again:
```powershell
python scripts/run_pipeline.py
```

Say:
> "If I run it again on the same files, the pipeline detects all 4 as duplicates
> using MD5 file hashing and skips them. Zero reprocessing, zero duplicate records."

---

**STEP 8 — Show logs (30 sec)**

```powershell
cat logs/pipeline.log
```

Say:
> "Every run is fully logged with timestamps — which files succeeded, which
> were duplicates, any validation errors. Full observability."

---

## 6. INTERVIEW QUESTIONS & ANSWERS

**Q: Why did you use regex instead of an LLM for field extraction?**

A: "Rule-based regex is faster, cheaper, and fully explainable. For structured
documents like invoices and receipts, fields appear in predictable patterns.
Regex is deterministic — same input always gives same output. LLMs add API cost,
latency, and unpredictability for a task that doesn't need them. I can always
layer LLM extraction on top for edge cases."

---

**Q: How does your deduplication work?**

A: "Two layers. First, I compute an MD5 hash of the file's binary content.
Same file content always produces the same hash, regardless of filename.
Hashes are stored in a JSON file after first processing. On subsequent runs,
if the hash exists, the file is skipped. Second layer compares key fields like
receipt number and amount to catch renamed copies of the same document."

---

**Q: Why PostgreSQL and ChromaDB — why both?**

A: "They serve different purposes. PostgreSQL is for structured queries —
give me all receipts from vendor X, or total spend this month. ChromaDB is
for semantic search — find documents similar to this description. Together
they cover both exact and fuzzy retrieval patterns, which is common in modern
data platforms."

---

**Q: What is ChromaDB and why did you use it?**

A: "ChromaDB is a vector database. It converts text into mathematical
embeddings — numerical representations of meaning. Similar concepts have
similar vectors. This enables semantic search: find documents by meaning
rather than exact keywords. It's the storage layer in RAG (Retrieval
Augmented Generation) architectures, which is increasingly required in
AI data platform roles."

---

**Q: How would you scale this to production?**

A: "Several ways. Replace the local file watcher with an S3 event trigger
or Kafka topic for input. Replace local PostgreSQL with RDS or Cloud SQL.
Replace local ChromaDB with a managed vector DB like Pinecone or Weaviate.
Add Airflow or Prefect for scheduling and retry logic. Containerize with
Docker (already done) and deploy on Kubernetes or ECS. The pipeline logic
stays the same — only the infrastructure changes."

---

**Q: What would you improve?**

A: "Three things. First, add LLM-based extraction as a fallback for documents
where regex fails. Second, add a REST API using FastAPI so external systems
can submit documents programmatically. Third, add data quality metrics —
track field extraction success rate per document type to identify where
regex patterns need improvement."

---

**Q: How does Pydantic help here?**

A: "Pydantic enforces a schema at runtime. Before any data reaches the database,
it must match the defined model — correct types, valid values. If OCR reads
a garbled amount like 'hello' instead of a float, Pydantic raises a validation
error immediately. This prevents silent data corruption, which is a serious
problem in production pipelines where bad data can propagate for days before
anyone notices."

---

## 7. JD KEYWORD MAPPING

| JD Requirement | Where in Your Project |
|---|---|
| ETL pipeline | run_pipeline.py orchestrates end-to-end ETL |
| Unstructured data processing | OCR extracts text from images and scanned PDFs |
| Schema validation | Pydantic validates every record before saving |
| Data deduplication | MD5 hashing + field-level comparison |
| PostgreSQL | database.py — receipts and invoices tables |
| Vector database / ChromaDB | vector_store.py — semantic search |
| Python | All scripts — pytesseract, pypdf, pydantic, psycopg2 |
| Docker / containerization | Dockerfile with Tesseract + Poppler |
| Logging / observability | Python logging — pipeline.log with full audit trail |
| Data quality | Validation errors logged, bad records rejected |
| Regex / pattern matching | extract_fields.py — rule-based field extraction |
| JSON output | to_json.py — structured JSON per document |

---

## PROJECT FOLDER STRUCTURE

```
document-pipeline-local/
├── input_docs/          ← raw PDF and image files go here
├── raw_text/            ← extracted text (before cleaning)
├── clean_text/          ← cleaned normalized text
├── json_output/         ← final structured JSON output
├── chroma_db/           ← ChromaDB vector storage
├── logs/
│   ├── pipeline.log     ← full audit log
│   └── seen_hashes.json ← deduplication registry
├── scripts/
│   ├── detect_files.py
│   ├── extract_pdf_text.py
│   ├── ocr_extract.py
│   ├── clean_text.py
│   ├── extract_fields.py
│   ├── to_json.py
│   ├── deduplicate.py
│   ├── database.py
│   ├── vector_store.py
│   └── run_pipeline.py  ← MASTER SCRIPT — run this
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## QUICK REFERENCE — COMMANDS TO REMEMBER

```powershell
# Activate environment
venv\Scripts\activate

# Run full pipeline
python scripts/run_pipeline.py

# Test ChromaDB search
python scripts/vector_store.py

# Query PostgreSQL
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT * FROM receipts;"

# View logs
cat logs/pipeline.log

# Reset and run fresh
del logs\seen_hashes.json
del json_output\*.json
python scripts/run_pipeline.py
```

---

*Built with: Python 3.13 | pytesseract | pypdf | pdf2image | Pydantic | PostgreSQL | ChromaDB | Docker*
