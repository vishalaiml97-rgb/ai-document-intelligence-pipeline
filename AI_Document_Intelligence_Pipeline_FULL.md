# AI Document Intelligence Pipeline


**Author:** Vishal S
**Contact:** vishalaiml97@gmail.com


---

# TABLE OF CONTENTS

1. Executive Summary
2. Problem Statement
3. System Architecture
4. Complete Technology Stack
5. Skill 1 — Python (Core Language)
6. Skill 2 — OCR with Tesseract + pytesseract
7. Skill 3 — PDF Text Extraction with pypdf
8. Skill 4 — Image Conversion with pdf2image + Poppler
9. Skill 5 — Image Processing with Pillow
10. Skill 6 — Text Cleaning with Regex
11. Skill 7 — Field Extraction (Rule-Based NLP)
12. Skill 8 — Schema Validation with Pydantic
13. Skill 9 — Deduplication with MD5 Hashing
14. Skill 10 — JSON Serialization
15. Skill 11 — PostgreSQL Relational Database
16. Skill 12 — ChromaDB Vector Database
17. Skill 13 — Sentence Transformers (Embeddings)
18. Skill 14 — Pipeline Orchestration
19. Skill 15 — Logging and Observability
20. Skill 16 — Docker Containerization
21. Skill 17 — Virtual Environment and Dependency Management
22. Script-by-Script Code Walkthrough
23. Data Flow — End to End
24. Sample Outputs
25. Project Demo Guide
26. Future Roadmap

---

# 1. EXECUTIVE SUMMARY

The AI Document Intelligence Pipeline is a production-grade, fully automated
local ETL system that transforms raw, unstructured documents — scanned images,
photo receipts, and PDF invoices — into validated, structured, model-ready data.

The pipeline is designed to mirror the exact data infrastructure requirements
found in AI/ML platform engineering roles:

- Ingests raw documents from a watched folder
- Detects file type and routes to appropriate extraction method
- Extracts text using direct PDF reading or Tesseract OCR
- Cleans and normalizes extracted text
- Applies intelligent rule-based field extraction
- Validates every record against strict Pydantic schemas
- Deduplicates using MD5 file hashing across runs
- Saves structured output as JSON
- Persists records in PostgreSQL for relational querying
- Stores document vectors in ChromaDB for semantic search and RAG
- Logs every event with timestamps for full observability
- Containerized with Docker for portable deployment

This is not a toy project. Every component reflects real production patterns
used in AI data platforms at scale.

---

# 2. PROBLEM STATEMENT

## The Challenge
Organizations handling large volumes of invoices, receipts, and scanned
documents face a critical data problem: valuable information is locked inside
unstructured files. These files cannot be directly queried, aggregated,
or used to train machine learning models without transformation.

## Manual Process Problems
- Manually reading and entering data is slow and error-prone
- No validation — bad data silently enters databases
- No deduplication — same document processed multiple times
- No audit trail — impossible to debug failures
- Not scalable — falls apart at volume

## What This Pipeline Solves

| Problem | Solution |
|---|---|
| Text locked in images/scans | Tesseract OCR extracts it automatically |
| Messy, inconsistent text | Cleaning step normalizes everything |
| Fields hard to find | Regex patterns extract structured fields |
| Bad data reaches database | Pydantic rejects invalid records |
| Duplicate documents processed | MD5 hashing detects and skips duplicates |
| No audit trail | Logging records every event |
| Can't search by meaning | ChromaDB enables semantic search |
| Hard to deploy | Docker containerizes everything |

---

# 3. SYSTEM ARCHITECTURE

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
│                       input_docs/                                │
│         invoice.pdf    receipt.jpeg    scan.pdf                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DETECTION LAYER                              │
│                    detect_files.py                               │
│   Reads file extension + attempts pypdf extraction               │
│   Text PDF → pypdf path                                          │
│   Scanned PDF / Image → OCR path                                 │
└──────────┬───────────────────────────────┬──────────────────────┘
           │                               │
           ▼                               ▼
┌──────────────────┐             ┌──────────────────────────────┐
│ Text PDF Path    │             │ OCR Path                     │
│                  │             │                              │
│ extract_pdf_     │             │ pdf2image converts PDF       │
│ text.py          │             │ pages to images              │
│ (pypdf)          │             │                              │
│                  │             │ pytesseract runs OCR         │
│                  │             │ on each image                │
└────────┬─────────┘             └──────────────┬───────────────┘
         │                                      │
         └──────────────┬───────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TRANSFORMATION LAYER                           │
│                                                                  │
│  clean_text.py      → remove noise, normalize whitespace         │
│  extract_fields.py  → regex patterns pull structured fields      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                              │
│                  Pydantic Schema Check                           │
│                                                                  │
│   PASS → continue pipeline                                       │
│   FAIL → log error, reject record, skip to next file            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DEDUPLICATION LAYER                             │
│                   deduplicate.py                                 │
│                                                                  │
│   NEW FILE  → continue pipeline                                  │
│   DUPLICATE → log warning, skip file                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LOAD LAYER                                 │
│                                                                  │
│   to_json.py       → json_output/filename.json                   │
│   database.py      → PostgreSQL pipeline_db                      │
│   vector_store.py  → ChromaDB semantic index                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OBSERVABILITY LAYER                             │
│                   logs/pipeline.log                              │
│   Timestamps | File names | Status | Errors | Summary           │
└─────────────────────────────────────────────────────────────────┘
```

---

# 4. COMPLETE TECHNOLOGY STACK

| Category | Tool / Library | Version | Role |
|---|---|---|---|
| Language | Python | 3.13 | Core logic |
| OCR Engine | Tesseract | 5.5.0 | Image text recognition |
| OCR Python Wrapper | pytesseract | 0.3.13 | Calls Tesseract from Python |
| PDF Text Extraction | pypdf | 6.9.2 | Read text-based PDFs |
| PDF to Image | pdf2image | 1.17.0 | Convert scanned PDF pages |
| PDF Renderer | Poppler | 24.08.0 | Backend for pdf2image |
| Image Processing | Pillow | 12.1.1 | Open and handle image files |
| Data Validation | Pydantic | 2.12.5 | Schema enforcement |
| Hashing | hashlib | built-in | MD5 deduplication |
| Relational DB | PostgreSQL | 17.9 | Structured data storage |
| DB Connector | psycopg2-binary | 2.9.11 | Python-PostgreSQL bridge |
| Vector DB | ChromaDB | 1.5.5 | Semantic search storage |
| Embeddings | all-MiniLM-L6-v2 | via chromadb | Document vectorization |
| Containerization | Docker | latest | Portable deployment |
| Logging | logging | built-in | Observability |
| Data Analysis | pandas | 3.0.1 | Tabular operations |

---

# 5. SKILL 1 — PYTHON (CORE LANGUAGE)

## What It Is
Python is the primary programming language for the entire pipeline.
Every script, every function, every connection is written in Python.

## Why Python
- Richest ecosystem for data engineering, OCR, and ML tooling
- Native support for file I/O, regex, JSON, logging
- First-class support from all major databases and vector stores
- Used by the vast majority of AI/ML data platforms in production

## How It Is Used In This Project

### File System Operations
```python
from pathlib import Path
import os

