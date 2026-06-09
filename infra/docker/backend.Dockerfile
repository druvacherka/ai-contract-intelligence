# ============================================
# AI Contract Intelligence — Backend Dockerfile
# ============================================
FROM python:3.11-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY data-ocr-module/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY data-ocr-module/ .

# Create required directories
RUN mkdir -p uploads logs datasets/raw datasets/processed datasets/exports datasets/schemas

# Expose FastAPI port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
