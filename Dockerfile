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

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create required folders
RUN mkdir -p input_docs raw_text clean_text json_output logs chroma_db

# Default command: run the pipeline
CMD ["python", "scripts/run_pipeline.py"]