# Define all folder paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input_docs"
RAW_TEXT_DIR = BASE_DIR / "raw_text"
CLEAN_TEXT_DIR = BASE_DIR / "clean_text"
JSON_OUTPUT_DIR = BASE_DIR / "json_output"
LOG_DIR = BASE_DIR / "logs"

# Create folders if they don't exist
for folder in [RAW_TEXT_DIR, CLEAN_TEXT_DIR, JSON_OUTPUT_DIR, LOG_DIR]:
    folder.mkdir(exist_ok=True)
```

**Why pathlib instead of os.path:**
pathlib gives object-oriented path manipulation. `BASE_DIR / "input_docs"`
is cleaner and cross-platform compared to `os.path.join(BASE_DIR, "input_docs")`.

### Exception Handling
```python
try:
    text = extract_text_from_pdf(file_path)
except Exception as e:
    logger.error(f"FAILED: {file_path.name} — {e}")
    stats["failed"] += 1
    continue  # don't stop the whole pipeline for one bad file
```

**Why this matters:** In production pipelines, one bad file should never
crash the entire run. Each file is isolated in a try/except block.

### Dictionary and JSON Handling
```python
import json

fields = {
    "file_name": file_name,
    "vendor_name": vendor,
    "amount_paid": 150.0,
    "date_paid": "Mar 17, 2026"
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(fields, f, indent=4, default=str)
```

---

# 6. SKILL 2 — OCR WITH TESSERACT + PYTESSERACT

## What It Is
Tesseract is an open-source OCR (Optical Character Recognition) engine
originally developed by HP and now maintained by Google.
pytesseract is a Python wrapper that allows calling Tesseract from Python code.

## Why It Is Used
Scanned PDFs and phone photos of receipts contain text as pixels — not as
readable characters. A regular PDF reader sees nothing in these files.
Tesseract looks at the image and recognizes the text character by character,
converting pixels into a readable string.

## The Problem It Solves
```
WhatsApp photo of a receipt
         ↓
Just pixels — no readable text
         ↓
Tesseract OCR reads the pixels
         ↓
"Receipt from AURBORBLOOM LLC
 Amount paid $150.00
 Mar 17, 2026"
```

## How It Is Used — Full Code

```python
# scripts/ocr_extract.py

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path

# Tell pytesseract exactly where tesseract.exe lives
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_image_file(image_path: Path, output_dir: Path) -> str:
    """
    Run OCR on a single image file (JPG, PNG, etc.)
    Returns the extracted text string.
    """
    # Open the image using Pillow
    image = Image.open(image_path)

    # Run Tesseract OCR on the image
    # lang="eng" tells Tesseract to use English language data
    text = pytesseract.image_to_string(image, lang="eng")

    # Save raw text output
    output_path = output_dir / (image_path.stem + ".txt")
    output_path.write_text(text, encoding="utf-8")

    return text


def ocr_scanned_pdf(pdf_path: Path, output_dir: Path) -> str:
    """
    Run OCR on a scanned PDF.
    Steps: PDF pages → images → OCR each image → combine text
    """
    # Convert each PDF page to a PIL Image object
    # dpi=300 gives higher resolution = better OCR accuracy
    pages = convert_from_path(str(pdf_path), dpi=300)

    full_text = ""
    for i, page_image in enumerate(pages):
        # Run OCR on each page image
        page_text = pytesseract.image_to_string(page_image, lang="eng")
        full_text += f"\n--- Page {i+1} ---\n{page_text}"

    # Save combined text
    output_path = output_dir / (pdf_path.stem + ".txt")
    output_path.write_text(full_text, encoding="utf-8")

    return full_text
```

## Key Parameters Explained

| Parameter | Value | Why |
|---|---|---|
| `lang="eng"` | English | Tells Tesseract which language model to use |
| `dpi=300` | 300 DPI | Higher resolution = better character recognition |
| `tesseract_cmd` | Full path | Windows needs explicit path to tesseract.exe |

## OCR Quality Considerations
- Higher DPI = better accuracy but slower processing
- Dark, clear images = best results
- Blurry or low-contrast images = lower accuracy
- Noise in OCR output is handled by the cleaning step

---

# 7. SKILL 3 — PDF TEXT EXTRACTION WITH pypdf

## What It Is
pypdf is a Python library that reads text directly from text-based PDF files.
Text-based PDFs have actual text embedded in them (like a Word document saved
as PDF). The text is selectable in a PDF reader.

## Why It Is Used
pypdf is faster and more accurate than OCR for text-based PDFs because
it reads the embedded text directly without image processing.

## How to Tell Which Type of PDF You Have
- Open the PDF → try to select text with your mouse
- Can select text → text-based PDF → use pypdf
- Cannot select text → scanned PDF → use OCR

## How It Is Used — Full Code

```python
# scripts/extract_pdf_text.py

from pypdf import PdfReader
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path, output_dir: Path) -> str:
    """
    Extract embedded text from a text-based PDF.
    Loops through each page and concatenates the text.
    """
    reader = PdfReader(str(pdf_path))
    full_text = ""

    for i, page in enumerate(reader.pages):
        # extract_text() returns the text on this page as a string
        page_text = page.extract_text()

        if page_text:
            full_text += f"\n--- Page {i+1} ---\n{page_text}"

    # If no text extracted, the PDF is probably scanned
    if not full_text.strip():
        return ""  # caller will route to OCR instead

    # Save to raw_text/ folder
    output_path = output_dir / (pdf_path.stem + ".txt")
    output_path.write_text(full_text, encoding="utf-8")

    return full_text
```

## Why Check if Text is Empty
If pypdf returns empty text, it means the PDF is scanned.
The pipeline uses this as the signal to re-route to the OCR path:

```python
text = extract_text_from_pdf(file_path, raw_text_dir)
if not text.strip():
    # Fall back to OCR
    text = ocr_scanned_pdf(file_path, raw_text_dir)
```

---

# 8. SKILL 4 — IMAGE CONVERSION WITH pdf2image + POPPLER

## What It Is
pdf2image is a Python library that converts PDF pages into PIL Image objects.
Poppler is the underlying PDF rendering engine that pdf2image depends on.

## Why It Is Needed
Tesseract OCR only reads image data — it cannot process PDF files directly.
For scanned PDFs, each page must be converted to an image first, then OCR runs
on each image.

## The Dependency Chain
```
pdf2image (Python library)
      ↓ calls
Poppler (system-level PDF renderer, installed separately)
      ↓ renders
PDF page as image
      ↓ passed to
pytesseract → Tesseract OCR
```

## How It Is Used — Full Code

```python
from pdf2image import convert_from_path

