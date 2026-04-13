import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ── Connection Config ─────────────────────────────────────────────────────────

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pipeline_db",
    "user": "postgres",
    "password": "postgres123"
}


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


# ── Create Tables ─────────────────────────────────────────────────────────────

def create_tables():
    """Create receipts and invoices tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id              SERIAL PRIMARY KEY,
            file_name       TEXT NOT NULL,
            vendor_name     TEXT,
            receipt_number  TEXT UNIQUE,
            date_paid       TEXT,
            amount_paid     FLOAT,
            item_description TEXT,
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id              SERIAL PRIMARY KEY,
            file_name       TEXT NOT NULL,
            vendor_name     TEXT,
            invoice_number  TEXT UNIQUE,
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


# ── Insert Records ────────────────────────────────────────────────────────────

def insert_receipt(data: dict) -> bool:
    """Insert a receipt record. Returns True on success, False if duplicate."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO receipts (file_name, vendor_name, receipt_number, date_paid, amount_paid, item_description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (receipt_number) DO NOTHING
            RETURNING id;
        """, (
            data.get("file_name"),
            data.get("vendor_name"),
            data.get("receipt_number"),
            data.get("date_paid"),
            data.get("amount_paid"),
            data.get("item_description")
        ))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result:
            print(f"  DB INSERT: receipt saved (id={result[0]})")
            return True
        else:
            print(f"  DB SKIP: receipt_number already exists")
            return False
    except Exception as e:
        print(f"  DB ERROR (receipt): {e}")
        return False


def insert_invoice(data: dict) -> bool:
    """Insert an invoice record. Returns True on success, False if duplicate."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO invoices (file_name, vendor_name, invoice_number, invoice_date, due_date, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (invoice_number) DO NOTHING
            RETURNING id;
        """, (
            data.get("file_name"),
            data.get("vendor_name"),
            data.get("invoice_number"),
            data.get("invoice_date"),
            data.get("due_date"),
            data.get("total_amount")
        ))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result:
            print(f"  DB INSERT: invoice saved (id={result[0]})")
            return True
        else:
            print(f"  DB SKIP: invoice_number already exists")
            return False
    except Exception as e:
        print(f"  DB ERROR (invoice): {e}")
        return False


def save_to_database(data: dict) -> bool:
    """Route to correct insert function based on document type."""
    doc_type = data.get("document_type")
    if doc_type == "receipt":
        return insert_receipt(data)
    elif doc_type == "invoice":
        return insert_invoice(data)
    else:
        print(f"  DB SKIP: unknown document type '{doc_type}'")
        return False


# ── Query Records ─────────────────────────────────────────────────────────────

def fetch_all_receipts():
    """Fetch and print all receipts from the database."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM receipts ORDER BY created_at DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_all_invoices():
    """Fetch and print all invoices from the database."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM invoices ORDER BY created_at DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_folder = os.path.join(base_dir, "json_output")

    print("\nConnecting to PostgreSQL...\n")
    create_tables()

    print(f"\nLoading JSON files from: {json_folder}\n")

    for file_name in os.listdir(json_folder):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(json_folder, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"--- {file_name} ---")
        save_to_database(data)

    print("\n--- Receipts in DB ---")
    for row in fetch_all_receipts():
        print(dict(row))

    print("\n--- Invoices in DB ---")
    for row in fetch_all_invoices():
        print(dict(row))
