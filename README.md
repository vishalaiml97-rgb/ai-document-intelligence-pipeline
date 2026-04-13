# Local Document Processing Pipeline

A local ETL pipeline that extracts structured data from PDFs and scanned images using OCR, validates it with Pydantic, stores results in PostgreSQL, and enables semantic search via ChromaDB.

---

## What It Does

- Detects file type (text PDF, scanned PDF, image)
- Extracts text using `pypdf` (text PDFs) or `Tesseract OCR` (scanned PDFs/images)
- Cleans and normalizes extracted text
- Extracts key fields (vendor, amount, date, receipt/invoice number) using regex
- Validates data using Pydantic schemas
- Deduplicates using file hashing + field comparison
- Saves structured output as JSON
- Stores results in PostgreSQL database
- Stores document embeddings in ChromaDB for semantic search
- Logs every step to `logs/pipeline.log`

---

## Project Structure

```
document-pipeline-local/
├── input_docs/         ← Drop PDFs and images here
├── raw_text/           ← Extracted raw text (auto-generated)
├── clean_text/         ← Cleaned text (auto-generated)
├── json_output/        ← Structured JSON output (auto-generated)
├── logs/               ← Pipeline logs (auto-generated)
├── chroma_db/          ← ChromaDB vector store (auto-generated)
├── scripts/
│   ├── detect_files.py       ← Detect file type
│   ├── extract_pdf_text.py   ← Extract text from text PDFs
│   ├── ocr_extract.py        ← OCR for scanned PDFs and images
│   ├── clean_text.py         ← Normalize extracted text
│   ├── extract_fields.py     ← Regex-based field extraction
│   ├── to_json.py            ← Pydantic validation + JSON output
│   ├── deduplicate.py        ← File hash + field deduplication
│   ├── database.py           ← PostgreSQL integration
│   ├── vector_store.py       ← ChromaDB vector storage + search
│   └── run_pipeline.py       ← Master pipeline script
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Setup

### 1. Prerequisites

- Python 3.11
- Tesseract OCR — [Download](https://github.com/UB-Mannheim/tesseract/wiki)
- Poppler — [Download](https://github.com/oschwartz10612/poppler-windows/releases)
- PostgreSQL 17 — [Download](https://www.postgresql.org/download/windows/)

### 2. Clone and Install

```bash
git clone <your-repo-url>
cd document-pipeline-local
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Setup PostgreSQL

```sql
CREATE DATABASE pipeline_db;
```

### 4. Add Documents

Drop PDF or image files into `input_docs/`

### 5. Run Pipeline

```bash
python scripts/run_pipeline.py
```

---

## Run with Docker

```bash
docker-compose up --build
```

---

## Output Example

**JSON Output (`json_output/receipt.json`):**
```json
{
    "file_name": "receipt.txt",
    "document_type": "receipt",
    "vendor_name": "AURBORBLOOM LLC",
    "receipt_number": "1148-2760",
    "date_paid": "Feb 27, 2026",
    "amount_paid": 130.0,
    "item_description": "Full Stack Software Testing"
}
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| pypdf | Text PDF extraction |
| Tesseract + pytesseract | OCR for scanned docs |
| pdf2image + Poppler | PDF to image conversion |
| Pydantic | Data validation |
| PostgreSQL + psycopg2 | Structured data storage |
| ChromaDB | Vector storage + semantic search |
| pandas | Data handling |
| Docker | Containerization |

---

## Key Features for Data Engineering

- **ETL Pipeline** — Extract, Transform, Load end to end
- **Schema Validation** — Pydantic models with type enforcement
- **Deduplication** — MD5 file hashing + field-level comparison
- **Vector Search** — ChromaDB semantic similarity search
- **Logging** — Structured logs for every pipeline run
- **Containerized** — Docker + docker-compose ready