def convert_pdf_to_images(pdf_path, dpi=300):
    """
    Convert all pages of a PDF to PIL Image objects.
    Returns a list of images, one per page.
    """
    pages = convert_from_path(
        str(pdf_path),
        dpi=300,           # resolution — higher = better OCR
        fmt="jpeg",        # image format
        thread_count=2     # use 2 threads for faster conversion
    )
    return pages
    # pages[0] = first page image
    # pages[1] = second page image, etc.
```

## Why DPI Matters
- 150 DPI: Fast but may miss small text
- 300 DPI: Balanced — good accuracy, reasonable speed (used in this project)
- 600 DPI: Maximum accuracy, much slower, large memory usage

---

# 9. SKILL 5 — IMAGE PROCESSING WITH PILLOW

## What It Is
Pillow (PIL — Python Imaging Library) is Python's standard image processing
library. It handles opening, converting, and manipulating image files.

## Why It Is Used
pytesseract requires images in PIL Image format. Pillow opens JPG, PNG, TIFF,
BMP, and other formats and converts them into the format pytesseract expects.

## How It Is Used — Full Code

```python
from PIL import Image

def process_image_file(image_path):
    """
    Open an image file and prepare it for OCR.
    """
    # Open the image — works with JPG, PNG, TIFF, BMP, etc.
    image = Image.open(image_path)

    # Convert to RGB if needed (some images are RGBA or grayscale)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Pass directly to pytesseract
    text = pytesseract.image_to_string(image, lang="eng")
    return text
```

## Image Mode Conversion
- RGBA (PNG with transparency) must be converted to RGB
- Grayscale images work fine but RGB is safest
- Tesseract handles grayscale internally anyway

---

# 10. SKILL 6 — TEXT CLEANING WITH REGEX

## What It Is
Regex (Regular Expressions) is a pattern-matching language built into Python.
The `re` module provides regex functions — no installation needed.

## Why Text Cleaning Is Critical
Raw OCR output is always noisy. Even good OCR produces:
- Double and triple spaces
- Random junk characters (©, ™, @@@, ===)
- Broken line endings
- Non-printable characters (control characters, null bytes)
- Lines with only symbols and no real content

If we run field extraction on noisy text, the regex patterns fail.
Cleaning normalizes the text so extraction works reliably.

## Before and After Cleaning

**Before:**
```
© Hous

= See order for more details

Is this correct? 1 1)

'sive AURBORBLOOM LLC  &  10:54 pm  @ &
Receipt  from  AURBORBLOOM  LLC

seipt  #1055-6311

AMOUNT   PAID    DATE PAID    PAYMENT METHOD
$150.00   Mar  17, 2026,  12:23:25 PM    visa - 5810
```

**After:**
```
AURBORBLOOM LLC 10:54 pm
Receipt from AURBORBLOOM LLC
seipt #1055-6311
AMOUNT PAID DATE PAID PAYMENT METHOD
$150.00 Mar 17, 2026, 12:23:25 PM visa - 5810
```

## How It Is Used — Full Code

```python
# scripts/clean_text.py

import re

def clean_text(text: str) -> str:
    """
    Clean and normalize raw OCR-extracted text.
    Applied before field extraction.
    """

    # Step 1: Replace tab characters with a space
    text = text.replace("\t", " ")

    # Step 2: Remove non-printable/junk characters
    # Keep only printable ASCII (0x20 to 0x7E) and newlines
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)

    # Step 3: Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)

    # Step 4: Process line by line
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Step 5: Keep only lines that have real content
        # (at least one letter or number)
        if stripped and re.search(r"[a-zA-Z0-9]", stripped):
            cleaned_lines.append(stripped)

    # Step 6: Join lines, collapse multiple blank lines
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()
```

## Regex Patterns Explained

| Pattern | What it matches | Why |
|---|---|---|
| `[^\x20-\x7E\n]` | Any non-printable character | Remove OCR noise |
| `" {2,}"` | Two or more spaces | Normalize whitespace |
| `[a-zA-Z0-9]` | Any letter or digit | Keep only meaningful lines |
| `\n{3,}` | Three or more newlines | Limit blank lines to max 2 |

---

# 11. SKILL 7 — FIELD EXTRACTION (RULE-BASED NLP)

## What It Is
Field extraction uses regex patterns to find specific pieces of information
inside unstructured text. This is a form of rule-based Named Entity Recognition
(NER) — a classic NLP technique.

## Why Rule-Based Instead of LLM
- Deterministic: same input always gives same output
- No API cost, no latency, no internet required
- Fully explainable — you can see exactly why a field was or wasn't found
- For structured documents (invoices, receipts), patterns are predictable
- LLM can be added as a fallback for edge cases later

## Document Types Supported
1. **Receipts** — from AURBORBLOOM LLC (WhatsApp photo receipts)
2. **Invoices** — text-based PDF invoices

## How It Is Used — Full Code

```python
# scripts/extract_fields.py

import re
from pathlib import Path

def extract_receipt_fields(text: str, file_name: str) -> dict:
    """
    Extract structured fields from a receipt document.
    """
    fields = {
        "file_name": file_name,
        "document_type": "receipt",
        "vendor_name": None,
        "receipt_number": None,
        "date_paid": None,
        "amount_paid": None,
        "item_description": None
    }

    # --- VENDOR NAME ---
    # Look for "Receipt from VENDOR NAME" pattern
    vendor_match = re.search(
        r"Receipt from ([A-Z][A-Z\s&]+(?:LLC|INC|CORP|LTD)?)",
        text, re.IGNORECASE
    )
    if vendor_match:
        fields["vendor_name"] = vendor_match.group(1).strip()

    # --- RECEIPT NUMBER ---
    # Look for #XXXX-XXXX pattern (with or without "Receipt" before it)
    receipt_match = re.search(
        r"(?:Receipt\s*)?#([\d]{4}-[\d]{4})",
        text, re.IGNORECASE
    )
    if receipt_match:
        fields["receipt_number"] = receipt_match.group(1).strip()

    # --- DATE PAID ---
    # Look for Month DD, YYYY pattern (e.g., Mar 17, 2026)
    date_match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*"
        r"\s+\d{1,2},\s+\d{4}",
        text, re.IGNORECASE
    )
    if date_match:
        fields["date_paid"] = date_match.group(0).strip()

    # --- AMOUNT PAID ---
    # Look for "Amount paid $XXX.XX" pattern
    amount_match = re.search(
        r"Amount paid\s+\$?([\d,]+\.\d{2})",
        text, re.IGNORECASE
    )
    if amount_match:
        amount_str = amount_match.group(1).replace(",", "")
        fields["amount_paid"] = float(amount_str)

    # --- ITEM DESCRIPTION ---
    # Look for text between SUMMARY and "x 1"
    item_match = re.search(
        r"SUMMARY\s*\n([^\n]+?)(?:\s*x\s*\d+)?$",
        text, re.IGNORECASE | re.MULTILINE
    )
    if item_match:
        fields["item_description"] = item_match.group(1).strip()

    return fields


def extract_invoice_fields(text: str, file_name: str) -> dict:
    """
    Extract structured fields from an invoice document.
    """
    fields = {
        "file_name": file_name,
        "document_type": "invoice",
        "vendor_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_amount": None
    }

    # --- VENDOR NAME ---
    # Look for "From:\nVENDOR NAME" pattern
    vendor_match = re.search(
        r"From:\s*\n([^\n]+)",
        text, re.IGNORECASE
    )
    if vendor_match:
        fields["vendor_name"] = vendor_match.group(1).strip()

    # --- INVOICE NUMBER ---
    # Look for "Invoice Number INV-XXXX" pattern
    inv_match = re.search(
        r"Invoice\s*Number\s+([A-Z]{2,5}-\d+)",
        text, re.IGNORECASE
    )
    if inv_match:
        fields["invoice_number"] = inv_match.group(1).strip()

    # --- INVOICE DATE ---
    date_match = re.search(
        r"Invoice\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4})",
        text, re.IGNORECASE
    )
    if date_match:
        fields["invoice_date"] = date_match.group(1).strip()

    # --- DUE DATE ---
    due_match = re.search(
        r"Due\s*Date\s+([A-Za-z]+ \d{1,2},? \d{4})",
        text, re.IGNORECASE
    )
    if due_match:
        fields["due_date"] = due_match.group(1).strip()

    # --- TOTAL AMOUNT ---
    total_match = re.search(
        r"(?:Total|Grand Total|Amount Due)\s+\$?([\d,]+\.\d{2})",
        text, re.IGNORECASE
    )
    if total_match:
        fields["total_amount"] = float(
            total_match.group(1).replace(",", "")
        )

    return fields
```

## Regex Pattern Breakdown

| Field | Pattern | Explanation |
|---|---|---|
| Vendor | `Receipt from ([A-Z][A-Z\s&]+LLC)` | Capture company name after "Receipt from" |
| Receipt # | `#([\d]{4}-[\d]{4})` | Capture XXXX-XXXX format after # |
| Date | `(Jan\|Feb\|...)\\s+\\d{1,2},\\s+\\d{4}` | Month Day, Year format |
| Amount | `Amount paid\\s+\\$?([\\d,]+\\.\\d{2})` | Dollar amount after "Amount paid" |
| Invoice # | `Invoice\\s*Number\\s+([A-Z]{2,5}-\\d+)` | INV-3337 style numbers |

---

# 12. SKILL 8 — SCHEMA VALIDATION WITH PYDANTIC

## What It Is
Pydantic is a Python data validation library that enforces data schemas at
runtime. You define a model class with typed fields, and Pydantic checks every
piece of data against that schema before it is used.

## Why Pydantic Is Critical
In production data pipelines, bad data is a silent killer. Without validation:
- A garbled amount ("hello" instead of 150.00) gets inserted as NULL
- An invalid date crashes a downstream ML training job hours later
- No one knows which file caused the problem

With Pydantic:
- Every record is checked before it touches any database
- Type mismatches raise clear errors with field names
- Bad records are logged and rejected immediately
- The database stays clean

## How It Is Used — Full Code

```python
# Inside scripts/to_json.py

from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional
from datetime import datetime

class ReceiptSchema(BaseModel):
    """
    Schema for receipt documents.
    Every receipt must match this structure before being saved.
    """
    file_name: str                   # must be a string
    document_type: str               # must be a string
    vendor_name: Optional[str]       # can be None if not found
    receipt_number: Optional[str]    # can be None if not found
    date_paid: Optional[str]         # can be None if not found
    amount_paid: Optional[float]     # must be float if present
    item_description: Optional[str]  # can be None

    @field_validator("amount_paid")
    @classmethod
    def amount_must_be_positive(cls, v):
        """
        Custom validation: amount cannot be negative or zero.
        """
        if v is not None and v <= 0:
            raise ValueError(f"amount_paid must be positive, got {v}")
        return v

    @field_validator("file_name")
    @classmethod
    def file_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("file_name cannot be empty")
        return v


class InvoiceSchema(BaseModel):
    """
    Schema for invoice documents.
    """
    file_name: str
    document_type: str
    vendor_name: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    due_date: Optional[str]
    total_amount: Optional[float]

    @field_validator("total_amount")
    @classmethod
    def total_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError(f"total_amount must be positive, got {v}")
        return v


def validate_and_save(fields: dict, output_dir: Path) -> bool:
    """
    Validate extracted fields against schema.
    Save to JSON if valid. Log error if invalid.
    Returns True if saved, False if validation failed.
    """
    doc_type = fields.get("document_type", "unknown")

    try:
        if doc_type == "receipt":
            validated = ReceiptSchema(**fields)
        elif doc_type == "invoice":
            validated = InvoiceSchema(**fields)
        else:
            raise ValueError(f"Unknown document type: {doc_type}")

        # Save validated data as JSON
        output_path = output_dir / (
            Path(fields["file_name"]).stem + ".json"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validated.model_dump(), f, indent=4, default=str)

        print(f"  SAVED: {output_path}")
        return True

    except ValidationError as e:
        print(f"  VALIDATION FAILED: {fields.get('file_name')}")
        for error in e.errors():
            print(f"    Field: {error['loc']} | Error: {error['msg']}")
        return False
```

## What Pydantic Catches

| Bad Data | What Pydantic Does |
|---|---|
| `amount_paid = "hello"` | Raises ValidationError — not a float |
| `amount_paid = -50.0` | Raises ValidationError — not positive |
| `file_name = ""` | Raises ValidationError — empty string |
| `amount_paid = None` | Passes — Optional field allows None |
| `amount_paid = 150.0` | Passes — valid float |

---

# 13. SKILL 9 — DEDUPLICATION WITH MD5 HASHING

## What It Is
MD5 (Message Digest 5) is a hashing algorithm that converts any data into
a fixed-length 32-character string called a hash or fingerprint.
The same data always produces the same hash. Different data produces different hashes.

## Why Deduplication Is Essential
In production pipelines, documents are resubmitted constantly:
- Users drop the same file twice by mistake
- Retry logic re-sends failed files
- Multiple users upload the same document
- Scheduled jobs re-process entire folders

Without deduplication: duplicate records fill the database, analytics are wrong,
ML training data has duplicates that bias models.

## Two Layers of Deduplication

### Layer 1: File Hash (Exact Duplicate Detection)
Same file content → same MD5 → skip

### Layer 2: Field Comparison (Renamed Duplicate Detection)
Same receipt_number + amount + date → skip even if filename is different

## How It Is Used — Full Code

```python
# scripts/deduplicate.py

import hashlib
import json
from pathlib import Path

HASHES_FILE = Path(__file__).resolve().parent.parent / "logs" / "seen_hashes.json"

def load_seen_hashes() -> dict:
    """Load previously seen file hashes from disk."""
    if HASHES_FILE.exists():
        with open(HASHES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_seen_hashes(hashes: dict):
    """Save updated hashes back to disk."""
    HASHES_FILE.parent.mkdir(exist_ok=True)
    with open(HASHES_FILE, "w") as f:
        json.dump(hashes, f, indent=2)

def hash_file(file_path: Path) -> str:
    """
    Compute MD5 hash of a file's binary content.
    Same file = same hash, regardless of filename.
    """
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:    # "rb" = read binary
        hasher.update(f.read())
    return hasher.hexdigest()           # returns 32-char hex string

def is_duplicate(file_path: Path, seen_hashes: dict) -> tuple:
    """
    Check if this file has been processed before.
    Returns (is_duplicate: bool, file_hash: str, matched_name: str)
    """
    file_hash = hash_file(file_path)

    if file_hash in seen_hashes:
        matched_name = seen_hashes[file_hash]
        print(f"  DUPLICATE: {file_path.name} matches {matched_name}")
        return True, file_hash, matched_name

    return False, file_hash, None

def register_file(file_path: Path, file_hash: str, seen_hashes: dict):
    """Register a new file hash after successful processing."""
    seen_hashes[file_hash] = file_path.name
    save_seen_hashes(seen_hashes)
```

## How MD5 Hashing Works

```
File: receipt_001.jpeg (binary content)
         ↓
hashlib.md5().hexdigest()
         ↓
"a3f8d1c2b4e5f6a7b8c9d0e1f2a3b4c5"  (32 hex characters)

Same file renamed to receipt_copy.jpeg:
         ↓
hashlib.md5().hexdigest()
         ↓
"a3f8d1c2b4e5f6a7b8c9d0e1f2a3b4c5"  (SAME hash)
→ Detected as duplicate
```

---

# 14. SKILL 10 — JSON SERIALIZATION

## What It Is
JSON (JavaScript Object Notation) is the standard data interchange format
for structured data. Python's built-in `json` module handles reading and writing.

## Why JSON as Intermediate Format
- Human-readable — easy to inspect and debug
- Language-agnostic — any system can consume it
- Standard format for REST APIs and data pipelines
- Natural output format before database insertion
- Can be consumed directly by ML training pipelines

## How It Is Used

```python
import json
from pathlib import Path

def save_to_json(fields: dict, output_dir: Path) -> Path:
    """Save extracted fields as a formatted JSON file."""

    file_stem = Path(fields["file_name"]).stem
    output_path = output_dir / f"{file_stem}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            fields,
            f,
            indent=4,        # pretty print with 4-space indent
            default=str,     # convert non-serializable types to string
            ensure_ascii=False  # allow unicode characters
        )

    return output_path
```

## Sample JSON Output

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

# 15. SKILL 11 — POSTGRESQL RELATIONAL DATABASE

## What It Is
PostgreSQL is a powerful, open-source relational database system.
Data is stored in structured tables with typed columns, relationships,
and full SQL query support.

## Why PostgreSQL
- Industry-standard database for production data systems
- Full SQL support — aggregations, joins, filters, window functions
- ACID compliant — data is always consistent
- Handles concurrent connections safely
- Free and open-source

## Why Not Just JSON Files
JSON files are good for individual records but:
- Cannot query across multiple files easily
- No aggregations (SUM, COUNT, GROUP BY)
- No relationships between documents
- No concurrent write safety
- Not scalable to millions of records

## How It Is Used — Full Code

```python
# scripts/database.py

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "pipeline_db",
    "user": "postgres",
    "password": "postgres123"
}

def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """
    Create receipts and invoices tables if they don't exist.
    Called once at pipeline startup.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Create receipts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id              SERIAL PRIMARY KEY,
            file_name       TEXT,
            vendor_name     TEXT,
            receipt_number  TEXT UNIQUE,    -- UNIQUE prevents duplicates
            date_paid       TEXT,
            amount_paid     FLOAT,
            item_description TEXT,
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    # Create invoices table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id              SERIAL PRIMARY KEY,
            file_name       TEXT,
            vendor_name     TEXT,
            invoice_number  TEXT UNIQUE,    -- UNIQUE prevents duplicates
            invoice_date    TEXT,
            due_date        TEXT,
            total_amount    FLOAT,
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("  Tables created (or already exist)")


def insert_receipt(fields: dict) -> int:
    """
    Insert a receipt record into the database.
    ON CONFLICT DO NOTHING prevents duplicate inserts.
    Returns the new record ID, or None if skipped.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO receipts
                (file_name, vendor_name, receipt_number,
                 date_paid, amount_paid, item_description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (receipt_number) DO NOTHING
            RETURNING id;
        """, (
            fields.get("file_name"),
            fields.get("vendor_name"),
            fields.get("receipt_number"),
            fields.get("date_paid"),
            fields.get("amount_paid"),
            fields.get("item_description")
        ))

        result = cur.fetchone()
        conn.commit()

        if result:
            print(f"  DB INSERT: receipt saved (id={result[0]})")
            return result[0]
        else:
            print(f"  DB SKIP: receipt_number already exists")
            return None

    finally:
        cur.close()
        conn.close()
```

## Key SQL Concepts Used

| Concept | What It Does |
|---|---|
| `SERIAL PRIMARY KEY` | Auto-incrementing unique ID per row |
| `TEXT UNIQUE` | Column value must be unique across all rows |
| `ON CONFLICT DO NOTHING` | Skip insert if unique constraint violated |
| `RETURNING id` | Return the new row's ID after insert |
| `DEFAULT NOW()` | Automatically set timestamp on insert |

## Useful Queries for Demo

```sql
-- See all receipts
SELECT * FROM receipts;

-- Total spend per vendor
SELECT vendor_name, SUM(amount_paid) AS total_spent
FROM receipts GROUP BY vendor_name;

-- Receipts over $100
SELECT vendor_name, amount_paid, date_paid
FROM receipts WHERE amount_paid > 100
ORDER BY amount_paid DESC;

-- All invoices
SELECT * FROM invoices;
```

---

# 16. SKILL 12 — CHROMADB VECTOR DATABASE

## What It Is
ChromaDB is an open-source vector database designed for AI applications.
Instead of storing data as rows and columns, it stores data as vectors —
mathematical representations of meaning — and allows searching by similarity.

## Why Vector Databases Matter for AI Systems
Traditional databases answer: "Does this record contain the word X?"
Vector databases answer: "Which records are semantically similar to X?"

This is the core technology behind:
- RAG (Retrieval Augmented Generation) systems
- Semantic document search
- Recommendation engines
- Duplicate detection by meaning (not just exact match)

## How ChromaDB Works

```
Document text: "Receipt for C# .NET Basics training course"
         ↓
Sentence transformer model converts to vector:
[0.234, -0.891, 0.445, 0.123, ..., -0.567]  (384 dimensions)
         ↓
Vector stored in ChromaDB
         ↓
Query: "software training payment"
         ↓
Query converted to vector
         ↓
ChromaDB finds vectors closest in meaning
         ↓
Returns: "C# .NET Basics" receipt, "Full Stack Testing" receipt
```

## How It Is Used — Full Code

```python
# scripts/vector_store.py

import chromadb
from pathlib import Path

# Initialize persistent ChromaDB client
# Data saved to chroma_db/ folder on disk
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Create or load collection
# Collection = like a table in a traditional database
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # cosine similarity metric
)


def store_document(fields: dict, clean_text: str):
    """
    Store a document's text and metadata in ChromaDB.
    ChromaDB auto-generates embeddings using all-MiniLM-L6-v2.
    """
    # Create a safe document ID (no spaces or special chars)
    doc_id = Path(fields["file_name"]).stem
    doc_id = doc_id.replace(" ", "_").replace("(", "").replace(")", "")

    # Metadata stored alongside the vector
    metadata = {
        "file_name": fields.get("file_name", ""),
        "vendor_name": fields.get("vendor_name", ""),
        "document_type": fields.get("document_type", ""),
        "amount": str(
            fields.get("amount_paid") or fields.get("total_amount") or ""
        )
    }

    # Upsert = insert if new, update if exists
    collection.upsert(
        ids=[doc_id],
        documents=[clean_text],  # raw text → auto-embedded
        metadatas=[metadata]
    )

    print(f"  CHROMA STORED: {doc_id}")


def semantic_search(query: str, n_results: int = 3) -> list:
    """
    Search for documents semantically similar to the query.
    Returns top n_results matches with metadata.
    """
    results = collection.query(
        query_texts=[query],    # ChromaDB embeds this automatically
        n_results=n_results
    )

    matches = []
    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        matches.append({
            "id": doc_id,
            "file_name": meta.get("file_name"),
            "vendor": meta.get("vendor_name"),
            "amount": meta.get("amount"),
            "similarity_score": round(1 - distance, 4)
        })

    return matches
```

## Semantic Search Demo Results

```
Query: "software training payment"
  Match 1: Full Stack Software Testing | AURBORBLOOM LLC | $130
  Match 2: C# & .NET Basics | AURBORBLOOM LLC | $150

Query: "invoice from sliced invoices"
  Match 1: wordpress-pdf-invoice-plugin-sample | DEMO - Sliced Invoices

Query: "full stack course receipt"
  Match 1: Full Stack Software Testing | AURBORBLOOM LLC | $130
```

The query "software training payment" finds receipts about software courses
even though those exact words don't appear together in the documents.
This is semantic understanding, not keyword matching.

---

# 17. SKILL 13 — SENTENCE TRANSFORMERS (EMBEDDINGS)

## What It Is
Sentence transformers are neural network models that convert text into
dense numerical vectors (embeddings) that capture semantic meaning.

## Model Used: all-MiniLM-L6-v2
- Lightweight model (80MB) — fast and efficient
- Produces 384-dimensional embeddings
- Excellent at semantic similarity tasks
- Default model in ChromaDB
- Downloaded automatically on first run

## Why This Model
- Small enough to run locally without GPU
- Fast inference — seconds not minutes
- Widely used in production RAG systems
- Good balance of accuracy and speed

## How Embeddings Enable Search

```
Text A: "payment for software training"
Embedding A: [0.2, -0.8, 0.4, ...]

Text B: "invoice for C# .NET course"
Embedding B: [0.19, -0.78, 0.42, ...]

Text C: "weather forecast for tomorrow"
Embedding C: [-0.5, 0.3, -0.1, ...]

Cosine similarity(A, B) = 0.94  ← very similar
Cosine similarity(A, C) = 0.12  ← very different
```

ChromaDB does this calculation automatically for every query.

---

# 18. SKILL 14 — PIPELINE ORCHESTRATION

## What It Is
Pipeline orchestration is the coordination of multiple processing steps
in the correct order, with error handling, logging, and state management.
`run_pipeline.py` is the orchestrator for this project.

## Why It Matters
Without an orchestrator:
- Each script must be run manually in the right order
- One failure breaks the rest of the process
- No visibility into overall pipeline state
- Hard to debug and maintain

With an orchestrator:
- Single command runs everything
- Per-file error isolation
- Centralized stats tracking
- Production-ready run summary

## How It Is Used — Full Code

```python
# scripts/run_pipeline.py

import logging
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from detect_files import scan_input_folder
from extract_pdf_text import extract_text_from_pdf
from ocr_extract import ocr_image_file, ocr_scanned_pdf
from clean_text import clean_text, save_clean_text
from extract_fields import extract_receipt_fields, extract_invoice_fields
from to_json import validate_and_save
from deduplicate import is_duplicate, register_file, load_seen_hashes
from database import create_tables, insert_receipt, insert_invoice
from vector_store import store_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),  # write to file
        logging.StreamHandler()                     # also print to console
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(base_dir: Path):
    """
    Master pipeline function.
    Processes all files in input_docs/ from start to finish.
    """
    logger.info("=" * 60)
    logger.info("PIPELINE STARTED")
    logger.info("=" * 60)

    # Initialize database tables
    create_tables()

    # Load deduplication registry
    seen_hashes = load_seen_hashes()

    # Scan input folder and classify files
    files = scan_input_folder(base_dir / "input_docs")
    logger.info(f"Found {len(files)} files")

    # Stats tracking
    stats = {"total": len(files), "success": 0,
             "failed": 0, "duplicate": 0, "skipped": 0}

    # Process each file
    for file_path, file_type in files:
        logger.info(f"--- Processing: {file_path.name} [{file_type}] ---")

        # STEP 1: Deduplication check
        dup, file_hash, matched = is_duplicate(file_path, seen_hashes)
        if dup:
            logger.warning(f"SKIPPED (duplicate file): {file_path.name}")
            stats["duplicate"] += 1
            continue

        try:
            # STEP 2: Text Extraction
            raw_dir = base_dir / "raw_text"
            if file_type == "text_pdf":
                raw_text = extract_text_from_pdf(file_path, raw_dir)
            else:  # image or scanned_pdf
                raw_text = ocr_image_file(file_path, raw_dir) \
                    if file_type == "image" \
                    else ocr_scanned_pdf(file_path, raw_dir)

            # STEP 3: Clean text
            clean_dir = base_dir / "clean_text"
            cleaned = clean_text(raw_text)
            save_clean_text(cleaned, file_path.stem, clean_dir)
            logger.info(f"Text cleaned: {clean_dir / (file_path.stem + '.txt')}")

            # STEP 4: Extract fields
            if file_type == "text_pdf":
                fields = extract_invoice_fields(cleaned, file_path.stem + ".txt")
            else:
                fields = extract_receipt_fields(cleaned, file_path.stem + ".txt")
            logger.info(f"Fields extracted: {list(fields.keys())}")

            # STEP 5: Validate and save JSON
            json_dir = base_dir / "json_output"
            saved = validate_and_save(fields, json_dir)
            if not saved:
                stats["failed"] += 1
                continue

            logger.info(f"SUCCESS: {file_path.name}")

            # STEP 6: Save to PostgreSQL
            if fields["document_type"] == "receipt":
                insert_receipt(fields)
            else:
                insert_invoice(fields)
            logger.info(f"DB saved: {file_path.name}")

            # STEP 7: Store in ChromaDB
            store_document(fields, cleaned)
            logger.info(f"Vector stored: {file_path.name}")

            # Register as seen
            register_file(file_path, file_hash, seen_hashes)
            stats["success"] += 1

        except Exception as e:
            logger.error(f"FAILED: {file_path.name} — {e}")
            stats["failed"] += 1

    # Pipeline summary
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Total files   : {stats['total']}")
    logger.info(f"  Successful    : {stats['success']}")
    logger.info(f"  Failed        : {stats['failed']}")
    logger.info(f"  Duplicates    : {stats['duplicate']}")
    logger.info(f"  Skipped       : {stats['skipped']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    run_pipeline(base_dir)
```

---

# 19. SKILL 15 — LOGGING AND OBSERVABILITY

## What It Is
Python's built-in `logging` module provides structured, level-based logging
to both console output and persistent log files.

## Why Logging Is Non-Negotiable in Production
Without logs:
- When a file fails, you don't know why
- You can't tell which files were processed yesterday
- No audit trail for compliance
- Debugging requires re-running the entire pipeline

With logs:
- Complete history of every pipeline run
- Exact error messages with timestamps
- Easy to filter by level (INFO, WARNING, ERROR)
- Stakeholders can review processing history

## Log Levels Used

| Level | When Used | Example |
|---|---|---|
| INFO | Normal successful events | "SUCCESS: invoice.pdf" |
| WARNING | Non-fatal issues | "SKIPPED: duplicate file" |
| ERROR | Failures that need attention | "FAILED: receipt.jpeg — OCR error" |

## Sample Log File Content

```
2026-03-26 21:12:04 [INFO] PIPELINE STARTED
2026-03-26 21:12:04 [INFO] Found 4 files
2026-03-26 21:12:04 [INFO] --- Processing: receipt_001.jpeg [image] ---
2026-03-26 21:12:07 [INFO] Text cleaned: clean_text/receipt_001.txt
2026-03-26 21:12:07 [INFO] Fields extracted: ['vendor_name', 'receipt_number', ...]
2026-03-26 21:12:07 [INFO] SUCCESS: receipt_001.jpeg
2026-03-26 21:12:07 [INFO] DB saved: receipt_001.jpeg
2026-03-26 21:12:07 [INFO] Vector stored: receipt_001.jpeg
2026-03-26 21:12:08 [WARNING] SKIPPED (duplicate file): receipt_001_copy.jpeg
2026-03-26 21:12:11 [INFO] PIPELINE COMPLETE
2026-03-26 21:12:11 [INFO]   Total: 4 | Success: 3 | Duplicate: 1 | Failed: 0
```

---

# 20. SKILL 16 — DOCKER CONTAINERIZATION

## What It Is
Docker packages an application with all its dependencies — Python, Tesseract,
Poppler, all pip packages — into a portable container that runs identically
on any machine.

## Why Docker
Without Docker:
- "Works on my machine" problem
- Every new server needs manual Tesseract + Poppler installation
- Version conflicts between environments
- Hard to deploy at scale

With Docker:
- One container, runs anywhere
- Reproducible environment every time
- Ready for cloud deployment (ECS, GKE, AKS)
- Easy to version and roll back

## Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
# Tesseract OCR and Poppler must be installed at OS level
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create required directories
RUN mkdir -p input_docs raw_text clean_text json_output logs chroma_db

# Default command: run the pipeline
CMD ["python", "scripts/run_pipeline.py"]
```

## Docker Commands

```bash
# Build the image
docker build -t document-pipeline .

# Run with input documents mounted from host
docker run \
  -v $(pwd)/input_docs:/app/input_docs \
  -v $(pwd)/json_output:/app/json_output \
  -v $(pwd)/logs:/app/logs \
  document-pipeline

# Run interactively for debugging
docker run -it document-pipeline /bin/bash
```

---

# 21. SKILL 17 — VIRTUAL ENVIRONMENT AND DEPENDENCY MANAGEMENT

## What It Is
A virtual environment (venv) is an isolated Python installation for a
specific project. It has its own packages, separate from system Python.

## Why It Matters
Without venv:
- All projects share the same Python packages
- Updating one package for Project A breaks Project B
- Impossible to have different package versions for different projects

With venv:
- Each project has its own isolated package set
- No conflicts between projects
- requirements.txt records exact versions for reproducibility

## Commands Used

```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Save current packages to requirements.txt
pip freeze > requirements.txt
```

## requirements.txt

```
pytesseract==0.3.13
pypdf==6.9.2
pdf2image==1.17.0
Pillow==12.1.1
pydantic==2.12.5
pandas==3.0.1
psycopg2-binary==2.9.11
chromadb==1.5.5
```

---

# 22. SCRIPT-BY-SCRIPT CODE WALKTHROUGH

| Script | Lines | Purpose | Key Libraries |
|---|---|---|---|
| detect_files.py | ~60 | File type classification | pypdf, pathlib |
| extract_pdf_text.py | ~45 | Text PDF extraction | pypdf |
| ocr_extract.py | ~80 | OCR for images and scanned PDFs | pytesseract, pdf2image, Pillow |
| clean_text.py | ~60 | Text normalization | re |
| extract_fields.py | ~120 | Regex field extraction | re |
| to_json.py | ~90 | Pydantic validation + JSON | pydantic, json |
| deduplicate.py | ~70 | MD5 deduplication | hashlib, json |
| database.py | ~100 | PostgreSQL operations | psycopg2 |
| vector_store.py | ~80 | ChromaDB storage + search | chromadb |
| run_pipeline.py | ~150 | Master orchestrator | logging, all above |

---

# 23. DATA FLOW — END TO END

## Single Document Journey

```
INPUT:  WhatsApp Image 2026-03-23.jpeg
        (photo of AURBORBLOOM LLC receipt for $130)

STEP 1: detect_files.py
        → extension is .jpeg → file_type = "image"

STEP 2: deduplicate.py
        → compute MD5: "a3f8...c5"
        → check seen_hashes.json → NOT FOUND → new file

STEP 3: ocr_extract.py
        → Image.open("WhatsApp Image 2026-03-23.jpeg")
        → pytesseract.image_to_string(image, lang="eng")
        → raw text saved to raw_text/WhatsApp Image 2026-03-23.txt

STEP 4: clean_text.py
        → remove junk symbols, collapse spaces, filter lines
        → clean text saved to clean_text/WhatsApp Image 2026-03-23.txt

STEP 5: extract_fields.py
        → doc_type = "receipt" (detected from text content)
        → vendor_name: "AURBORBLOOM LLC"
        → receipt_number: "1148-2760"
        → date_paid: "Feb 27, 2026"
        → amount_paid: 130.0
        → item_description: "Full Stack Software Testing"

STEP 6: to_json.py (Pydantic validation)
        → ReceiptSchema(**fields)
        → amount_paid = 130.0 ✓ (positive float)
        → PASS → save to json_output/WhatsApp Image 2026-03-23.json

STEP 7: database.py
        → INSERT INTO receipts (vendor_name, receipt_number, ...)
        → receipt_number "1148-2760" not in DB → new record
        → id = 3 assigned

STEP 8: vector_store.py
        → collection.upsert(id="WhatsApp_Image_2026-03-23",
                           document=cleaned_text)
        → ChromaDB generates embedding automatically
        → stored in chroma_db/

STEP 9: deduplicate.py
        → register hash "a3f8...c5" → saved to seen_hashes.json

STEP 10: pipeline.log
        → "2026-03-26 21:12:10 [INFO] SUCCESS: WhatsApp Image 2026-03-23.jpeg"
```

---

# 24. SAMPLE OUTPUTS

## JSON Output

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

## PostgreSQL Query Results

```sql
SELECT vendor_name, receipt_number, amount_paid, date_paid
FROM receipts ORDER BY amount_paid DESC;

RESULT:
vendor_name      | receipt_number | amount_paid | date_paid
-----------------+----------------+-------------+------------------
AURBORBLOOM LLC  | 1055-6311      | 150.0       | Mar 17, 2026
AURBORBLOOM LLC  | 1580-9520      | 150.0       | Mar 17, 2026
AURBORBLOOM LLC  | 1148-2760      | 130.0       | Feb 27, 2026
```

```sql
SELECT vendor_name, SUM(amount_paid) AS total_spent
FROM receipts GROUP BY vendor_name;

RESULT:
vendor_name      | total_spent
-----------------+------------
AURBORBLOOM LLC  | 430.00
```

## ChromaDB Semantic Search Results

```
Query: "software training payment"
  Match 1: WhatsApp Image...PM.txt | AURBORBLOOM LLC | $130 | score: 0.8921
  Match 2: WhatsApp Image...PM (1).txt | AURBORBLOOM LLC | $150 | score: 0.8654

Query: "invoice from sliced invoices"
  Match 1: wordpress-pdf-invoice-plugin-sample.txt | DEMO - Sliced Invoices | $1.0

Query: "full stack course receipt"
  Match 1: WhatsApp Image...PM.txt | AURBORBLOOM LLC | $130 | score: 0.9234
```

## Pipeline Summary Log

```
2026-03-26 21:12:04 [INFO] PIPELINE STARTED
2026-03-26 21:12:11 [INFO] PIPELINE COMPLETE
2026-03-26 21:12:11 [INFO]   Total files   : 4
2026-03-26 21:12:11 [INFO]   Successful    : 4
2026-03-26 21:12:11 [INFO]   Failed        : 0
2026-03-26 21:12:11 [INFO]   Duplicates    : 0
2026-03-26 21:12:11 [INFO]   Skipped       : 0
```

---

# 25. PROJECT DEMO GUIDE

## Pre-Demo Setup

```powershell
cd C:\Users\vishal\Desktop\document-pipeline-local
venv\Scripts\activate
del logs\seen_hashes.json
del json_output\*.json
```

## Demo Script (10 Minutes)

### Minute 0-1: Introduction
Open VS Code. Show folder structure.:
> "I built a local document processing pipeline — an ETL system that takes
> raw documents and turns them into structured, validated data stored in
> PostgreSQL and ChromaDB. Let me walk you through it end to end."

### Minute 1-2: Show Input Files
Open input_docs/ folder. :
> "These are the inputs — three WhatsApp phone photos of receipts, and one
> text-based PDF invoice. The pipeline automatically detects what each file
> is and handles it appropriately."

### Minute 2-5: Run the Pipeline Live
```powershell
python scripts/run_pipeline.py
```
Point out each section as it runs:
- "Here it detects file types"
- "Here Tesseract OCR reads the phone photos"
- "Here pypdf reads the PDF directly"
- "Here it cleans and extracts fields"
- "Here Pydantic validates each record"
- "Here it saves to PostgreSQL and ChromaDB"

### Minute 5-6 JSON Output
```powershell
cat "json_output/WhatsApp Image 2026-03-23 at 10.11.06 PM.json"
```
> "This is the structured output from a phone photo —
> vendor, receipt number, date, and amount — all automatically extracted."

### Minute 6-7:  PostgreSQL
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT vendor_name, receipt_number, amount_paid FROM receipts;"
```
Then:
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT vendor_name, SUM(amount_paid) AS total FROM receipts GROUP BY vendor_name;"
```
> "All records are in PostgreSQL. I can run SQL queries — total spend per vendor,
> date range filters, anything."

### Minute 7-9:  ChromaDB Semantic Search
```powershell
python scripts/vector_store.py
```
> "ChromaDB stores document embeddings for semantic search. I search 'software
> training payment' and it finds the correct receipts even though those exact
> words don't appear together in the documents. This is the foundation of RAG."

### Minute 9-10:  Deduplication + Logs
Run pipeline again:
```powershell
python scripts/run_pipeline.py
```
> "Second run — all 4 files detected as duplicates via MD5 hashing and skipped.
> Zero reprocessing, zero duplicate records."

```powershell
cat logs/pipeline.log
```
> "Full audit trail — every file processed, every success, every skip, timestamped."

---


---

# 26. FUTURE ROADMAP

| Enhancement | Benefit | Technology |
|---|---|---|
| Airflow scheduling | Automated periodic runs, retry logic | Apache Airflow |
| S3 input source | Cloud document ingestion | AWS S3 + boto3 |
| FastAPI endpoint | REST API for programmatic submission | FastAPI + uvicorn |
| LLM fallback extraction | Handle edge cases and complex layouts | OpenAI / Claude API |
| Spark processing | Parallel processing at scale | Apache Spark |
| pgvector | PostgreSQL-native vector search | pgvector extension |
| Delta Lake integration | Data versioning and lineage | Delta Lake |
| Kubernetes deployment | Production-grade orchestration | Kubernetes + Helm |
| Monitoring dashboard | Real-time pipeline metrics | Grafana + Prometheus |
| Multi-language OCR | Handle non-English documents | Tesseract lang packs |

---

# QUICK REFERENCE COMMANDS

```powershell
# Activate environment
venv\Scripts\activate

# Run full pipeline
python scripts/run_pipeline.py

# Test ChromaDB semantic search
python scripts/vector_store.py

# Query PostgreSQL — all receipts
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT * FROM receipts;"

# Query PostgreSQL — total per vendor
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d pipeline_db -c "SELECT vendor_name, SUM(amount_paid) FROM receipts GROUP BY vendor_name;"

# View logs
cat logs/pipeline.log

# Reset and run fresh
del logs\seen_hashes.json
del json_output\*.json
python scripts/run_pipeline.py
```

---

**Vishal S**
AI Data & Platform Engineer
vishalaiml97@gmail.com

*Built with: Python | Tesseract OCR | pypdf | pdf2image | Pydantic |
PostgreSQL | ChromaDB | Sentence Transformers | Docker*